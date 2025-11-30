# config.py
from typing import Dict


DEFAULTS: Dict[str, object] = {
    "intent_conf_threshold": 0.6,
    "emotion_conf_threshold": 0.55,
    "subtext_conf_threshold": 0.55,
    "summary_max_points": 10,
    "summary_max_recent": 6,
    "model_provider": "mock",
    "model_temperature": 0.7,
    "max_tokens": 512,
}
