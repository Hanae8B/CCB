# summarizer.py
from typing import List, Optional
from dataclasses import dataclass


@dataclass
class SummaryConfig:
    """Config for summarization behavior."""
    max_turns: int = 12
    include_emotions: bool = True
    include_intents: bool = True
    include_subtext: bool = True
    bullet_style: str = "-"  # choose '-', '*', or '•'


class Summarizer:
    """
    Stable, deterministic summarizer for conversation state.
    Produces a short, structured summary from a list of turns.
    """

    def __init__(self, config: Optional[SummaryConfig] = None):
        self.config = config or SummaryConfig()

    def summarize(self, turns: List) -> str:
        if not turns:
            return "No conversation yet."

        # select last N turns
        recent = turns[-self.config.max_turns :]

        lines = []
        lines.append("Conversation summary:")
        for i, t in enumerate(recent, 1):
            parts = [f"{self.config.bullet_style} Turn {i}: {t.user_text.strip()}"]
            if self.config.include_intents and t.intent:
                parts.append(f"(intent: {t.intent})")
            if self.config.include_emotions and t.emotion:
                parts.append(f"(emotion: {t.emotion})")
            if self.config.include_subtext and getattr(t, "subtext_tags", None):
                tags = ", ".join(t.subtext_tags)
                if tags:
                    parts.append(f"(subtext: {tags})")
            lines.append(" ".join(parts))

        # simple insight extraction
        insights = self._extract_insights(recent)
        if insights:
            lines.append("")
            lines.append("Key insights:")
            for k in insights:
                lines.append(f"{self.config.bullet_style} {k}")

        return "\n".join(lines)

    def _extract_insights(self, recent_turns: List) -> List[str]:
        insights = []
        # intent trend
        intents = [t.intent for t in recent_turns if t.intent]
        if intents:
            common_intent = self._most_common(intents)
            insights.append(f"Dominant intent appears to be '{common_intent}'.")
        # emotion trend
        emotions = [t.emotion for t in recent_turns if t.emotion]
        if emotions:
            common_emotion = self._most_common(emotions)
            insights.append(f"Prevailing emotion is '{common_emotion}'.")
        # subtext presence
        tag_count = sum(len(getattr(t, "subtext_tags", []) or []) for t in recent_turns)
        if tag_count > 0:
            insights.append("Subtext cues appear across multiple turns.")
        return insights

    @staticmethod
    def _most_common(items: List[str]) -> str:
        counts = {}
        for it in items:
            counts[it] = counts.get(it, 0) + 1
        return max(counts.items(), key=lambda kv: kv[1])[0]
