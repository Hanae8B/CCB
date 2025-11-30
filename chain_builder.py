# chain_builder.py
from typing import Optional
from intent_classifier import IntentClassifier
from emotion_classifier import EmotionClassifier
from subtext_detector import SubtextDetector
from conversation_state_machine import ConversationStateMachine
from summarizer import Summarizer
from schema import InferenceInput, InferenceOutput
from state_manager import Turn  # <-- import the Turn dataclass


class ChainBuilder:
    """
    Orchestrates analysis across modules and returns a unified InferenceOutput.
    """

    def __init__(self):
        self.intent_analyzer = IntentClassifier()
        self.emotion_detector = EmotionClassifier()
        self.subtext_inferencer = SubtextDetector()
        self.fsm = ConversationStateMachine()
        self.summarizer = Summarizer()
        self.turns = []  # keep Turn objects

    def process_turn(
        self, inp: InferenceInput, assistant_text: Optional[str] = None
    ) -> InferenceOutput:
        text = inp.text or ""

        # Run classifiers
        intent = self.intent_analyzer.classify(text)
        emotion = self.emotion_detector.classify(text)
        subtext_tags = self.subtext_inferencer.detect(text)

        # State machine transition
        transition = self.fsm.transition(intent, subtext_tags[0] if subtext_tags else None)
        state = transition.current

        # Build a Turn object and store it
        turn = Turn(user_text=text, intent=intent, emotion=emotion, subtext_tags=subtext_tags)
        self.turns.append(turn)

        # Summarize based on Turn objects
        summary = self.summarizer.summarize(self.turns)

        return InferenceOutput(
            intent=intent,
            emotion=emotion,
            subtext_tags=subtext_tags,
            summary=summary,
            raw={"state": state, "transition": transition},
        )
