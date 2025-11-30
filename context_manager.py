# context_manager.py
"""
Context Manager

Responsibilities:
- Manage conversation context and memory
- Orchestrate inference pipeline via ChainBuilder
- Maintain turn numbering and structured summaries
- Provide utilities for history, reset, and insights
"""

from typing import Optional, List, Dict, Any
from memory_store import MemoryStore
from chain_builder import ChainBuilder
from schema import InferenceInput, InferenceOutput


class ContextManager:
    """
    Manages conversation context, memory, and inference pipeline.

    Integrates:
    - MemoryStore for storing conversation turns/messages
    - ChainBuilder for processing user input
    - Updates summaries, insights, and subtext

    Features:
    - Robust error handling
    - Reset and history utilities
    - Transparent insights for logging/debugging
    """

    def __init__(self, chain_builder: Optional[ChainBuilder] = None):
        self.memory = MemoryStore()
        self.chain_builder = chain_builder or ChainBuilder()
        self.turn_number: int = 0

    def reset(self) -> None:
        """
        Reset the context manager:
        - Clear memory
        - Reset turn counter
        - Reset chain builder state
        """
        self.memory.clear()
        self.turn_number = 0
        self.chain_builder.reset()

    def process_input(self, user_input: str, assistant_text: Optional[str] = None) -> InferenceOutput:
        """
        Process a single user input:
        - Store in memory
        - Run inference pipeline
        - Update summary and insights

        Args:
            user_input: Raw text from user
            assistant_text: Optional assistant response for richer context

        Returns:
            InferenceOutput with structured summary and metadata
        """
        self.turn_number += 1

        # Save user message
        self.memory.add_message("user", user_input)

        # Run inference pipeline via ChainBuilder
        inference_input = InferenceInput(text=user_input)
        try:
            context: InferenceOutput = self.chain_builder.process_turn(inference_input, assistant_text)
        except Exception as e:
            # Fallback output if pipeline fails
            context = InferenceOutput(
                intent="unknown",
                emotion="neutral",
                subtext_tags=[],
                summary=f"Error processing input: {e}",
                raw={"error": str(e)},
            )

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
        insights: List[str] = []
        if context.intent and context.intent != "unknown":
            insights.append(f"Dominant intent appears to be '{context.intent}'.")
        if context.emotion and context.emotion != "neutral":
            insights.append(f"Prevailing emotion is '{context.emotion}'.")
        if context.subtext_tags:
            insights.append("Subtext cues detected: " + ", ".join(context.subtext_tags))

        # Store insights in context object
        context.summary = "\n".join([response_summary] + insights)

        return context

    def get_history(self) -> List[Dict[str, Any]]:
        """
        Retrieve full conversation history from memory.
        Returns list of message dicts.
        """
        return self.memory.get_all()

    def get_last_message(self, role: Optional[str] = None) -> Optional[Dict[str, Any]]:
        """
        Retrieve the most recent message.
        Optionally filter by role ('user' or 'ccb').
        """
        return self.memory.get_last(role)

    def get_insights(self) -> List[str]:
        """
        Retrieve insights from the most recent turn.
        """
        last_output = self.chain_builder.get_last_turn()
        if not last_output:
            return []
        insights: List[str] = []
        if last_output.intent and last_output.intent != "unknown":
            insights.append(f"Dominant intent: {last_output.intent}")
        if last_output.emotion and last_output.emotion != "neutral":
            insights.append(f"Emotion detected: {last_output.emotion}")
        if last_output.subtext_tags:
            insights.append("Subtext cues: " + ", ".join(last_output.subtext_tags))
        return insights
