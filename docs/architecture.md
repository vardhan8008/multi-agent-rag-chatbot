# Architecture

## System overview

```
                ┌──────────────────┐
                │   Streamlit UI   │   upload + chat (port 8501)
                └────────┬─────────┘
                         │ HTTP (JSON / multipart)
                ┌────────▼─────────┐
                │   FastAPI app    │   /upload  /chat  /history  /sessions
                └───┬──────────┬───┘
        index path  │          │  chat path
            ┌───────▼───┐  ┌───▼────────────────┐
            │  loader   │  │  LangGraph runtime │
            │ (chunk)   │  │  + MemorySaver     │
            └─────┬─────┘  └───┬────────────────┘
                  │            │
            ┌─────▼────────────▼─────┐
            │      Chroma store      │   local, persisted to ./data/chroma
            │  (HuggingFace embeds)  │
            └────────────────────────┘
```

## Ingestion pipeline

1. **Upload** — file saved to `data/uploads`.
2. **Load** — `loader.py` extracts text (`pypdf` for PDFs, plain read for txt/md).
3. **Chunk** — `RecursiveCharacterTextSplitter`, 1000 chars with 150 overlap.
4. **Embed + store** — each chunk embedded locally with `all-MiniLM-L6-v2`
   and written to Chroma with `{source, chunk}` metadata.

## LangGraph flow

The chat request runs through a compiled `StateGraph`. State is a `TypedDict`
with `messages` (reduced by `add_messages`), `question`, `route`, `context`
and `sources`.

```
            ┌───────────┐
   START ──▶│  analyze  │   router agent: retrieve vs chat + query rewrite
            └─────┬─────┘
       route=chat │ route=retrieve
        ┌─────────┴──────────┐
        ▼                    ▼
   ┌─────────┐         ┌───────────┐
   │  chat   │         │ retrieve  │   pull top-k chunks from Chroma
   └────┬────┘         └─────┬─────┘
        │                    ▼
        │              ┌───────────┐
        │              │ generate  │   grounded answer + citations
        │              └─────┬─────┘
        ▼                    ▼
       END                  END
```

### Agents (nodes)

| Node       | Role                                                                                                                     |
| ---------- | ------------------------------------------------------------------------------------------------------------------------ |
| `analyze`  | Router. Classifies the message (`retrieve`/`chat`) and rewrites follow-ups into a standalone query using recent history. |
| `retrieve` | Similarity search over Chroma; builds the context block + source list.                                                   |
| `generate` | Produces a grounded answer from context + history, with inline citations.                                                |
| `chat`     | Handles greetings / small talk without touching the vector store.                                                        |

### Why a router?

Not every message needs retrieval ("hi", "thanks", "what can you do?").
Routing avoids unnecessary vector lookups and keeps small talk snappy. It also
solves the classic follow-up problem: a question like _"and who wrote it?"_ is
rewritten to _"who wrote <topic from previous turn>?"_ before searching.

## Memory model

Memory is handled by LangGraph's `MemorySaver` checkpointer. Each API call
passes `thread_id = session_id`, so the graph reloads that session's message
history before running and saves it after. This gives:

- **Multi-turn context** — previous turns are fed to `generate`/`chat`.
- **Follow-up resolution** — `analyze` reads history to rewrite queries.
- **Isolation** — different `session_id`s never see each other's history.

`app/memory.py` keeps a small registry of session ids purely so the API/UI can
list existing sessions (the checkpointer doesn't expose that directly).

## Persistence

- **Vectors** → `data/chroma` (survives restarts).
- **Uploaded files** → `data/uploads`.
- **Conversation memory** → in-process (MemorySaver). Resets on server restart;
  swappable for a SQLite/Postgres checkpointer if durability is needed.
