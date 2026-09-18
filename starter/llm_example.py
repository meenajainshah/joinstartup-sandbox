"""One LLM call through the sandbox gateway.

It does NOT retry, validate, or handle failures. That part is yours.

Usage:
  eval "$(python -m sandbox env)"
  python starter/llm_example.py "mera order abhi tak nahi aaya, 10 din ho gaye"
"""
import sys

import anthropic

QUEUES = "order_status, return_refund, payment_issue, product_question, complaint_escalation, spam_irrelevant"

client = anthropic.Anthropic()  # reads ANTHROPIC_BASE_URL and ANTHROPIC_API_KEY
text = sys.argv[1] if len(sys.argv) > 1 else "where is my order?"

resp = client.messages.create(
    model="claude-haiku-4-5",
    max_tokens=200,
    messages=[{
        "role": "user",
        "content": f"Classify this customer message into one of: {QUEUES}. "
                   f'Reply as JSON: {{"queue": "...", "needs_human": true|false}}.\n\nMessage: {text}',
    }],
)
print(resp.content[0].text)
