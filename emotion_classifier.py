# emotion_classifier.py
from typing import Dict
import re


class EmotionClassifier:
    """
    Bare-minimum emotion classifier based on lexicon cues.
    Returns one of: 'neutral', 'joy', 'sadness', 'anger', 'fear', 'surprise'.
    """

    LEXICON: Dict[str, Dict[str, int]] = {
        "joy": {
            "happy": 2, "joy": 2, "glad": 1, "love": 1, "great": 1, "awesome": 2, "excited": 2,
        },
        "sadness": {
            "sad": 2, "down": 1, "depressed": 2, "unhappy": 2, "cry": 2, "tears": 2,
        },
        "anger": {
            "angry": 2, "mad": 2, "furious": 2, "rage": 2, "annoyed": 1, "irritated": 1,
        },
        "fear": {
            "afraid": 2, "scared": 2, "fear": 2, "anxious": 2, "nervous": 1, "terrified": 2,
        },
        "surprise": {
            "surprised": 2, "shocked": 2, "wow": 1, "unexpected": 1, "astonished": 2,
        },
    }

    def classify(self, text: str) -> str:
        if not text or not text.strip():
            return "neutral"

        txt = text.lower()
        scores = {k: 0 for k in self.LEXICON.keys()}

        for emotion, words in self.LEXICON.items():
            for w, weight in words.items():
                # basic word boundary matching
                if re.search(rf"\b{re.escape(w)}\b", txt):
                    scores[emotion] += weight

        # tie-breaking priority: joy, sadness, anger, fear, surprise, neutral
        best_emotion = max(scores.items(), key=lambda kv: kv[1])
        return best_emotion[0] if best_emotion[1] > 0 else "neutral"
