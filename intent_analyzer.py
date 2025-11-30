# intent_analyzer.py
from typing import Optional
from schema import IntentResult
from utils import normalize_text


class IntentAnalyzer:
    """
    Classifies user input into a coarse intent category:
    - greeting, question, instruction, emotional_expression, chit_chat, narrative, math, code, correction, closing, unknown
    """

    GREETING_KEYWORDS = {"hi", "hello", "hey", "good morning", "good evening", "good afternoon"}
    CLOSING_KEYWORDS = {"bye", "goodbye", "see you", "thanks", "thank you", "cheers"}
    QUESTION_MARKERS = {"?", "what", "why", "how", "when", "where", "who", "which"}
    INSTRUCTION_MARKERS = {"please", "can you", "could you", "help me", "show me", "explain", "walk me through", "build", "create"}
    EMOTION_MARKERS = {"i feel", "i'm feeling", "i am feeling", "frustrated", "confused", "excited", "sad", "angry", "overwhelmed"}
    MATH_MARKERS = {"solve", "equation", "integral", "derivative", "proof", "algebra", "geometry"}
    CODE_MARKERS = {"python", "javascript", "code", "bug", "error", "stacktrace", "function", "class"}
    CORRECTION_MARKERS = {"actually", "correction", "to clarify", "i meant"}
    CHIT_CHAT_MARKERS = {"how are you", "what's up", "sup", "hows it going"}

    def __init__(self, thresholds: Optional[dict] = None):
        self.thresholds = thresholds or {}

    def classify(self, text: str) -> IntentResult:
        t = normalize_text(text)

        # Greeting
        if any(k in t for k in self.GREETING_KEYWORDS):
            return IntentResult(intent="greeting", confidence=0.85, rationale="Matched greeting keywords")

        # Closing
        if any(k in t for k in self.CLOSING_KEYWORDS):
            return IntentResult(intent="closing", confidence=0.85, rationale="Matched closing keywords")

        # Question (presence of '?' or interrogative)
        if "?" in t or any(t.startswith(k) or f" {k} " in t for k in self.QUESTION_MARKERS):
            return IntentResult(intent="question", confidence=0.8, rationale="Question mark or interrogative detected")

        # Instruction/request
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

        # Narrative (longer non-question statement)
        if len(t.split()) > 20 and "?" not in t:
            return IntentResult(intent="narrative", confidence=0.55, rationale="Long statement without question")

        return IntentResult(intent="unknown", confidence=0.4, rationale="No strong pattern match")
