# tone_emotion_detector.py
from typing import Optional
from schema import EmotionResult
from utils import normalize_text


class ToneEmotionDetector:
    """
    Lightweight rule-based detector for sentiment and coarse emotions.
    Replace with an ML model by overriding detect() while preserving EmotionResult schema.
    """

    POSITIVE = {"great", "good", "awesome", "love", "happy", "excited", "glad", "relieved"}
    NEGATIVE = {"bad", "terrible", "hate", "sad", "angry", "upset", "annoyed", "frustrated", "confused", "overwhelmed"}
    SARCASTIC = {"yeah right", "sure", "as if", "totally", "great..."}
    UNCERTAINTY = {"maybe", "not sure", "idk", "i don't know", "perhaps"}

    def __init__(self, thresholds: Optional[dict] = None):
        self.thresholds = thresholds or {}

    def detect(self, text: str) -> EmotionResult:
        t = normalize_text(text)
        score_pos = sum(1 for w in self.POSITIVE if w in t)
        score_neg = sum(1 for w in self.NEGATIVE if w in t)
        score_sar = sum(1 for w in self.SARCASTIC if w in t)
        score_unc = sum(1 for w in self.UNCERTAINTY if w in t)

        sentiment = "neutral"
        confidence = 0.5
        tone = []

        if score_pos > score_neg and score_pos > 0:
            sentiment = "positive"
            confidence = 0.6 + min(0.3, 0.05 * score_pos)
            tone.append("optimistic")
        elif score_neg > score_pos and score_neg > 0:
            sentiment = "negative"
            confidence = 0.6 + min(0.3, 0.05 * score_neg)
            tone.append("frustrated")

        if score_sar > 0:
            tone.append("sarcastic")
            confidence = max(confidence, 0.65)

        if score_unc > 0:
            tone.append("uncertain")
            confidence = max(confidence, 0.55)

        primary_emotion = None
        if "angry" in t or "annoyed" in t:
            primary_emotion = "anger"
        elif "sad" in t or "upset" in t:
            primary_emotion = "sadness"
        elif "excited" in t or "glad" in t or "happy" in t:
            primary_emotion = "joy"
        elif "confused" in t or "overwhelmed" in t:
            primary_emotion = "confusion"

        return EmotionResult(
            sentiment=sentiment,
            primary_emotion=primary_emotion,
            tone=tone,
            confidence=confidence,
            rationale="Rule-based keyword detection"
        )
