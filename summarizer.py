# summarizer.py
"""
Summarizer Module

Responsibilities:
- Produce structured, deterministic summaries of conversation turns
- Support multiple output styles (bullet, narrative, json, markdown)
- Extract insights (dominant intent, prevailing emotion, subtext density, question ratio, emphasis)
- Handle edge cases (neutral/None emotions, empty subtext, long text, missing fields)
- Provide configuration validation and runtime updates
"""

from typing import List, Optional, Dict, Any, Tuple
from dataclasses import dataclass, asdict
from datetime import datetime
from utils import contains_emphasis, is_question


# -----------------------------
# Configuration
# -----------------------------
@dataclass
class SummaryConfig:
    """Config for summarization behavior."""
    max_turns: int = 12
    include_emotions: bool = True
    include_intents: bool = True
    include_subtext: bool = True
    include_assistant: bool = False          # include assistant_text in entries if available
    include_timestamps: bool = False         # include per-turn timestamps
    include_meta: bool = False               # include meta dict if present
    bullet_style: str = "-"                  # '-', '*', or '•'
    style: str = "bullet"                    # "bullet", "narrative", "json", "markdown"
    heading: str = "Conversation summary"    # top-level heading/title
    show_indices: bool = True                # number turns (Turn 1, Turn 2, ...)
    show_empty_subtext_as_none: bool = True  # explicitly show '(Subtext: none)' when absent
    max_text_length: int = 200               # truncate long text segments for readability
    truncate_ellipsis: str = "…"             # ellipsis used when truncating

    # Insight controls
    show_insights: bool = True
    omit_neutral_prevailing: bool = False    # if True, skip 'Prevailing emotion is neutral' unless all neutral
    compute_question_ratio: bool = True
    compute_emphasis_count: bool = True
    compute_subtext_density: bool = True
    compute_intent_distribution: bool = True


