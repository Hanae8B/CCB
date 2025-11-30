# memory_store.py
"""
Memory Store

Responsibilities:
- Persist conversation messages to disk
- Provide utilities for retrieval, search, and pruning
- Handle corrupted or invalid files gracefully
- Support metadata (timestamps, roles)
"""

import json
import os
import time
from typing import List, Dict, Optional, Union, Any


class MemoryStore:
    """
    Persistent memory store for conversation messages.

    Features:
    - JSON file persistence
    - Robust error handling
    - Metadata support (timestamp, role)
    - Retrieval utilities (recent, last, all)
    - Search and pruning
    - Clear/reset functionality
    """

    def __init__(self, filename: str = "conversation.json"):
        self.filename = filename
        self.messages: List[Dict[str, Any]] = []
        self._load()

    # -----------------------------
    # Persistence
    # -----------------------------
    def _load(self) -> None:
        """Load messages from file if it exists, else start empty."""
        if os.path.exists(self.filename):
            try:
                with open(self.filename, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    if isinstance(data, list) and all(
                        isinstance(m, dict) and "sender" in m and "text" in m
                        for m in data
                    ):
                        self.messages = data
                    else:
                        print("Warning: memory file structure invalid, starting fresh.")
                        self.messages = []
            except json.JSONDecodeError:
                print("Warning: memory file corrupted, starting fresh.")
                self.messages = []
            except Exception as e:
                print(f"Error loading memory: {e}")
                self.messages = []
        else:
            self.messages = []

    def _save(self) -> None:
        """Persist messages to file."""
        try:
            with open(self.filename, "w", encoding="utf-8") as f:
                json.dump(self.messages, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"Error saving memory: {e}")

    # -----------------------------
    # Message Management
    # -----------------------------
    def add_message(self, sender: str, text: Union[str, int, float], role: Optional[str] = None) -> None:
        """
        Add a message to memory and save.
        Only accepts JSON‑serializable primitives for 'text'.
        """
        safe_text = str(text)  # always store as string
        message = {
            "sender": str(sender),
            "text": safe_text,
            "role": role or "user",
            "timestamp": time.time(),
        }
        self.messages.append(message)
        self._save()

    def get_recent_messages(self, n: int) -> List[Dict[str, Any]]:
        """Return the last n messages."""
        return self.messages[-n:]

    def last_message(self) -> Optional[Dict[str, Any]]:
        """Return the most recent message or None if empty."""
        return self.messages[-1] if self.messages else None

    def all_messages(self) -> List[Dict[str, Any]]:
        """Return all messages."""
        return list(self.messages)

    def clear(self) -> None:
        """Clear all saved messages and overwrite the file."""
        self.messages = []
        self._save()

    # -----------------------------
    # Search & Utilities
    # -----------------------------
    def search(self, keyword: str) -> List[Dict[str, Any]]:
        """
        Search messages containing a keyword (case-insensitive).
        """
        keyword_lower = keyword.lower()
        return [m for m in self.messages if keyword_lower in m.get("text", "").lower()]

    def prune(self, max_messages: int, strategy: str = "oldest") -> None:
        """
        Prune memory to keep at most `max_messages`.
        Strategies:
        - "oldest": remove oldest messages
        - "newest": remove newest messages
        """
        if len(self.messages) <= max_messages:
            return

        if strategy == "oldest":
            self.messages = self.messages[-max_messages:]
        elif strategy == "newest":
            self.messages = self.messages[:max_messages]
        else:
            print(f"Unknown prune strategy: {strategy}")
            return

        self._save()

    def export(self) -> str:
        """
        Export messages as a JSON string.
        """
        try:
            return json.dumps(self.messages, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"Error exporting memory: {e}")
            return "[]"

    def import_messages(self, data: Union[str, List[Dict[str, Any]]]) -> None:
        """
        Import messages from JSON string or list of dicts.
        """
        try:
            if isinstance(data, str):
                parsed = json.loads(data)
            else:
                parsed = data

            if isinstance(parsed, list) and all("sender" in m and "text" in m for m in parsed):
                self.messages = parsed
                self._save()
            else:
                print("Invalid import data structure.")
        except Exception as e:
            print(f"Error importing messages: {e}")
