# model_interface.py
from typing import Optional
from dataclasses import dataclass
from intent_classifier import IntentClassifier
from emotion_classifier import EmotionClassifier
from subtext_detector import SubtextDetector
from state_manager import StateManager, Turn
from summarizer import Summarizer, SummaryConfig
from schema import InferenceInput, InferenceOutput


@dataclass
class PipelineConfig:
    summarize: bool = True
    summary_max_turns: int = 12


class ModelInterface:
    """
    Strong, stable glue module that ties together classifiers, subtext, state, and summarizer.
    Provides a single 'infer' entrypoint.
    """

    def __init__(self, pipeline_config: Optional[PipelineConfig] = None):
        self.intent = IntentClassifier()
        self.emotion = EmotionClassifier()
        self.subtext = SubtextDetector()
        self.state = StateManager()
        cfg = pipeline_config or PipelineConfig()
        self.summarizer = Summarizer(SummaryConfig(max_turns=cfg.summary_max_turns))
        self._cfg = cfg

    def infer(self, inp: InferenceInput) -> InferenceOutput:
        text = inp.text or ""
        intent = self.intent.classify(text)
        emotion = self.emotion.classify(text)
        tags = self.subtext.detect(text)

        # Update state
        turn = Turn(user_text=text, intent=intent, emotion=emotion, subtext_tags=tags)
        self.state.append_turn(turn)

        summary = None
        if self._cfg.summarize:
            summary = self.summarizer.summarize(self.state.get_state().turns)

        return InferenceOutput(
            intent=intent,
            emotion=emotion,
            subtext_tags=tags,
            summary=summary,
            raw={"text_length": len(text)},
        )

    def reset(self) -> None:
        self.state.reset()
