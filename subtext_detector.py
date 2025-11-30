# subtext_detector.py
"""
Subtext Detector

Responsibilities:
- Detect subtext cues (hedging, sarcasm, uncertainty, emphasis, politeness, exaggeration, etc.)
- Return structured tags with optional confidence scores and rationale
- Provide extensibility for new cues
- Handle empty or invalid input gracefully
"""

from typing import List, Dict, Any


class SubtextDetector:
    """
    Heuristic detector for subtext cues.
    Returns a list of tags that might apply to the message.

    Features:
    - Detects hedging, uncertainty, sarcasm, negation, emphasis
    - Confidence scoring based on cue frequency
    - Rationale explanation for transparency
    - Extensible cue sets
    """

    # -----------------------------
    # Cue Definitions
    # -----------------------------
    HEDGING_CUES = [
        "maybe", "perhaps", "kind of", "sort of", "i guess", "i think", "probably",
        "possibly", "could be", "might", "seems like"
    ]
    UNCERTAINTY_CUES = [
        "not sure", "unsure", "confused", "uncertain", "don’t know", "don't know",
        "no idea", "lost", "unclear"
    ]
    SARCASM_CUES = [
        "yeah right", "as if", "sure", "totally", "great", "amazing",
        "fantastic", "wonderful", "brilliant"
    ]
    NEGATION_CUES = [
        "not", "never", "no", "none", "nothing", "cannot", "can't", "won't"
    ]
    EMPHASIS_CUES = [
        "!", "all caps", "literally", "absolutely", "completely", "extremely"
    ]
    POLITENESS_CUES = [
        "please", "thank you", "thanks", "appreciate", "grateful"
    ]
    EXAGGERATION_CUES = [
        "always", "never", "everyone", "nobody", "forever", "completely", "totally"
    ]

    # -----------------------------
    # Detection
    # -----------------------------
    def detect(self, text: str) -> List[str]:
        """
        Return a list of subtext tags detected in the text.
        """
        if not text or not text.strip():
            return []

        t = text.lower()
        tags: List[str] = []

        if any(cue in t for cue in self.HEDGING_CUES):
            tags.append("hedging")
        if any(cue in t for cue in self.UNCERTAINTY_CUES):
            tags.append("uncertainty")

        # naive sarcasm: positive word + negative context
        positive_hit = any(cue in t for cue in self.SARCASM_CUES)
        negation_hit = any(cue in t for cue in self.NEGATION_CUES)
        if positive_hit and negation_hit:
            tags.append("possible_sarcasm")

        # emphasis cues
        if "!" in text or "all caps" in t or any(word.isupper() and len(word) > 2 for word in text.split()):
            tags.append("emphasis")
        if any(cue in t for cue in self.EMPHASIS_CUES):
            tags.append("emphasis")

        # politeness cues
        if any(cue in t for cue in self.POLITENESS_CUES):
            tags.append("politeness")

        # exaggeration cues
        if any(cue in t for cue in self.EXAGGERATION_CUES):
            tags.append("exaggeration")

        return list(set(tags))  # ensure uniqueness

    def detect_with_confidence(self, text: str) -> Dict[str, float]:
        """
        Return subtext tags with confidence scores (0–1).
        Confidence is based on cue frequency relative to text length.
        """
        if not text or not text.strip():
            return {}

        t = text.lower()
        words = t.split()
        scores: Dict[str, float] = {}

        def score_for(cues: List[str], tag: str) -> None:
            hits = sum(1 for cue in cues if cue in t)
            if hits > 0:
                scores[tag] = min(1.0, hits / max(1, len(words)))

        score_for(self.HEDGING_CUES, "hedging")
        score_for(self.UNCERTAINTY_CUES, "uncertainty")
        score_for(self.SARCASM_CUES, "sarcasm")
        score_for(self.NEGATION_CUES, "negation")
        score_for(self.EMPHASIS_CUES, "emphasis")
        score_for(self.POLITENESS_CUES, "politeness")
        score_for(self.EXAGGERATION_CUES, "exaggeration")

        return scores

    def explain(self, text: str) -> Dict[str, Any]:
        """
        Provide detailed explanation of detected subtext:
        - Tags
        - Confidence scores
        - Rationale
        """
        tags = self.detect(text)
        scores = self.detect_with_confidence(text)
        rationale = [f"Detected {tag} due to cues" for tag in tags]

        return {
            "text": text,
            "tags": tags,
            "scores": scores,
            "rationale": rationale,
        }

    # -----------------------------
    # Extensibility
    # -----------------------------
    def add_cues(self, category: str, cues: List[str]) -> None:
        """
        Dynamically add new cues to a category.
        """
        if hasattr(self, category.upper() + "_CUES"):
            getattr(self, category.upper() + "_CUES").extend(cues)
        else:
            print(f"Unknown cue category: {category}")

    def list_categories(self) -> List[str]:
        """
        List all available cue categories.
        """
        return [
            "hedging", "uncertainty", "sarcasm",
            "negation", "emphasis", "politeness", "exaggeration"
        ]
