# tone_emotion_detector.py
"""
Tone Emotion Detector

Responsibilities:
- Detect sentiment (positive, negative, neutral) and coarse emotions
- Identify tones such as sarcasm, uncertainty, optimism, frustration
- Provide confidence scoring and rationale
- Support extensibility for new cues
- Ensure compatibility with EmotionResult schema
"""

from typing import Optional, Dict, Any, List
from schema import EmotionResult
from utils import normalize_text


class ToneEmotionDetector:
    """
    Lightweight rule-based detector for sentiment and coarse emotions.
    Replace with an ML model by overriding detect() while preserving EmotionResult schema.

    Features:
    - Keyword-based detection for sentiment and emotions
    - Confidence scoring based on cue frequency
    - Tone detection (sarcasm, uncertainty, optimism, frustration)
    - Extensible cue sets
    - Transparent rationale
    """

    # -----------------------------
    # Cue Definitions
    # -----------------------------
    POSITIVE = {
        "great", "good", "awesome", "love", "happy", "excited", "glad", "relieved",
        "fantastic", "wonderful", "amazing", "excellent", "positive"
    }
    NEGATIVE = {
        "bad", "terrible", "hate", "sad", "angry", "upset", "annoyed", "frustrated",
        "confused", "overwhelmed", "awful", "horrible", "negative"
    }
    SARCASTIC = {
        "yeah right", "sure", "as if", "totally", "great...", "obviously", "of course"
    }
    UNCERTAINTY = {
        "maybe", "not sure", "idk", "i don't know", "perhaps", "unsure", "uncertain"
    }
    NEUTRAL = {
        "okay", "fine", "alright", "normal", "average"
    }

    def __init__(self, thresholds: Optional[dict] = None):
        self.thresholds = thresholds or {}

    # -----------------------------
    # Core Detection
    # -----------------------------
    def detect(self, text: str) -> EmotionResult:
        """
        Detect sentiment, primary emotion, tone, and confidence from text.
        """
        if not text or not text.strip():
            return EmotionResult(
                sentiment="neutral",
                primary_emotion=None,
                tone=[],
                confidence=0.0,
                rationale="Empty input"
            )

        t = normalize_text(text)

        # Score cues
        score_pos = sum(1 for w in self.POSITIVE if w in t)
        score_neg = sum(1 for w in self.NEGATIVE if w in t)
        score_sar = sum(1 for w in self.SARCASTIC if w in t)
        score_unc = sum(1 for w in self.UNCERTAINTY if w in t)

        sentiment = "neutral"
        confidence = 0.5
        tone: List[str] = []

        # Sentiment detection
        if score_pos > score_neg and score_pos > 0:
            sentiment = "positive"
            confidence = 0.6 + min(0.3, 0.05 * score_pos)
            tone.append("optimistic")
        elif score_neg > score_pos and score_neg > 0:
            sentiment = "negative"
            confidence = 0.6 + min(0.3, 0.05 * score_neg)
            tone.append("frustrated")

        # Sarcasm
        if score_sar > 0:
            tone.append("sarcastic")
            confidence = max(confidence, 0.65)

        # Uncertainty
        if score_unc > 0:
            tone.append("uncertain")
            confidence = max(confidence, 0.55)

        # Primary emotion detection
        primary_emotion = None
        if "angry" in t or "annoyed" in t or "frustrated" in t:
            primary_emotion = "anger"
        elif "sad" in t or "upset" in t or "depressed" in t:
            primary_emotion = "sadness"
        elif "excited" in t or "glad" in t or "happy" in t or "joy" in t:
            primary_emotion = "joy"
        elif "confused" in t or "overwhelmed" in t or "uncertain" in t:
            primary_emotion = "confusion"
        elif "relieved" in t:
            primary_emotion = "relief"

        return EmotionResult(
            sentiment=sentiment,
            primary_emotion=primary_emotion,
            tone=list(set(tone)),  # ensure uniqueness
            confidence=round(confidence, 2),
            rationale="Rule-based keyword detection"
        )

    # -----------------------------
    # Utilities
    # -----------------------------
    def explain(self, text: str) -> Dict[str, Any]:
        """
        Provide detailed explanation of detection.
        """
        result = self.detect(text)
        return {
            "text": text,
            "sentiment": result.sentiment,
            "primary_emotion": result.primary_emotion,
            "tone": result.tone,
            "confidence": result.confidence,
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
        return ["POSITIVE", "NEGATIVE", "SARCASTIC", "UNCERTAINTY", "NEUTRAL"]
