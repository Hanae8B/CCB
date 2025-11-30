# router.py
from schema import RouterDecision, IntentResult, SubtextResult


class Router:
    """
    Determines an ordered list of modules to run based on intent and subtext.
    """

    def decide(self, intent: IntentResult, subtext: SubtextResult) -> RouterDecision:
        route = ["intent_analyzer", "tone_emotion_detector", "subtext_inferencer", "conversation_state_machine", "summarizer"]

        if intent.intent in ("math", "code"):
            route.append("model_interface")

        if subtext.primary in ("seeking_empathy",):
            # prioritize emotion-aware response
            route = ["tone_emotion_detector", "intent_analyzer", "subtext_inferencer", "conversation_state_machine", "summarizer"]

        return RouterDecision(route=route, rationale=f"Intent={intent.intent}; Subtext={subtext.primary}")
