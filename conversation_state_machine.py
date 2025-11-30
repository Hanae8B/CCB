"""
Conversation State Machine

Responsibilities:
- Manage conversation phases via finite state machine
- Provide structured transitions with rationale
- Support reset, validation, and inspection utilities
"""

from typing import Optional, Dict, Any
from dataclasses import dataclass


# -----------------------------
# Data structures
# -----------------------------
@dataclass
class Transition:
    """
    Represents a state transition in the conversation state machine.
    """
    previous: str
    current: str
    rationale: str
    metadata: Optional[Dict[str, Any]] = None


# -----------------------------
# FSM implementation
# -----------------------------
class ConversationStateMachine:
    """
    Finite state machine for conversation phases.

    States:
    - IDLE: no active conversation
    - GREETING: user greets or starts conversation
    - REQUEST: user asks a question or gives instruction
    - CLARIFICATION: user seeks clarification or elaboration
    - FOLLOWUP: user continues, corrects, or adds narrative
    - EMOTIONAL_SUPPORT: user expresses emotions needing support
    - CLOSING: user ends conversation

    Features:
    - Deterministic transitions based on intent + subtext
    - Reset and validation utilities
    - Transparent rationale for each transition
    """

    VALID_STATES = {
        "IDLE",
        "GREETING",
        "REQUEST",
        "CLARIFICATION",
        "FOLLOWUP",
        "EMOTIONAL_SUPPORT",
        "CLOSING",
    }

    def __init__(self, initial: str = "IDLE"):
        if initial not in self.VALID_STATES:
            raise ValueError(f"Invalid initial state: {initial}")
        self.state: str = initial

    def reset(self) -> None:
        """
        Reset FSM to IDLE state.
        """
        self.state = "IDLE"

    def get_state(self) -> str:
        """
        Return current state.
        """
        return self.state

    def transition(self, intent: str, subtext_primary: Optional[str]) -> Transition:
        """
        Transition FSM based on intent and optional subtext.

        Args:
            intent: classified intent string
            subtext_primary: primary subtext tag (if any)

        Returns:
            Transition object with previous, current, rationale, metadata
        """
        prev = self.state
        rationale_parts = [f"Intent={intent}"]
        if subtext_primary:
            rationale_parts.append(f"Subtext={subtext_primary}")

        # --- Transition logic ---
        if intent == "greeting":
            self.state = "GREETING"

        elif intent in ("question", "instruction", "math", "code", "request"):
            if subtext_primary == "seeking_clarification":
                self.state = "CLARIFICATION"
            else:
                self.state = "REQUEST"

        elif intent in ("correction", "narrative", "chit_chat", "feedback", "opinion"):
            self.state = "FOLLOWUP"

        elif intent in ("emotional_expression", "emotional_state", "emotional_positive", "emotional_negative"):
            self.state = "EMOTIONAL_SUPPORT"

        elif intent in ("closing", "goodbye"):
            self.state = "CLOSING"

        else:
            # Default fallback logic
            if self.state == "IDLE":
                self.state = "FOLLOWUP"
            # Otherwise remain in current state

        rationale = "; ".join(rationale_parts)

        return Transition(
            previous=prev,
            current=self.state,
            rationale=rationale,
            metadata={"intent": intent, "subtext": subtext_primary},
        )

    def validate_state(self, state: str) -> bool:
        """
        Validate if a state is recognized.
        """
        return state in self.VALID_STATES

    def describe(self) -> str:
        """
        Human-readable description of current state.
        """
        descriptions = {
            "IDLE": "No active conversation; waiting for input.",
            "GREETING": "User greeted or initiated conversation.",
            "REQUEST": "User asked a question or gave instruction.",
            "CLARIFICATION": "User seeks clarification or elaboration.",
            "FOLLOWUP": "User continues, corrects, or adds narrative.",
            "EMOTIONAL_SUPPORT": "User expressed emotions needing support.",
            "CLOSING": "User ended the conversation.",
        }
        return descriptions.get(self.state, f"Unknown state: {self.state}")
