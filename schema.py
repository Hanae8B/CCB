# schema.py
"""
Schema Definitions

Responsibilities:
- Define core dataclasses for messages, inference input/output, conversations, and routing
- Provide validation and utility methods
- Ensure transparency and extensibility
"""

from dataclasses import dataclass, field, asdict
from typing import List, Optional, Dict, Any
import time


# -----------------------------
# Core Message Structures
# -----------------------------
@dataclass
class Message:
    """
    Represents a single message in a conversation.
    """
    role: str  # 'user' | 'assistant' | 'system'
    content: str
    timestamp: float = field(default_factory=lambda: time.time())
    metadata: Optional[Dict[str, Any]] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert Message to dictionary."""
        return asdict(self)


# -----------------------------
# Inference Pipeline Structures
# -----------------------------
@dataclass
class InferenceInput:
    """
    Input to inference pipeline.
    """
    text: str
    context: Optional[List[Message]] = None
    metadata: Optional[Dict[str, Any]] = None

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class InferenceOutput:
    """
    Output from inference pipeline.
    """
    intent: str
    emotion: str
    subtext_tags: List[str]
    summary: Optional[str] = None
    raw: Optional[Dict[str, Any]] = None  # any extra diagnostic info

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


# -----------------------------
# Conversation Structures
# -----------------------------
@dataclass
class Conversation:
    """
    Represents a full conversation with multiple messages.
    """
    messages: List[Message] = field(default_factory=list)

    def add(self, role: str, content: str, metadata: Optional[Dict[str, Any]] = None) -> None:
        """Add a new message to the conversation."""
        self.messages.append(Message(role=role, content=content, metadata=metadata))

    def last_user_text(self) -> Optional[str]:
        """Return the most recent user message text."""
        for msg in reversed(self.messages):
            if msg.role == "user":
                return msg.content
        return None

    def last_assistant_text(self) -> Optional[str]:
        """Return the most recent assistant message text."""
        for msg in reversed(self.messages):
            if msg.role == "assistant":
                return msg.content
        return None

    def as_context(self, last_n: int = 10) -> List[Message]:
        """Return the last n messages as context."""
        return self.messages[-last_n:]

    def to_dict(self) -> Dict[str, Any]:
        """Convert conversation to dictionary."""
        return {"messages": [m.to_dict() for m in self.messages]}


# -----------------------------
# Intent & Subtext Structures
# -----------------------------
@dataclass
class IntentResult:
    """
    Result of intent classification.
    """
    intent: str
    confidence: float
    rationale: str

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class SubtextResult:
    """
    Result of subtext detection.
    """
    primary: Optional[str] = None
    secondary: Optional[List[str]] = None
    rationale: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


# -----------------------------
# Router Structures
# -----------------------------
@dataclass
class RouterDecision:
    """
    Routing decision for pipeline modules.
    """
    route: List[str]
    rationale: str

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


# -----------------------------
# State Management Structures
# -----------------------------
@dataclass
class Turn:
    """
    Represents a single turn in the conversation state.
    """
    user_text: str
    assistant_text: Optional[str] = None
    intent: Optional[str] = None
    emotion: Optional[str] = None
    subtext_tags: Optional[List[str]] = None
    state: Optional[str] = None
    timestamp: float = field(default_factory=lambda: time.time())

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class StateSnapshot:
    """
    Snapshot of current conversation state.
    """
    turns: List[Turn] = field(default_factory=list)
    current_state: str = "IDLE"

    def to_dict(self) -> Dict[str, Any]:
        return {
            "current_state": self.current_state,
            "turns": [t.to_dict() for t in self.turns],
        }