# -----------------------------
# Summarizer
# -----------------------------
class Summarizer:
    """
    Deterministic, configurable summarizer for conversation state.

    Features:
    - Multiple summary styles (bullet, narrative, JSON, markdown)
    - Robust formatting with truncation and safe field access
    - Insight extraction (trends and ratios)
    - Config validation and dynamic updates
    """

    def __init__(self, config: Optional[SummaryConfig] = None):
        self.config = config or SummaryConfig()
        self._validate_config()

    # Public API
    def summarize(self, turns: List) -> str:
        """
        Summarize a list of turns according to configuration.
        Each turn is expected to expose:
          - user_text: str
          - intent: Optional[str]
          - emotion: Optional[str]
          - subtext_tags: Optional[List[str]]
          - assistant_text: Optional[str]
          - timestamp: Optional[float]
          - meta: Optional[Dict[str, Any]]
        """
        if not turns:
            return "No conversation yet."

        recent = turns[-self.config.max_turns:]
        style = (self.config.style or "bullet").lower()

        if style == "bullet":
            return self._summarize_bullet(recent)
        if style == "narrative":
            return self._summarize_narrative(recent)
        if style == "json":
            return self._summarize_json(recent)
        if style == "markdown":
            return self._summarize_markdown(recent)

        # Fallback
        return self._summarize_bullet(recent)

    def reset(self) -> None:
        """Reset summarizer configuration to defaults."""
        self.config = SummaryConfig()
        self._validate_config()

    def update_config(self, **kwargs) -> None:
        """Update summarizer configuration dynamically."""
        for k, v in kwargs.items():
            if hasattr(self.config, k):
                setattr(self.config, k, v)
        self._validate_config()

    def to_config_dict(self) -> Dict[str, Any]:
        """Export current configuration as dict."""
        return asdict(self.config)

    # -----------------------------
    # Styles
    # -----------------------------
    def _summarize_bullet(self, recent: List) -> str:
        lines: List[str] = [f"{self.config.heading}:"]
        for i, t in enumerate(recent, 1):
            parts: List[str] = []
            index = f" Turn {i}:" if self.config.show_indices else ""
            parts.append(f"{self.config.bullet_style}{index} {self._fmt_user_text(t)}")

            if self.config.include_assistant and getattr(t, "assistant_text", None):
                parts.append(f"(Assistant: {self._truncate(getattr(t, 'assistant_text', '') or '')})")

            if self.config.include_intents:
                intent = getattr(t, "intent", None)
                if intent:
                    parts.append(f"(Intent: {intent})")

            if self.config.include_emotions:
                emotion = getattr(t, "emotion", None) or "neutral"
                parts.append(f"(Emotion: {emotion})")

            if self.config.include_subtext:
                tags = getattr(t, "subtext_tags", None) or []
                tag_str = ", ".join(tags) if tags else ("none" if self.config.show_empty_subtext_as_none else "")
                if tag_str:
                    parts.append(f"(Subtext: {tag_str})")

            if self.config.include_timestamps and getattr(t, "timestamp", None):
                parts.append(f"(Time: {self._fmt_timestamp(getattr(t, 'timestamp'))})")

            if self.config.include_meta and getattr(t, "meta", None):
                parts.append(f"(Meta: {self._fmt_meta(getattr(t, 'meta'))})")

            lines.append(" ".join(parts))

        insights = self._extract_insights(recent) if self.config.show_insights else []
        if insights:
            lines.append("")
            lines.append("Key insights:")
            for k in insights:
                lines.append(f"{self.config.bullet_style} {k}")

        return "\n".join(lines)

    def _summarize_narrative(self, recent: List) -> str:
        lines: List[str] = [f"{self.config.heading} (narrative):"]
        for i, t in enumerate(recent, 1):
            sentence = []
            sentence.append(f"Turn {i}: The user said “{self._fmt_user_text(t)}”.")
            if self.config.include_intents and getattr(t, "intent", None):
                sentence.append(f"The intent was {getattr(t, 'intent')}.")
            if self.config.include_emotions:
                emotion = getattr(t, "emotion", None) or "neutral"
                sentence.append(f"The emotion was {emotion}.")
            if self.config.include_subtext:
                tags = getattr(t, "subtext_tags", None) or []
                if tags:
                    sentence.append(f"Subtext cues: {', '.join(tags)}.")
                elif self.config.show_empty_subtext_as_none:
                    sentence.append("No subtext detected.")
            if self.config.include_assistant and getattr(t, "assistant_text", None):
                sentence.append(f"The assistant replied: “{self._truncate(getattr(t, 'assistant_text', '') or '')}”.")
            lines.append(" ".join(sentence))

        insights = self._extract_insights(recent) if self.config.show_insights else []
        if insights:
            lines.append("Overall insights:")
            for k in insights:
                lines.append(f"{self.config.bullet_style} {k}")

        return "\n".join(lines)

    def _summarize_json(self, recent: List) -> str:
        import json
        data: Dict[str, Any] = {
            "heading": self.config.heading,
            "config": self.to_config_dict(),
            "turns": [],
            "insights": self._extract_insights(recent) if self.config.show_insights else [],
        }
        for i, t in enumerate(recent, 1):
            turn_data: Dict[str, Any] = {
                "index": i,
                "user_text": self._fmt_user_text(t),
            }
            if self.config.include_assistant and getattr(t, "assistant_text", None):
                turn_data["assistant_text"] = self._truncate(getattr(t, "assistant_text", "") or "")
            if self.config.include_intents and getattr(t, "intent", None):
                turn_data["intent"] = getattr(t, "intent")
            if self.config.include_emotions:
                turn_data["emotion"] = getattr(t, "emotion", None) or "neutral"
            if self.config.include_subtext:
                turn_data["subtext_tags"] = getattr(t, "subtext_tags", None) or []
            if self.config.include_timestamps and getattr(t, "timestamp", None):
                turn_data["timestamp"] = self._fmt_timestamp(getattr(t, "timestamp"))
            if self.config.include_meta and getattr(t, "meta", None):
                turn_data["meta"] = getattr(t, "meta")
            data["turns"].append(turn_data)
        return json.dumps(data, indent=2, ensure_ascii=False)

    def _summarize_markdown(self, recent: List) -> str:
        # Table header
        cols = ["Turn", "User", "Intent" if self.config.include_intents else None,
                "Emotion" if self.config.include_emotions else None,
                "Subtext" if self.config.include_subtext else None,
                "Assistant" if self.config.include_assistant else None,
                "Time" if self.config.include_timestamps else None]
        cols = [c for c in cols if c is not None]

        lines: List[str] = [f"# {self.config.heading}", "", "|" + "|".join(cols) + "|",
                            "|" + "|".join(["---"] * len(cols)) + "|"]
        for i, t in enumerate(recent, 1):
            row: List[str] = [str(i), self._fmt_user_text(t)]
            if self.config.include_intents:
                row.append(getattr(t, "intent", "") or "")
            if self.config.include_emotions:
                row.append(getattr(t, "emotion", None) or "neutral")
            if self.config.include_subtext:
                tags = getattr(t, "subtext_tags", None) or []
                row.append(", ".join(tags) if tags else ("none" if self.config.show_empty_subtext_as_none else ""))
            if self.config.include_assistant:
                row.append(self._truncate(getattr(t, "assistant_text", "") or ""))
            if self.config.include_timestamps:
                row.append(self._fmt_timestamp(getattr(t, "timestamp", None)))
            lines.append("|" + "|".join(row) + "|")

        if self.config.show_insights:
            lines.append("")
            lines.append("## Key insights")
            for k in self._extract_insights(recent):
                lines.append(f"- {k}")

        return "\n".join(lines)

    # -----------------------------
    # Insight Extraction
    # -----------------------------
    def _extract_insights(self, recent_turns: List) -> List[str]:
        insights: List[str] = []

        # Intent trend
        intents = [getattr(t, "intent", None) for t in recent_turns if getattr(t, "intent", None)]
        if intents:
            common_intent = self._most_common(intents)
            insights.append(f"Dominant intent appears to be '{common_intent}'.")

        # Emotion trend (handle None/neutral properly)
        emotions = [(getattr(t, "emotion", None) or "neutral") for t in recent_turns]
        if emotions:
            common_emotion = self._most_common(emotions)
            all_neutral = all(e == "neutral" for e in emotions)
            if not self.config.omit_neutral_prevailing or all_neutral or common_emotion != "neutral":
                insights.append(f"Prevailing emotion is '{common_emotion}'.")

        # Subtext density
        if self.config.compute_subtext_density:
            tag_count = sum(len(getattr(t, "subtext_tags", []) or []) for t in recent_turns)
            turns_with_subtext = sum(1 for t in recent_turns if getattr(t, "subtext_tags", []) or [])
            if tag_count > 0:
                insights.append(f"Subtext cues present in {turns_with_subtext}/{len(recent_turns)} turns.")

        # Question ratio
        if self.config.compute_question_ratio:
            questions = sum(1 for t in recent_turns if is_question(getattr(t, "user_text", "") or ""))
            if questions > 0:
                insights.append(f"Questions comprise {questions}/{len(recent_turns)} turns.")

        # Emphasis count
        if self.config.compute_emphasis_count:
            emph = sum(1 for t in recent_turns if contains_emphasis(getattr(t, "user_text", "") or ""))
            if emph > 0:
                insights.append(f"Emphasis markers detected in {emph}/{len(recent_turns)} turns.")

        # Intent distribution (top 3)
        if self.config.compute_intent_distribution and intents:
            dist = self._distribution(intents)
            top = sorted(dist.items(), key=lambda kv: kv[1], reverse=True)[:3]
            items = ", ".join(f"{k}: {v}" for k, v in top)
            insights.append(f"Top intents distribution → {items}.")

        return insights

    # -----------------------------
    # Helpers
    # -----------------------------
    @staticmethod
    def _most_common(items: List[str]) -> str:
        counts: Dict[str, int] = {}
        for it in items:
            counts[it] = counts.get(it, 0) + 1
        return max(counts.items(), key=lambda kv: kv[1])[0]

    @staticmethod
    def _distribution(items: List[str]) -> Dict[str, int]:
        dist: Dict[str, int] = {}
        for it in items:
            dist[it] = dist.get(it, 0) + 1
        return dist

    def _fmt_user_text(self, t: Any) -> str:
        text = getattr(t, "user_text", "") or ""
        return self._truncate(text.strip())

    def _truncate(self, s: str) -> str:
        max_len = max(10, int(self.config.max_text_length))
        if len(s) <= max_len:
            return s
        return s[:max_len].rstrip() + self.config.truncate_ellipsis

    @staticmethod
    def _fmt_timestamp(ts: Optional[float]) -> str:
        if ts is None:
            return ""
        try:
            return datetime.utcfromtimestamp(ts).strftime("%Y-%m-%d %H:%M:%S UTC")
        except Exception:
            return str(ts)

    @staticmethod
    def _fmt_meta(meta: Dict[str, Any]) -> str:
        try:
            # compact key:value pairs
            pairs = [f"{k}={meta[k]}" for k in sorted(meta.keys())]
            return "{ " + ", ".join(pairs) + " }"
        except Exception:
            return str(meta)

    def _validate_config(self) -> None:
        # bullet_style validation
        if self.config.bullet_style not in {"-", "*", "•"}:
            self.config.bullet_style = "-"
        # style validation
        if (self.config.style or "").lower() not in {"bullet", "narrative", "json", "markdown"}:
            self.config.style = "bullet"
        # numeric bounds
        if self.config.max_turns <= 0:
            self.config.max_turns = 1
        if self.config.max_text_length < 20:
            self.config.max_text_length = 20
