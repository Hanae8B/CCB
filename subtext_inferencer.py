# subtext_inferencer.py
from typing import Optional
from schema import SubtextResult
from utils import normalize_text


class SubtextInferencer:
    """
    Detects implied goals, emotional cues, or emphasis beyond surface intent.
    Heuristics can later be replaced or augmented with embeddings/LLM reasoning.
    """

    HELP_SEEKING = {"help", "need advice", "what should i do", "can you guide", "how do i"}
    VALIDATION_SEEKING = {"does that make sense", "am i right", "is this correct", "do you think"}
    EMPATHY_SEEKING = {"i'm tired", "i am tired", "burned out", "overwhelmed", "stressed", "exhausted"}
    CLARIFICATION = {"i don't understand", "i'm confused", "not clear", "clarify", "explain again"}
    GRATITUDE = {"thanks", "thank you"}
    APOLOGETIC = {"sorry", "my apologies"}
    TOPIC_SHIFT = {"by the way", "btw"}

    def __init__(self, thresholds: Optional[dict] = None):
        self.thresholds = thresholds or {}

    def infer(self, text: str, emotion: Optional[str] = None, intent: Optional[str] = None) -> SubtextResult:
        """
        Returns a SubtextResult based on:
        - Heuristic keyword patterns
        - Emotion cues (e.g., tired → seeking empathy)
        - Exclamation marks → emphasis
        - Emotional_state or exclamation intents
        """
        t = normalize_text(text)
        signals = []

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

        # Intent-based signals
        if intent == "exclamation":
            signals.append("emphasis")

        # Exclamation mark detection
        if "!" in text and "expressing_excitement" not in signals:
            signals.append("emphasis")

        # Determine primary signal
        primary = signals[0] if signals else None
        confidence = 0.7 if signals else 0.4

        return SubtextResult(
            primary=primary,
            signals=signals,
            confidence=confidence,
            rationale="Heuristic pattern detection with emotion/intent cues"
        )
