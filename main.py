# main.py
import tkinter as tk
from context_manager import ContextManager
from chain_builder import ChainBuilder
from schema import InferenceInput, InferenceOutput


class CCBApp:
    def __init__(self, root):
        self.cm = ContextManager(chain_builder=ChainBuilder())
        self.root = root
        self.root.title("Conversational Context Builder")

        # Conversation display
        self.text_area = tk.Text(root, wrap="word", height=20, width=70, state="disabled")
        self.text_area.pack(padx=10, pady=10)

        # User input
        self.entry = tk.Entry(root, width=55)
        self.entry.pack(side="left", padx=10, pady=10)
        self.entry.bind("<Return>", self.send_message)

        # Buttons
        self.send_button = tk.Button(root, text="Send", command=self.send_message)
        self.send_button.pack(side="left", padx=5)

        self.clear_button = tk.Button(root, text="Clear Memory", command=self.clear_memory)
        self.clear_button.pack(side="left", padx=5)

        self.load_button = tk.Button(root, text="Load Conversation", command=self.load_conversation)
        self.load_button.pack(side="left", padx=5)

    def send_message(self, event=None):
        user_input = self.entry.get()
        if not user_input.strip():
            return

        self._append_text(f"You: {user_input}\n")
        self.entry.delete(0, tk.END)

        # Process input through ContextManager
        context: InferenceOutput = self.cm.process_input(user_input)

        response_text = (
            f"Intent: {context.intent} | "
            f"Emotion: {context.emotion} | "
            f"Subtext: {', '.join(context.subtext_tags) if context.subtext_tags else 'none'} | "
            f"Summary: {context.summary or 'n/a'}\n"
        )

        self._append_text(f"CCB: {response_text}\n")

    def clear_memory(self):
        self.cm.memory.clear()
        self.text_area.config(state="normal")
        self.text_area.delete(1.0, tk.END)
        self.text_area.insert(tk.END, "Conversation cleared.\n")
        self.text_area.config(state="disabled")

    def load_conversation(self):
        self.text_area.config(state="normal")
        self.text_area.delete(1.0, tk.END)
        if not self.cm.memory.messages:
            self.text_area.insert(tk.END, "No previous conversation found.\n")
        else:
            for msg in self.cm.memory.messages:
                self.text_area.insert(tk.END, f"{msg['sender'].capitalize()}: {msg['text']}\n")
        self.text_area.config(state="disabled")

    def _append_text(self, text):
        self.text_area.config(state="normal")
        self.text_area.insert(tk.END, text)
        self.text_area.config(state="disabled")
        self.text_area.see(tk.END)


if __name__ == "__main__":
    root = tk.Tk()
    app = CCBApp(root)
    root.mainloop()
