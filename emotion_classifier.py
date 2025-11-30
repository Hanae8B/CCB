# emotion_classifier.py
from typing import Dict
import re

class EmotionClassifier:
    """
    Enhanced lexicon-based emotion classifier.
    Returns one of: 'neutral', 'joy', 'sadness', 'anger', 'fear', 'surprise', 'tired'.

    Improvements:
    - Detects excitement/joy from words and exclamation marks
    - Detects tired/exhausted/fatigued
    - Maintains deterministic lexicon scoring
    """

    LEXICON: Dict[str, Dict[str, int]] = {
        "joy": {
            "happy": 2, "joy": 2, "glad": 1, "love": 1, "great": 1,
            "awesome": 2, "excited": 2, "amazing": 2, "wonderful": 2, "wow": 1,
        },
        "sadness": {
            "sad": 2, "down": 1, "depressed": 2, "unhappy": 2,
            "cry": 2, "tears": 2, "lonely": 1, "hopeless": 2,
        },
        "anger": {
            "angry": 2, "mad": 2, "furious": 2, "rage": 2,
            "annoyed": 1, "irritated": 1,
        },
        "fear": {
            "afraid": 2, "scared": 2, "fear": 2, "anxious": 2,
            "nervous": 1, "terrified": 2,
        },
        "surprise": {
            "surprised": 2, "shocked": 2, "wow": 1, "unexpected": 1, "astonished": 2,
        },
        "tired": {
            "tired": 2, "exhausted": 2, "drained": 2, "fatigued": 2, "sleepy": 1,
        },
    }

    def classify(self, text: str) -> str:
        if not text or not text.strip():
            return "neutral"

        txt = text.lower()
        scores = {k: 0 for k in self.LEXICON.keys()}

        # Lexicon-based scoring
        for emotion, words in self.LEXICON.items():
            for w, weight in words.items():
                if re.search(rf"\b{re.escape(w)}\b", txt):
                    scores[emotion] += weight

        # Exclamation marks boost joy/emotion
        exclamations = len(re.findall(r'!+', txt))
        if exclamations > 0:
            scores["joy"] += exclamations  # each '!' adds 1 to joy

        # Determine top emotion
        priority = ["joy", "sadness", "anger", "fear", "surprise", "tired", "neutral"]
        max_score = max(scores.values())
        if max_score == 0:
            return "neutral"

        top_emotions = [e for e, s in scores.items() if s == max_score]
        for p in priority:
            if p in top_emotions:
                return p

        return "neutral"
