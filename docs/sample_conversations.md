# Sample Conversations

These walk through the behaviours to highlight in the demo video: retrieval,
multi-turn memory, follow-up resolution and routing. Upload
[sample_doc.md](sample_doc.md) first.

---

## 1. Retrieval + grounded answer

> **You:** What is Northwind's return policy?
>
> **Assistant:** Northwind accepts returns within 30 days of delivery for a full
> refund, as long as the item is unused and in its original packaging [1].

`route = retrieve` — the answer is pulled from the document and cited.

---

## 2. Multi-turn memory (follow-up with a pronoun)

> **You:** Who do I contact for support?
>
> **Assistant:** You can reach support at support@northwind.example or via the
> in-app chat, Monday–Friday 9am–6pm CT [1].
>
> **You:** And what's _their_ phone number?
>
> **Assistant:** Support's phone number is +1-555-0100 [1].

The second question has no subject on its own. The `analyze` agent rewrites it
to _"What is Northwind support's phone number?"_ using the previous turn, then
retrieves — that's the memory + follow-up resolution working together.

---

## 3. Context retention across topics

> **You:** What plans are available?
>
> **Assistant:** There are three plans: Free, Pro and Enterprise [1].
>
> **You:** How much is the second one?
>
> **Assistant:** The Pro plan costs $20 per user per month [1].

"the second one" is resolved to **Pro** from the earlier list.

---

## 4. Routing / small talk (no retrieval)

> **You:** hi there
>
> **Assistant:** Hi! Upload a document and ask me anything about it.

`route = chat` — no vector search performed.

---

## 5. Honest "I don't know"

> **You:** What is Northwind's stock price?
>
> **Assistant:** I couldn't find anything about a stock price in the uploaded
> documents, so I can't answer that reliably.

The `generate` agent is instructed not to invent facts that aren't in context.
