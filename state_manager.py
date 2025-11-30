# state_manager.py
"""
State Manager

Responsibilities:
- Maintain conversation state in memory
- Track turns, intents, emotions, and subtext
- Provide append, get, reset, and metadata operations
- Support serialization, search, pruning, and inspection
"""

from typing import Any, Dict, Optional, List
from dataclasses import dataclass, field, asdict
import time


# -----------------------------
# Data Structures
# -----------------------------
@dataclass
class Turn:
    """
    Represents a single conversational turn.
    """
    user_text: str
    intent: str
    emotion: str
    subtext_tags: List[str]
    assistant_text: Optional[str] = None
    state: Optional[str] = None
    timestamp: float = field(default_factory=lambda: time.time())
    meta: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """Convert Turn to dictionary for serialization."""
        return asdict(self)


@dataclass
class ConversationState:
    """
    Represents the full conversation state.
    """
    turns: List[Turn] = field(default_factory=list)
    last_intent: Optional[str] = None
    last_emotion: Optional[str] = None
    current_state: str = "IDLE"
    meta: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """Convert ConversationState to dictionary for serialization."""
        return {
            "turns": [t.to_dict() for t in self.turns],
            "last_intent": self.last_intent,
            "last_emotion": self.last_emotion,
            "current_state": self.current_state,
            "meta": self.meta,
        }


# -----------------------------
# State Manager
# -----------------------------
class StateManager:
    """
    In-memory state manager with append/get/reset operations.

    Features:
    - Append new turns
    - Track last intent and emotion
    - Manage metadata
    - Reset state
    - Search and prune utilities
    - Serialization for persistence
    """

    def __init__(self):
        self._state = ConversationState()

    # -----------------------------
    # Core Operations
    # -----------------------------
    def append_turn(self, turn: Turn) -> None:
        """Append a new turn and update last intent/emotion."""
        self._state.turns.append(turn)
        self._state.last_intent = turn.intent
        self._state.last_emotion = turn.emotion

    def get_state(self) -> ConversationState:
        """Return current conversation state."""
        return self._state

    def reset(self) -> None:
        """Reset conversation state to empty."""
        self._state = ConversationState()

    # -----------------------------
    # Metadata Operations
    # -----------------------------
    def set_meta(self, key: str, value: Any) -> None:
        """Set metadata key/value."""
        self._state.meta[key] = value

    def get_meta(self, key: str, default: Any = None) -> Any:
        """Get metadata value by key."""
        return self._state.meta.get(key, default)

    # -----------------------------
    # Utilities
    # -----------------------------
    def last_turn(self) -> Optional[Turn]:
        """Return the most recent turn."""
        return self._state.turns[-1] if self._state.turns else None

    def search_turns(self, keyword: str) -> List[Turn]:
        """Search turns containing a keyword in user_text or assistant_text."""
        keyword_lower = keyword.lower()
        return [
            t for t in self._state.turns
            if keyword_lower in (t.user_text or "").lower()
            or keyword_lower in (t.assistant_text or "").lower()
        ]

    def prune_turns(self, max_turns: int, strategy: str = "oldest") -> None:
        """
        Prune turns to keep at most `max_turns`.
        Strategies:
        - "oldest": keep most recent turns
        - "newest": keep earliest turns
        """
        if len(self._state.turns) <= max_turns:
            return

        if strategy == "oldest":
            self._state.turns = self._state.turns[-max_turns:]
        elif strategy == "newest":
            self._state.turns = self._state.turns[:max_turns]
        else:
            raise ValueError(f"Unknown prune strategy: {strategy}")

    def to_dict(self) -> Dict[str, Any]:
        """Serialize full state to dictionary."""
        return self._state.to_dict()

    def from_dict(self, data: Dict[str, Any]) -> None:
        """
        Load state from dictionary.
        """
        try:
            turns = [Turn(**t) for t in data.get("turns", [])]
            self._state = ConversationState(
                turns=turns,
                last_intent=data.get("last_intent"),
                last_emotion=data.get("last_emotion"),
                current_state=data.get("current_state", "IDLE"),
                meta=data.get("meta", {}),
            )
        except Exception as e:
            print(f"Error loading state from dict: {e}")
            self.reset()
