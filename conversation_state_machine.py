# conversation_state_machine.py
from typing import Optional
from dataclasses import dataclass


@dataclass
class StateTransition:
    previous: str
    current: str
    rationale: str


class ConversationStateMachine:
    """
    Finite state machine for conversation phases.
    States: GREETING, REQUEST, FOLLOWUP, CLARIFICATION, EMOTIONAL_SUPPORT, CLOSING, IDLE
    """

    def __init__(self, initial: str = "IDLE"):
        self.state = initial

    def transition(self, intent: str, subtext_primary: Optional[str]) -> StateTransition:
        prev = self.state

        if intent == "greeting":
            self.state = "GREETING"
        elif intent in ("question", "instruction", "math", "code"):
            if subtext_primary == "seeking_clarification":
                self.state = "CLARIFICATION"
            else:
                self.state = "REQUEST"
        elif intent in ("correction", "narrative", "chit_chat"):
            self.state = "FOLLOWUP"
        elif intent == "emotional_expression":
            self.state = "EMOTIONAL_SUPPORT"
        elif intent == "closing":
            self.state = "CLOSING"
        else:
            if self.state == "IDLE":
                self.state = "FOLLOWUP"

        return StateTransition(
            previous=prev,
            current=self.state,
            rationale=f"Intent={intent}; subtext={subtext_primary}",
        )
