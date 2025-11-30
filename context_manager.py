# context_manager.py
from memory_store import MemoryStore
from chain_builder import ChainBuilder
from schema import InferenceInput, InferenceOutput


class ContextManager:
    def __init__(self, chain_builder: ChainBuilder = None):
        self.memory = MemoryStore()
        self.chain_builder = chain_builder or ChainBuilder()

    def process_input(self, user_input: str) -> InferenceOutput:
        # Save user message as plain string
        self.memory.add_message("user", user_input)

        # Analyze with ChainBuilder (unwrap inside process_turn)
        context: InferenceOutput = self.chain_builder.process_turn(InferenceInput(text=user_input))

        # Save assistant summary
        response_summary = (
            f"Intent={context.intent}, "
            f"Emotion={context.emotion}, "
            f"Subtext={', '.join(context.subtext_tags) if context.subtext_tags else 'none'}, "
            f"Summary={context.summary or 'n/a'}"
        )
        self.memory.add_message("ccb", response_summary)

        return context
