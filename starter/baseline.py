"""Keyword baseline. It works, and it's meant to be beaten.

Usage: python starter/baseline.py > predictions.jsonl
"""
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

RULES = [
    ("spam_irrelevant", r"\b(crypto|lottery|investment|earn \d+|click here|seo services|follow back)\b"),
    ("payment_issue", r"\b(payment|paid|debited|deducted|upi|refund not|charged twice|emi|cod)\b"),
    ("return_refund", r"\b(return|refund|exchange|replace|replacement|wapas)\b"),
    ("order_status", r"\b(where is|order status|track|tracking|delivery|dispatch|kab aayega|delivered)\b"),
    ("complaint_escalation", r"\b(worst|fraud|cheat|consumer court|legal|disgusting|never again|pathetic)\b"),
    ("product_question", r"\b(size|colour|color|material|ingredients|available|stock|does it|kya ye)\b"),
]
HUMAN = r"\b(consumer court|legal|lawyer|police|allerg|burn|rash|third time|3rd time|twitter|instagram post|fraud)\b"


def classify(text: str) -> dict:
    t = text.lower()
    queue = "product_question"
    for name, pattern in RULES:
        if re.search(pattern, t):
            queue = name
            break
    return {"queue": queue, "needs_human": bool(re.search(HUMAN, t))}


def main():
    for line in (ROOT / "data" / "messages.jsonl").read_text().splitlines():
        if not line.strip():
            continue
        m = json.loads(line)
        print(json.dumps({"id": m["id"], **classify(m["text"])}))


if __name__ == "__main__":
    main()
