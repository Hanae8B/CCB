# schema.py
from dataclasses import dataclass, field
from typing import List, Optional, Dict, Any
import time


@dataclass
class Message:
    role: str  # 'user' | 'assistant' | 'system'
    content: str
    timestamp: float = field(default_factory=lambda: time.time())


@dataclass
class InferenceInput:
    text: str
    context: Optional[List[Message]] = None
    metadata: Optional[Dict[str, Any]] = None


@dataclass
class InferenceOutput:
    intent: str
    emotion: str
    subtext_tags: List[str]
    summary: Optional[str] = None
    raw: Optional[Dict[str, Any]] = None  # any extra diagnostic info


@dataclass
class Conversation:
    messages: List[Message] = field(default_factory=list)

    def add(self, role: str, content: str) -> None:
        self.messages.append(Message(role=role, content=content))

    def last_user_text(self) -> Optional[str]:
        for msg in reversed(self.messages):
            if msg.role == "user":
                return msg.content
        return None

    def as_context(self, last_n: int = 10) -> List[Message]:
        return self.messages[-last_n:]
