# subtext_inferencer.py
"""
Subtext Inferencer

Responsibilities:
- Detect implied goals, emotional cues, or emphasis beyond surface intent
- Use heuristic keyword patterns, emotion cues, and intent signals
- Provide confidence scoring and rationale
- Support extensibility for new cues and rules
"""

from typing import Optional, List, Dict, Any
from schema import SubtextResult
from utils import normalize_text


class SubtextInferencer:
    """
    Detects implied goals, emotional cues, or emphasis beyond surface intent.
    Heuristics can later be replaced or augmented with embeddings/LLM reasoning.

    Features:
    - Keyword-based detection for common subtext categories
    - Emotion and intent integration
    - Confidence scoring
    - Rationale explanation
    - Extensible cue sets
    """

    # -----------------------------
    # Cue Definitions
    # -----------------------------
    HELP_SEEKING = {
        "help", "need advice", "what should i do", "can you guide", "how do i", "assist me"
    }
    VALIDATION_SEEKING = {
        "does that make sense", "am i right", "is this correct", "do you think", "validate"
    }
    EMPATHY_SEEKING = {
        "i'm tired", "i am tired", "burned out", "overwhelmed", "stressed", "exhausted",
        "drained", "fatigued"
    }
    CLARIFICATION = {
        "i don't understand", "i'm confused", "not clear", "clarify", "explain again", "unclear"
    }
    GRATITUDE = {
        "thanks", "thank you", "much appreciated", "grateful"
    }
    APOLOGETIC = {
        "sorry", "my apologies", "forgive me"
    }
    TOPIC_SHIFT = {
        "by the way", "btw", "speaking of", "changing topic"
    }
    EMPHASIS = {
        "!", "literally", "absolutely", "completely", "totally"
    }

    def __init__(self, thresholds: Optional[dict] = None):
        self.thresholds = thresholds or {}

    # -----------------------------
    # Core Inference
    # -----------------------------
    def infer(
        self,
        text: str,
        emotion: Optional[str] = None,
        intent: Optional[str] = None
    ) -> SubtextResult:
        """
        Returns a SubtextResult based on:
        - Heuristic keyword patterns
        - Emotion cues (e.g., tired → seeking empathy)
        - Exclamation marks → emphasis
        - Emotional_state or exclamation intents
        """
        if not text or not text.strip():
            return SubtextResult(
                primary=None,
                signals=[],
                confidence=0.0,
                rationale="Empty input"
            )

        t = normalize_text(text)
        signals: List[str] = []

        # Heuristic keyword detection
        if any(k in t for k in self.HELP_SEEKING):
            signals.append("seeking_help")
        if any(k in t for k in self.VALIDATION_SEEKING):
            signals.append("seeking_validation")
        if any(k in t for k in self.EMPATHY_SEEKING):
            signals.append("seeking_empathy")
        if any(k in t for k in self.CLARIFICATION):
            signals.append("seeking_clarification")
        if any(k in t for k in self.APOLOGETIC):
            signals.append("apologetic")
        if any(k in t for k in self.GRATITUDE):
            signals.append("gratitude")
        if any(k in t for k in self.TOPIC_SHIFT):
            signals.append("topic_shift")

        # Emotion-based signals
        if emotion == "tired" or "exhausted" in t:
            signals.append("seeking_empathy")
        if emotion == "joy" and "!" in text:
            signals.append("expressing_excitement")
        if emotion == "sadness":
            signals.append("seeking_support")

        # Intent-based signals
        if intent == "exclamation":
            signals.append("emphasis")
        if intent == "emotional_expression" and emotion in ("sadness", "anger"):
            signals.append("venting")

        # Exclamation mark detection
        if "!" in text and "expressing_excitement" not in signals:
            signals.append("emphasis")

        # Deduplicate signals
        signals = list(set(signals))

        # Determine primary signal
        primary = signals[0] if signals else None
        confidence = 0.7 if signals else 0.4

        return SubtextResult(
            primary=primary,
            secondary=signals,
            rationale="Heuristic pattern detection with emotion/intent cues",
        )

    # -----------------------------
    # Utilities
    # -----------------------------
    def explain(self, text: str, emotion: Optional[str] = None, intent: Optional[str] = None) -> Dict[str, Any]:
        """
        Provide detailed explanation of subtext inference.
        """
        result = self.infer(text, emotion, intent)
        return {
            "text": text,
            "emotion": emotion,
            "intent": intent,
            "primary": result.primary,
            "signals": result.secondary,
            "rationale": result.rationale,
        }

    def add_cues(self, category: str, cues: List[str]) -> None:
        """
        Dynamically add new cues to a category.
        """
        attr = category.upper()
        if hasattr(self, attr):
            getattr(self, attr).update(cues)
        else:
            print(f"Unknown cue category: {category}")

    def list_categories(self) -> List[str]:
        """
        List all available cue categories.
        """
        return [
            "HELP_SEEKING", "VALIDATION_SEEKING", "EMPATHY_SEEKING",
            "CLARIFICATION", "GRATITUDE", "APOLOGETIC", "TOPIC_SHIFT", "EMPHASIS"
        ]
