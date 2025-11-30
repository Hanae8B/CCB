# chain_builder.py
from typing import Optional, List, Dict, Any
from intent_classifier import IntentClassifier
from emotion_classifier import EmotionClassifier
from subtext_detector import SubtextDetector
from conversation_state_machine import ConversationStateMachine, Transition
from summarizer import Summarizer
from schema import InferenceInput, InferenceOutput
from state_manager import Turn  # <-- import the Turn dataclass


class ChainBuilder:
    """
    Orchestrates analysis across modules and returns a unified InferenceOutput.

    Responsibilities:
    - Run intent, emotion, and subtext classifiers
    - Drive conversation state machine transitions
    - Maintain a history of Turn objects
    - Summarize conversation history
    - Provide unified InferenceOutput with raw metadata

    Features:
    - Extensible: swap out classifiers or summarizer
    - Transparent: returns raw state/transition info
    - Robust: handles empty input, errors gracefully
    """

    def __init__(self):
        # Core analyzers
        self.intent_analyzer = IntentClassifier()
        self.emotion_detector = EmotionClassifier()
        self.subtext_inferencer = SubtextDetector()

        # State machine & summarizer
        self.fsm = ConversationStateMachine()
        self.summarizer = Summarizer()

        # Conversation memory
        self.turns: List[Turn] = []

    def reset(self) -> None:
        """
        Clears stored conversation turns and resets state machine.
        """
        self.turns.clear()
        self.fsm.reset()

    def process_turn(
        self, inp: InferenceInput, assistant_text: Optional[str] = None
    ) -> InferenceOutput:
        """
        Process a single user turn and return unified inference output.

        Args:
            inp: InferenceInput containing user text and metadata
            assistant_text: Optional assistant response text (for richer context)

        Returns:
            InferenceOutput with intent, emotion, subtext, summary, and raw state info
        """
        text = inp.text or ""

        # --- Run classifiers ---
        try:
            intent = self.intent_analyzer.classify(text)
        except Exception as e:
            intent = "unknown"
            self._log_error("IntentClassifier", e)

        try:
            emotion = self.emotion_detector.classify(text)
        except Exception as e:
            emotion = "neutral"
            self._log_error("EmotionClassifier", e)

        try:
            subtext_tags = self.subtext_inferencer.detect(text)
        except Exception as e:
            subtext_tags = []
            self._log_error("SubtextDetector", e)

        # --- State machine transition ---
        try:
            transition: Transition = self.fsm.transition(
                intent, subtext_tags[0] if subtext_tags else None
            )
            state = transition.current
        except Exception as e:
            transition = Transition(previous="unknown", current="unknown", trigger=None)
            state = "unknown"
            self._log_error("ConversationStateMachine", e)

        # --- Build Turn object ---
        turn = Turn(
            user_text=text,
            assistant_text=assistant_text,
            intent=intent,
            emotion=emotion,
            subtext_tags=subtext_tags,
            state=state,
        )
        self.turns.append(turn)

        # --- Summarize conversation ---
        try:
            summary = self.summarizer.summarize(self.turns)
        except Exception as e:
            summary = ""
            self._log_error("Summarizer", e)

        # --- Build unified output ---
        return InferenceOutput(
            intent=intent,
            emotion=emotion,
            subtext_tags=subtext_tags,
            summary=summary,
            raw={
                "state": state,
                "transition": transition,
                "turn_count": len(self.turns),
                "last_turn": turn,
            },
        )

    def get_history(self) -> List[Turn]:
        """
        Returns the full conversation history as a list of Turn objects.
        """
        return list(self.turns)

    def get_last_turn(self) -> Optional[Turn]:
        """
        Returns the most recent Turn object, if any.
        """
        return self.turns[-1] if self.turns else None

    def _log_error(self, component: str, error: Exception) -> None:
        """
        Internal error logging hook. Replace with real logger if needed.
        """
        print(f"[ChainBuilder] Error in {component}: {error}")