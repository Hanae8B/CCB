# router.py
"""
Router Module

Responsibilities:
- Determine an ordered list of modules to run based on intent and subtext
- Provide rationale for routing decisions
- Handle special cases (math, code, emotional support, clarification, etc.)
- Support extensibility for new modules and rules
"""

from typing import List, Dict, Any
from schema import RouterDecision, IntentResult, SubtextResult


class Router:
    """
    Determines an ordered list of modules to run based on intent and subtext.

    Features:
    - Default pipeline ordering
    - Special-case routing for math, code, emotional support, clarification
    - Extensible ruleset
    - Transparent rationale
    """

    DEFAULT_ROUTE: List[str] = [
        "intent_analyzer",
        "tone_emotion_detector",
        "subtext_inferencer",
        "conversation_state_machine",
        "summarizer",
    ]

    def __init__(self):
        # Custom routing rules can be added dynamically
        self.custom_rules: Dict[str, List[str]] = {}

    def decide(self, intent: IntentResult, subtext: SubtextResult) -> RouterDecision:
        """
        Decide which modules to run based on intent and subtext.

        Args:
            intent: IntentResult object containing intent and confidence
            subtext: SubtextResult object containing primary and secondary subtext tags

        Returns:
            RouterDecision with route and rationale
        """
        route = list(self.DEFAULT_ROUTE)
        rationale_parts: List[str] = [f"Intent={intent.intent}", f"Subtext={subtext.primary}"]

        # --- Special cases ---
        if intent.intent in ("math", "code"):
            route.append("model_interface")
            rationale_parts.append("Added model_interface for math/code processing")

        if subtext.primary in ("seeking_empathy", "emotional_support"):
            # prioritize emotion-aware response
            route = [
                "tone_emotion_detector",
                "intent_analyzer",
                "subtext_inferencer",
                "conversation_state_machine",
                "summarizer",
            ]
            rationale_parts.append("Prioritized emotion-aware response due to subtext")

        if subtext.primary in ("seeking_clarification",):
            # prioritize clarification handling
            route.insert(0, "clarification_handler")
            rationale_parts.append("Inserted clarification_handler due to subtext")

        if intent.intent in ("closing", "goodbye"):
            # streamline closing pipeline
            route = ["intent_analyzer", "conversation_state_machine", "summarizer"]
            rationale_parts.append("Simplified route for closing intent")

        if intent.intent in self.custom_rules:
            # apply custom rule override
            route = self.custom_rules[intent.intent]
            rationale_parts.append(f"Applied custom rule for intent={intent.intent}")

        rationale = "; ".join(rationale_parts)

        return RouterDecision(route=route, rationale=rationale)

    # -----------------------------
    # Extensibility
    # -----------------------------
    def add_rule(self, intent_name: str, route: List[str]) -> None:
        """
        Add a custom routing rule for a specific intent.
        """
        self.custom_rules[intent_name] = route

    def remove_rule(self, intent_name: str) -> None:
        """
        Remove a custom routing rule.
        """
        if intent_name in self.custom_rules:
            del self.custom_rules[intent_name]

    def list_rules(self) -> Dict[str, List[str]]:
        """
        List all custom routing rules.
        """
        return dict(self.custom_rules)

    def explain(self, intent: IntentResult, subtext: SubtextResult) -> Dict[str, Any]:
        """
        Provide detailed explanation of routing decision.
        """
        decision = self.decide(intent, subtext)
        return {
            "intent": intent.intent,
            "subtext": subtext.primary,
            "route": decision.route,
            "rationale": decision.rationale,
        }
