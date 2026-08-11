import json
import re


def clean_text(value) -> str:
    text = re.sub(r"\s+", " ", str(value or "")).strip()
    return text or "MISSING"


def clean_confidence(value) -> float:
    try:
        return min(1.0, max(0.0, float(value)))
    except (TypeError, ValueError):
        return 0.0


def clean_json(text: str) -> str:
    text = re.sub(r"```json\s*", "", text, flags=re.IGNORECASE)
    text = re.sub(r"```\s*", "", text)
    return text.strip()


def parse_prediction(text: str) -> dict:
    try:
        data = json.loads(clean_json(text))
    except (json.JSONDecodeError, TypeError):
        data = {}

    return {
        "verbatimDate": clean_text(data.get("verbatimDate")),
        "verbatimDate_confidence": clean_confidence(data.get("verbatimDate_confidence")),
        "verbatimLocality": clean_text(data.get("verbatimLocality")),
        "verbatimLocality_confidence": clean_confidence(data.get("verbatimLocality_confidence")),
    }
