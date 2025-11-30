# subtext_inferencer.py
from typing import Optional
from schema import SubtextResult
from utils import normalize_text


class SubtextInferencer:
    """
    Detects implied goals or relational signals beyond surface intent.
    Heuristics can be replaced by embeddings/LLM reasoning later.
    """

    HELP_SEEKING = {"help", "need advice", "what should i do", "can you guide", "how do i"}
    VALIDATION_SEEKING = {"does that make sense", "am i right", "is this correct", "do you think"}
    EMPATHY_SEEKING = {"i'm tired", "i am tired", "burned out", "overwhelmed", "stressed", "exhausted"}
    CLARIFICATION = {"i don't understand", "i'm confused", "not clear", "clarify", "explain again"}

    def __init__(self, thresholds: Optional[dict] = None):
        self.thresholds = thresholds or {}

    def infer(self, text: str) -> SubtextResult:
        t = normalize_text(text)
        signals = []

        if any(k in t for k in self.HELP_SEEKING):
            signals.append("seeking_help")
        if any(k in t for k in self.VALIDATION_SEEKING):
            signals.append("seeking_validation")
        if any(k in t for k in self.EMPATHY_SEEKING):
            signals.append("seeking_empathy")
        if any(k in t for k in self.CLARIFICATION):
            signals.append("seeking_clarification")
        if "sorry" in t:
            signals.append("apologetic")
        if "thanks" in t or "thank you" in t:
            signals.append("gratitude")
        if "by the way" in t:
            signals.append("topic_shift")

        primary = signals[0] if signals else None
        confidence = 0.6 if signals else 0.4

        return SubtextResult(
            primary=primary,
            signals=signals,
            confidence=confidence,
            rationale="Heuristic pattern detection"
        )
