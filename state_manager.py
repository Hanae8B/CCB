# state_manager.py
from typing import Any, Dict, Optional, List
from dataclasses import dataclass, field
import time


@dataclass
class Turn:
    user_text: str
    intent: str
    emotion: str
    subtext_tags: List[str]
    timestamp: float = field(default_factory=lambda: time.time())


@dataclass
class ConversationState:
    turns: List[Turn] = field(default_factory=list)
    last_intent: Optional[str] = None
    last_emotion: Optional[str] = None
    meta: Dict[str, Any] = field(default_factory=dict)


class StateManager:
    """
    Minimal in-memory state manager with append/get/reset operations.
    """

    def __init__(self):
        self._state = ConversationState()

    def append_turn(self, turn: Turn) -> None:
        self._state.turns.append(turn)
        self._state.last_intent = turn.intent
        self._state.last_emotion = turn.emotion

    def get_state(self) -> ConversationState:
        return self._state

    def reset(self) -> None:
        self._state = ConversationState()

    def set_meta(self, key: str, value: Any) -> None:
        self._state.meta[key] = value

    def get_meta(self, key: str, default: Any = None) -> Any:
        return self._state.meta.get(key, default)
