# context_manager.py
from memory_store import MemoryStore
from chain_builder import ChainBuilder
from schema import InferenceInput, InferenceOutput


class ContextManager:
    """
    Manages conversation context, memory, and inference pipeline.
    Integrates:
    - MemoryStore for storing conversation turns
    - ChainBuilder for processing user input
    - Updates summaries, insights, and subtext
    """

    def __init__(self, chain_builder: ChainBuilder = None):
        self.memory = MemoryStore()
        self.chain_builder = chain_builder or ChainBuilder()
        self.turn_number = 0

    def process_input(self, user_input: str) -> InferenceOutput:
        """
        Process a single user input:
        - Store in memory
        - Run inference pipeline
        - Update summary and insights
        """
        self.turn_number += 1

        # Save user message
        self.memory.add_message("user", user_input)

        # Run inference pipeline via ChainBuilder
        inference_input = InferenceInput(text=user_input)
        context: InferenceOutput = self.chain_builder.process_turn(inference_input)

        # Construct structured response summary
        response_summary = (
            f"- Turn {self.turn_number}: {user_input} "
            f"(Intent: {context.intent}) "
            f"(Emotion: {context.emotion}) "
            f"(Subtext: {', '.join(context.subtext_tags) if context.subtext_tags else 'none'})"
        )

        # Save assistant summary in memory
        self.memory.add_message("ccb", response_summary)

        # Key insights for display/logging
        insights = []
        if context.intent:
            insights.append(f"Dominant intent appears to be '{context.intent}'.")
        if context.emotion:
            insights.append(f"Prevailing emotion is '{context.emotion}'.")
        if context.subtext_tags:
            insights.append("Subtext cues detected: " + ", ".join(context.subtext_tags))

        # Store insights in context object
        context.summary = "\n".join([response_summary] + insights)

        return context
