# main.py
"""
Main Application Entry Point

Conversational Context Builder (CCB) GUI using Tkinter.

Responsibilities:
- Provide a user interface for interacting with ContextManager
- Display conversation history and inference results
- Support memory clearing and conversation loading
- Handle errors gracefully and log events
"""

import tkinter as tk
from typing import Optional
from context_manager import ContextManager
from chain_builder import ChainBuilder
from schema import InferenceOutput
from logger import get_logger

# Initialize logger
log = get_logger(__name__)


class CCBApp:
    """
    Tkinter-based GUI application for Conversational Context Builder.
    """

    def __init__(self, root: tk.Tk, title: str = "Conversational Context Builder (CCB)"):
        self.cm = ContextManager(chain_builder=ChainBuilder())
        self.root = root
        self.root.title(title)

        # Conversation display
        self.text_area = tk.Text(root, wrap="word", height=20, width=80, state="disabled")
        self.text_area.pack(padx=10, pady=10)

        # User input
        self.entry = tk.Entry(root, width=60)
        self.entry.pack(side="left", padx=10, pady=10)
        self.entry.bind("<Return>", self.send_message)

        # Buttons
        self.send_button = tk.Button(root, text="Send", command=self.send_message)
        self.send_button.pack(side="left", padx=5)

        self.clear_button = tk.Button(root, text="Clear Memory", command=self.clear_memory)
        self.clear_button.pack(side="left", padx=5)

        self.load_button = tk.Button(root, text="Load Conversation", command=self.load_conversation)
        self.load_button.pack(side="left", padx=5)

        self.save_button = tk.Button(root, text="Save Conversation", command=self.save_conversation)
        self.save_button.pack(side="left", padx=5)

    # -----------------------------
    # Event Handlers
    # -----------------------------
    def send_message(self, event: Optional[tk.Event] = None) -> None:
        """
        Handle sending a user message:
        - Append to display
        - Process through ContextManager
        - Display inference results
        """
        user_input = self.entry.get()
        if not user_input.strip():
            return

        self._append_text(f"You: {user_input}\n")
        self.entry.delete(0, tk.END)

        try:
            # Process input through ContextManager
            context: InferenceOutput = self.cm.process_input(user_input)

            response_text = (
                f"Intent: {context.intent} | "
                f"Emotion: {context.emotion} | "
                f"Subtext: {', '.join(context.subtext_tags) if context.subtext_tags else 'none'}\n"
                f"Summary: {context.summary or 'n/a'}\n"
            )

            self._append_text(f"CCB: {response_text}\n")
        except Exception as e:
            log.error(f"Error processing input: {e}")
            self._append_text("CCB: Error processing input. Please try again.\n")

    def clear_memory(self) -> None:
        """
        Clear conversation memory and reset display.
        """
        self.cm.reset()
        self.text_area.config(state="normal")
        self.text_area.delete(1.0, tk.END)
        self.text_area.insert(tk.END, "Conversation cleared.\n")
        self.text_area.config(state="disabled")
        log.info("Conversation memory cleared.")

    def load_conversation(self) -> None:
        """
        Load conversation history from memory and display.
        """
        self.text_area.config(state="normal")
        self.text_area.delete(1.0, tk.END)
        if not self.cm.memory.messages:
            self.text_area.insert(tk.END, "No previous conversation found.\n")
        else:
            for msg in self.cm.memory.messages:
                sender = msg.get("sender", "Unknown").capitalize()
                text = msg.get("text", "")
                self.text_area.insert(tk.END, f"{sender}: {text}\n")
        self.text_area.config(state="disabled")
        log.info("Conversation history loaded.")

    def save_conversation(self, file_path: str = "conversation_log.txt") -> None:
        """
        Save conversation history to a file.
        """
        try:
            with open(file_path, "w", encoding="utf-8") as f:
                for msg in self.cm.memory.messages:
                    sender = msg.get("sender", "Unknown").capitalize()
                    text = msg.get("text", "")
                    f.write(f"{sender}: {text}\n")
            self._append_text(f"Conversation saved to {file_path}\n")
            log.info(f"Conversation saved to {file_path}")
        except Exception as e:
            log.error(f"Error saving conversation: {e}")
            self._append_text("CCB: Error saving conversation.\n")

    # -----------------------------
    # Internal Utilities
    # -----------------------------
    def _append_text(self, text: str) -> None:
        """
        Append text to conversation display.
        """
        self.text_area.config(state="normal")
        self.text_area.insert(tk.END, text)
        self.text_area.config(state="disabled")
        self.text_area.see(tk.END)


# -----------------------------
# Entry Point
# -----------------------------
if __name__ == "__main__":
    root = tk.Tk()
    app = CCBApp(root)
    root.mainloop()
