# model_interface.py
"""
Model Interface

Responsibilities:
- Tie together intent, emotion, subtext, state, and summarizer modules
- Provide a single 'infer' entrypoint for unified inference
- Support pipeline configuration (summarization, max turns, etc.)
- Handle errors gracefully
- Expose utilities for reset, inspection, and transparency
"""

from typing import Optional, Dict, Any, List
from dataclasses import dataclass
from intent_classifier import IntentClassifier
from emotion_classifier import EmotionClassifier
from subtext_detector import SubtextDetector
from state_manager import StateManager, Turn
from summarizer import Summarizer, SummaryConfig
from schema import InferenceInput, InferenceOutput


# -----------------------------
# Pipeline configuration
# -----------------------------
@dataclass
class PipelineConfig:
    summarize: bool = True
    summary_max_turns: int = 12
    allow_multi_intent: bool = True
    allow_multi_emotion: bool = True
    include_raw_scores: bool = True


# -----------------------------
# Model Interface
# -----------------------------
class ModelInterface:
    """
    Strong, stable glue module that ties together classifiers, subtext, state, and summarizer.
    Provides a single 'infer' entrypoint.

    Features:
    - Unified inference pipeline
    - Configurable summarization and scoring
    - Multi-intent and multi-emotion support
    - Error handling and transparency
    """

    def __init__(self, pipeline_config: Optional[PipelineConfig] = None):
        self.intent = IntentClassifier()
        self.emotion = EmotionClassifier()
        self.subtext = SubtextDetector()
        self.state = StateManager()

        cfg = pipeline_config or PipelineConfig()
        self.summarizer = Summarizer(SummaryConfig(max_turns=cfg.summary_max_turns))
        self._cfg = cfg

    # -----------------------------
    # Core Inference
    # -----------------------------
    def infer(self, inp: InferenceInput) -> InferenceOutput:
        """
        Run unified inference pipeline on input text.
        """
        text = inp.text or ""

        try:
            # Intent classification
            if self._cfg.allow_multi_intent:
                intents = self.intent.classify_all(text)
                intent = intents[0] if intents else "unknown"
            else:
                intent = self.intent.classify(text)
                intents = [intent]

            # Emotion classification
            if self._cfg.allow_multi_emotion:
                emotions = self.emotion.classify_all(text)
                emotion = emotions[0][0] if emotions else "neutral"
            else:
                emotion = self.emotion.classify(text)
                emotions = [(emotion, 1.0)]

            # Subtext detection
            tags = self.subtext.detect(text)

            # Update state
            turn = Turn(user_text=text, intent=intent, emotion=emotion, subtext_tags=tags)
            self.state.append_turn(turn)

            # Summarization
            summary = None
            if self._cfg.summarize:
                summary = self.summarizer.summarize(self.state.get_state().turns)

            # Build raw metadata
            raw: Dict[str, Any] = {
                "text_length": len(text),
                "intents": intents,
                "emotions": emotions,
                "subtext_tags": tags,
                "turn_count": len(self.state.get_state().turns),
            }

            return InferenceOutput(
                intent=intent,
                emotion=emotion,
                subtext_tags=tags,
                summary=summary,
                raw=raw,
            )

        except Exception as e:
            # Graceful fallback
            return InferenceOutput(
                intent="unknown",
                emotion="neutral",
                subtext_tags=[],
                summary="Error during inference pipeline.",
                raw={"error": str(e)},
            )

    # -----------------------------
    # Utilities
    # -----------------------------
    def reset(self) -> None:
        """
        Reset state manager and summarizer.
        """
        self.state.reset()
        self.summarizer.reset()

    def get_state(self) -> Dict[str, Any]:
        """
        Return current state snapshot.
        """
        return {
            "turns": self.state.get_state().turns,
            "current_state": self.state.get_state().current_state,
        }

    def explain(self, text: str) -> Dict[str, Any]:
        """
        Provide detailed explanation of classification for transparency.
        """
        intent_expl = self.intent.explain(text)
        emotion_expl = self.emotion.explain(text)
        subtext_tags = self.subtext.detect(text)

        return {
            "text": text,
            "intent_explanation": intent_expl,
            "emotion_explanation": emotion_expl,
            "subtext_tags": subtext_tags,
        }
