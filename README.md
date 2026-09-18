# joinstartup sandbox — Ship it like it's live

You're building a support-triage assistant for **Kaapi & Co.**, a fictional 20-person D2C coffee brand in India.
They get ~300 customer messages a day on WhatsApp, email and Instagram — English, Hinglish and Hindi.

**You have 72 hours from `start`.** Not from receiving this.

## The job

For every message in `data/messages.jsonl`, decide:

- **queue** — one of:
  - `order_status` — where is my order, delivery timing, tracking
  - `return_refund` — return, exchange, replacement, refund request
  - `payment_issue` — payment failed, double charge, UPI/COD problems, refund not received after approval
  - `product_question` — sizes, grind, ingredients, stock, how to use
  - `complaint_escalation` — angry, unresolved, repeated, or reputational complaints
  - `spam_irrelevant` — promotions, scams, off-topic
- **needs_human** — `true` if a person must see it now: abusive or threatening language, legal or consumer-court
  threats, health or safety issues (allergic reaction, burns), someone contacting for the 3rd+ time,
  or a public-post / press threat.

Then build it like it's going live: draft replies, handle failure, and tell us what you'd watch after launch.

## Deliverables

1. **Your repo** (created from this template) with a working tool — any structure you like.
2. **`predictions.jsonl`** graded at least once: one line per message, `{"id": "m001", "queue": "...", "needs_human": false}`.
3. **Failure handling.** Our AI gateway behaves like a real provider: it is sometimes overloaded, sometimes slow,
   and sometimes returns broken output. Your tool should survive that. We can see how it does.
4. **`WEEK2.md`** (one page) — it's two weeks after launch: what do you watch, what tells you it's getting worse,
   and what would you change after listening to 5 support agents?
5. **A 5-minute video walkthrough** (Loom, Drive, YouTube unlisted — any link).

## How to start

1. Click **Use this template → Create a new repository** (public), then **Code → Codespaces → Create codespace**.
2. In the terminal:
   ```bash
   python -m sandbox login <your token from Meena>
   python -m sandbox status
   python -m sandbox start        # the 72-hour clock starts here
   eval "$(python -m sandbox env)"
   python starter/baseline.py > predictions.jsonl
   python -m sandbox grade predictions.jsonl
   ```
3. When done:
   ```bash
   python -m sandbox submit --repo https://github.com/<you>/<repo> --video <link> --note https://github.com/<you>/<repo>/blob/main/WEEK2.md
   ```

## Rules, so there are no surprises

- **AI assistants are allowed.** Use whatever helps. AI calls your *tool* makes go through our gateway
  (`claude-haiku-4-5`, $5 budget, no streaming) and are logged.
- **The grader shows half the answer key.** Every `grade` scores you against a public half. Your final score
  uses a hidden half. Tuning to the public score won't help — building something that generalises will.
- **40 grade runs, 30 seconds apart.** Commit before you grade — each run records your commit.
- **We read the code**, the commit history, how your tool behaved when the gateway failed, and `WEEK2.md`.
  Honest numbers beat high numbers.
- After `submit`, your token stops working for grading and AI calls.

Questions: reply to Meena's email.
