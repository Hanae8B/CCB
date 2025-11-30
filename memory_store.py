import json
import os
from typing import List, Dict, Optional, Union


class MemoryStore:
    def __init__(self, filename: str = "conversation.json"):
        self.filename = filename
        self.messages: List[Dict[str, str]] = []
        self._load()

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

    def add_message(self, sender: str, text: Union[str, int, float]) -> None:
        """
        Add a message to memory and save.
        Only accepts JSON‑serializable primitives for 'text'.
        """
        safe_text = str(text)  # always store as string
        self.messages.append({"sender": str(sender), "text": safe_text})
        self._save()

    def get_recent_messages(self, n: int) -> List[Dict[str, str]]:
        """Return the last n messages."""
        return self.messages[-n:]

    def last_message(self) -> Optional[Dict[str, str]]:
        """Return the most recent message or None if empty."""
        return self.messages[-1] if self.messages else None

    def all_messages(self) -> List[Dict[str, str]]:
        """Return all messages."""
        return list(self.messages)

    def clear(self) -> None:
        """Clear all saved messages and overwrite the file."""
        self.messages = []
        self._save()
