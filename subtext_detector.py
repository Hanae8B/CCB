# subtext_detector.py
from typing import List


class SubtextDetector:
    """
    Heuristic detector for subtext cues (hedging, sarcasm, uncertainty).
    Returns a list of tags that might apply to the message.
    """

    HEDGING_CUES = [
        "maybe", "perhaps", "kind of", "sort of", "i guess", "i think", "probably",
    ]
    UNCERTAINTY_CUES = [
        "not sure", "unsure", "confused", "uncertain", "don’t know", "don't know",
    ]
    SARCASM_CUES = [
        "yeah right", "as if", "sure", "totally", "great", "amazing",
    ]
    NEGATION_CUES = [
        "not", "never", "no", "none", "nothing",
    ]

    def detect(self, text: str) -> List[str]:
        if not text or not text.strip():
            return []

        t = text.lower()
        tags = []

        if any(cue in t for cue in self.HEDGING_CUES):
            tags.append("hedging")
        if any(cue in t for cue in self.UNCERTAINTY_CUES):
            tags.append("uncertainty")

        # naive sarcasm: positive word + negative context
        positive_hit = any(cue in t for cue in self.SARCASM_CUES)
        negation_hit = any(cue in t for cue in self.NEGATION_CUES)
        if positive_hit and negation_hit:
            tags.append("possible_sarcasm")

        # intensifiers / emphasis
        if "!" in text or "all caps" in t or any(word.isupper() and len(word) > 2 for word in text.split()):
            tags.append("emphasis")

        return tags
