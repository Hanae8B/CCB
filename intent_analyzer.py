# intent_analyzer.py
"""
Intent Analyzer

Responsibilities:
- Classify user input into coarse intent categories
- Provide confidence scores and rationale
- Support multi-intent detection
- Handle edge cases gracefully
"""

from typing import Optional, List, Dict, Tuple
from schema import IntentResult
from utils import normalize_text


class IntentAnalyzer:
    """
    Classifies user input into a coarse intent category:
    - greeting
    - question
    - instruction
    - emotional_expression
    - chit_chat
    - narrative
    - math
    - code
    - correction
    - closing
    - unknown

    Features:
    - Deterministic keyword/marker matching
    - Confidence scoring
    - Multi-intent detection
    - Rationale explanation
    """

    GREETING_KEYWORDS = {
        "hi", "hello", "hey", "good morning", "good evening", "good afternoon",
        "greetings", "yo", "hiya"
    }
    CLOSING_KEYWORDS = {
        "bye", "goodbye", "see you", "thanks", "thank you", "cheers",
        "farewell", "later", "take care"
    }
    QUESTION_MARKERS = {
        "?", "what", "why", "how", "when", "where", "who", "which", "do you", "can you"
    }
    INSTRUCTION_MARKERS = {
        "please", "can you", "could you", "help me", "show me", "explain",
        "walk me through", "build", "create", "generate", "write", "draft"
    }
    EMOTION_MARKERS = {
        "i feel", "i'm feeling", "i am feeling", "frustrated", "confused",
        "excited", "sad", "angry", "overwhelmed", "happy", "depressed", "lonely"
    }
    MATH_MARKERS = {
        "solve", "equation", "integral", "derivative", "proof", "algebra",
        "geometry", "calculus", "matrix", "theorem"
    }
    CODE_MARKERS = {
        "python", "javascript", "java", "c++", "code", "bug", "error",
        "stacktrace", "function", "class", "compile", "debug"
    }
    CORRECTION_MARKERS = {
        "actually", "correction", "to clarify", "i meant", "not exactly"
    }
    CHIT_CHAT_MARKERS = {
        "how are you", "what's up", "sup", "hows it going", "long time no see",
        "how have you been"
    }

    PRIORITY_ORDER = [
        "greeting", "closing", "question", "instruction",
        "emotional_expression", "math", "code", "correction",
        "chit_chat", "narrative", "unknown"
    ]

    def __init__(self, thresholds: Optional[dict] = None):
        self.thresholds = thresholds or {}

    def classify(self, text: str) -> IntentResult:
        """
        Classify text into a single dominant intent.
        """
        if not text or not text.strip():
            return IntentResult(intent="unknown", confidence=0.0, rationale="Empty input")

        t = normalize_text(text)

        # Greeting
        if any(k in t for k in self.GREETING_KEYWORDS):
            return IntentResult(intent="greeting", confidence=0.85, rationale="Matched greeting keywords")

        # Closing
        if any(k in t for k in self.CLOSING_KEYWORDS):
            return IntentResult(intent="closing", confidence=0.85, rationale="Matched closing keywords")

        # Question
        if "?" in t or any(t.startswith(k) or f" {k} " in t for k in self.QUESTION_MARKERS):
            return IntentResult(intent="question", confidence=0.8, rationale="Question mark or interrogative detected")

        # Instruction
        if any(k in t for k in self.INSTRUCTION_MARKERS):
            return IntentResult(intent="instruction", confidence=0.75, rationale="Instructional phrasing detected")

        # Emotional expression
        if any(k in t for k in self.EMOTION_MARKERS):
            return IntentResult(intent="emotional_expression", confidence=0.7, rationale="Emotion markers detected")

        # Math
        if any(k in t for k in self.MATH_MARKERS):
            return IntentResult(intent="math", confidence=0.7, rationale="Math markers detected")

        # Code
        if any(k in t for k in self.CODE_MARKERS):
            return IntentResult(intent="code", confidence=0.7, rationale="Code markers detected")

        # Correction
        if any(k in t for k in self.CORRECTION_MARKERS):
            return IntentResult(intent="correction", confidence=0.6, rationale="Correction markers detected")

        # Chit-chat
        if any(k in t for k in self.CHIT_CHAT_MARKERS):
            return IntentResult(intent="chit_chat", confidence=0.6, rationale="Chit-chat pattern detected")

        # Narrative
        if len(t.split()) > 20 and "?" not in t:
            return IntentResult(intent="narrative", confidence=0.55, rationale="Long statement without question")

        return IntentResult(intent="unknown", confidence=0.4, rationale="No strong pattern match")

    def classify_all(self, text: str) -> List[IntentResult]:
        """
        Return all matching intents with confidence scores.
        """
        if not text or not text.strip():
            return [IntentResult(intent="unknown", confidence=0.0, rationale="Empty input")]

        t = normalize_text(text)
        results: List[IntentResult] = []

        checks: Dict[str, Tuple[set, float, str]] = {
            "greeting": (self.GREETING_KEYWORDS, 0.85, "Matched greeting keywords"),
            "closing": (self.CLOSING_KEYWORDS, 0.85, "Matched closing keywords"),
            "instruction": (self.INSTRUCTION_MARKERS, 0.75, "Instructional phrasing detected"),
            "emotional_expression": (self.EMOTION_MARKERS, 0.7, "Emotion markers detected"),
            "math": (self.MATH_MARKERS, 0.7, "Math markers detected"),
            "code": (self.CODE_MARKERS, 0.7, "Code markers detected"),
            "correction": (self.CORRECTION_MARKERS, 0.6, "Correction markers detected"),
            "chit_chat": (self.CHIT_CHAT_MARKERS, 0.6, "Chit-chat pattern detected"),
        }

        # Greeting/closing/etc.
        for intent, (keywords, conf, rationale) in checks.items():
            if any(k in t for k in keywords):
                results.append(IntentResult(intent=intent, confidence=conf, rationale=rationale))

        # Question
        if "?" in t or any(t.startswith(k) or f" {k} " in t for k in self.QUESTION_MARKERS):
            results.append(IntentResult(intent="question", confidence=0.8, rationale="Question mark or interrogative detected"))

        # Narrative
        if len(t.split()) > 20 and "?" not in t:
            results.append(IntentResult(intent="narrative", confidence=0.55, rationale="Long statement without question"))

        if not results:
            results.append(IntentResult(intent="unknown", confidence=0.4, rationale="No strong pattern match"))

        return results

    def explain(self, text: str) -> Dict[str, Any]:
        """
        Provide detailed explanation of classification:
        - Dominant intent
        - Confidence
        - Rationale
        - All possible matches
        """
        dominant = self.classify(text)
        all_matches = self.classify_all(text)
        return {
            "text": text,
            "dominant": dominant,
            "all_matches": all_matches,
        }
