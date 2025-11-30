"""
Emotion Classifier

Responsibilities:
- Classify text into one of: 'neutral', 'joy', 'sadness', 'anger', 'fear', 'surprise', 'tired'
- Lexicon-based deterministic scoring
- Support confidence scoring and multi-emotion detection
- Handle punctuation cues (e.g., exclamation marks, question marks)
- Provide utilities for inspection and debugging
"""

from typing import Dict, Any, List, Tuple
import re


class EmotionClassifier:
    LEXICON: Dict[str, Dict[str, int]] = {
        "joy": {
            "happy": 2, "joy": 2, "glad": 1, "love": 1, "great": 1,
            "awesome": 2, "excited": 2, "amazing": 2, "wonderful": 2, "wow": 1,
            "fantastic": 2, "delighted": 2, "pleased": 1,
        },
        "sadness": {
            "sad": 2, "down": 1, "depressed": 2, "unhappy": 2,
            "cry": 2, "tears": 2, "lonely": 1, "hopeless": 2,
            "miserable": 2, "heartbroken": 2, "blue": 1,
        },
        "anger": {
            "angry": 2, "mad": 2, "furious": 2, "rage": 2,
            "annoyed": 1, "irritated": 1, "resentful": 2, "hostile": 2,
        },
        "fear": {
            "afraid": 2, "scared": 2, "fear": 2, "anxious": 2,
            "nervous": 1, "terrified": 2, "worried": 1, "panic": 2,
        },
        "surprise": {
            "surprised": 2, "shocked": 2, "unexpected": 1,
            "astonished": 2, "amazed": 2, "startled": 2,
        },
        "tired": {
            "tired": 2, "exhausted": 2, "drained": 2, "fatigued": 2,
            "sleepy": 1, "weary": 2, "burnt out": 2,
        },
    }

    PRIORITY_ORDER: List[str] = [
        "joy", "sadness", "anger", "fear", "surprise", "tired", "neutral"
    ]

    def classify(self, text: str) -> str:
        if not text or not text.strip():
            return "neutral"

        scores = self._score_text(text)
        max_score = max(scores.values())
        if max_score == 0:
            return "neutral"

        top_emotions = [e for e, s in scores.items() if s == max_score]
        for p in self.PRIORITY_ORDER:
            if p in top_emotions:
                return p
        return "neutral"

    def classify_with_confidence(self, text: str) -> Tuple[str, float]:
        if not text or not text.strip():
            return "neutral", 0.0

        scores = self._score_text(text)
        max_score = max(scores.values())
        if max_score == 0:
            return "neutral", 0.0

        emotion = self.classify(text)
        total = sum(scores.values())
        confidence = max_score / total if total > 0 else 0.0
        return emotion, round(confidence, 3)

    def classify_all(self, text: str, threshold: float = 0.2) -> List[Tuple[str, float]]:
        if not text or not text.strip():
            return [("neutral", 0.0)]

        scores = self._score_text(text)
        total = sum(scores.values())
        if total == 0:
            return [("neutral", 0.0)]

        results: List[Tuple[str, float]] = []
        for emotion, score in scores.items():
            conf = score / total
            if conf >= threshold:
                results.append((emotion, round(conf, 3)))

        results.sort(key=lambda x: x[1], reverse=True)
        return results

    def _score_text(self, text: str) -> Dict[str, int]:
        txt = text.lower()
        scores = {k: 0 for k in self.LEXICON.keys()}

        # Lexicon-based scoring
        for emotion, words in self.LEXICON.items():
            for w, weight in words.items():
                if re.search(rf"\b{re.escape(w)}\b", txt):
                    scores[emotion] += weight

        # Exclamation marks boost joy
        exclamations = len(re.findall(r"!+", txt))
        if exclamations > 0:
            scores["joy"] += exclamations

        # Question marks: only boost surprise if combined with surprise words
        questions = len(re.findall(r"\?+", txt))
        if questions > 0:
            if any(word in txt for word in ["really", "seriously", "what", "unexpected"]):
                scores["surprise"] += questions
            else:
                # treat as neutral inquiry
                scores["neutral"] = scores.get("neutral", 0) + questions

        return scores

    def explain(self, text: str) -> Dict[str, Any]:
        scores = self._score_text(text)
        dominant, confidence = self.classify_with_confidence(text)
        breakdown = self.classify_all(text, threshold=0.0)
        return {
            "text": text,
            "scores": scores,
            "dominant": dominant,
            "confidence": confidence,
            "breakdown": breakdown,
        }
