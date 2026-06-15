# Demo Video Script (~5 minutes)

A natural, spoken-style script. Read it like you're talking, not reciting.
Timings are rough — aim for 5–6 minutes. `[ACTION]` lines are what to do on
screen, the rest is what to say.

---

## 0:00 — Intro (30s)

> "Hi, I'm [your name]. This is my Conversational RAG system — basically a
> chatbot you can talk to about your own documents, and it actually remembers
> the conversation as you go.
>
> The stack is LangGraph for the orchestration, FastAPI for the backend, a
> Streamlit UI on top, and Chroma as the vector database. For the model I'm
> using an open-source Llama running on Groq, and the embeddings run locally —
> so the only thing you need is one free API key. Let me walk you through it."

---

## 0:30 — Architecture (1 min)

`[ACTION] Open docs/architecture.md and show the diagram]`

> "Quick look at the architecture. The flow is: the Streamlit UI sends a request
> to FastAPI. FastAPI hands it to a LangGraph graph, and that's where the
> interesting part happens.
>
> When you upload a document, it gets read, split into chunks, embedded, and
> stored in Chroma. When you ask a question, the graph kicks in.
>
> The graph has a few small agents. First there's a **router** — it looks at
> your message and decides: do we actually need to search the documents, or is
> this just small talk like 'hi' or 'thanks'? If it needs the documents, it goes
> to the **retriever**, which pulls the most relevant chunks from Chroma, and
> then the **generator**, which writes the answer grounded in those chunks and
> cites its sources. If it's just chit-chat, it skips retrieval entirely.
>
> And the memory — this is the key bit — is handled by LangGraph's checkpointer.
> Every conversation has a session ID, and the graph automatically saves and
> restores the history for that session. That's what makes it multi-turn."

---

## 1:30 — Folder structure (45s)

`[ACTION] Open the file explorer / VS Code tree]`

> "Folder structure is pretty clean. Everything lives under `app`.
>
> - `main.py` is the FastAPI app — all the routes: upload, chat, history.
> - `config.py` reads settings from the environment.
> - And then the `rag` package is the brains: `loader.py` reads and chunks
>   documents, `llm.py` sets up the model and embeddings, `vectorstore.py`
>   wraps Chroma, and `graph.py` is the LangGraph orchestration with all the
>   agents.
> - `ui` has the Streamlit app, `docs` has the architecture, API reference and
>   sample conversations, and there's a Dockerfile and docker-compose so the
>   whole thing runs with one command."

---

## 2:15 — Document upload (45s)

`[ACTION] Switch to the Streamlit UI. Upload docs/sample_doc.md, click Index]`

> "Okay, let's actually use it. On the left I'll upload a document — this is a
> little handbook for a fake company called Northwind. I'll click 'Index
> document'…
>
> …and there we go — it tells me how many chunks it indexed. Behind the scenes
> it just read the file, split it into overlapping chunks, embedded each one
> locally, and stored them in Chroma. The status line at the top now shows the
> chunk count."

---

## 3:00 — Retrieval (45s)

`[ACTION] Ask: "What is Northwind's return policy?"]`

> "Now I'll ask something that's actually in the document — 'What is Northwind's
> return policy?'
>
> …And it comes back with the 30-day return policy, and notice it gives me a
> **Sources** dropdown — so I can see exactly which chunk it pulled the answer
> from. That's the retrieval working: it searched the vector store, found the
> relevant passage, and the model answered from that instead of making something
> up."

---

## 3:45 — Multi-turn chat + memory (1 min)

`[ACTION] Ask: "Who do I contact for support?"]`
`[ACTION] Then ask the follow-up: "And what's their phone number?"]`

> "Here's the part I'm most happy with. I'll ask 'Who do I contact for support?'
> — it gives me the email and hours.
>
> Now watch this follow-up: I'm going to say 'And what's _their_ phone number?'
> — notice I never said who 'their' is. A normal search would have no idea what
> that means.
>
> …But it answers correctly with the support phone number. That's because the
> router agent looked at the previous turn, figured out 'their' means Northwind
> support, and rewrote my question into a proper standalone search query before
> retrieving. So it's combining the memory with the retrieval — that's the whole
> point of the system."

`[ACTION] Optionally click "New conversation"]`

> "And if I start a new conversation, the memory resets — this session won't see
> the previous one's history. Each session is isolated by its ID."

---

## 4:45 — Wrap up (30s)

> "So to recap: it's a full RAG pipeline, orchestrated with LangGraph using a
> router, retriever and generator agent, with proper session memory, a FastAPI
> backend, Chroma for vectors, and a Streamlit UI — all running on free,
> open-source models and fully dockerised.
>
> The repo has the README, setup guide, architecture diagrams, API docs and
> sample conversations. Thanks for watching!"

---

## Tips while recording

- Have the UI and the API docs (`localhost:8000/docs`) open in tabs beforehand.
- Pre-load the page so the embedding model is already downloaded — that first
  upload is instant then.
- If you want to show the API directly, hit `localhost:8000/docs` and run the
  `/chat` endpoint live for 10 seconds — looks great on camera.
- Speak to the _behaviour_ ("watch what happens when I…") rather than reading
  code line by line. It keeps it engaging.
