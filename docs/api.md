# API Reference

Base URL: `http://localhost:8000`

Interactive docs (Swagger): `http://localhost:8000/docs`

---

## GET /health

Liveness check + how many chunks are currently indexed.

**200**

```json
{ "status": "ok", "indexed_chunks": 42 }
```

---

## POST /upload

Upload and index a document. `multipart/form-data` with a `file` field.
Accepts `.pdf`, `.txt`, `.md`.

```bash
curl -F "file=@docs/sample_doc.md" http://localhost:8000/upload
```

**200**

```json
{
  "filename": "sample_doc.md",
  "chunks_added": 6,
  "message": "Indexed 6 chunks from sample_doc.md."
}
```

**400** — unsupported type or no extractable text.

---

## POST /chat

Send a message in a conversation. Reuse the same `session_id` to keep memory.

```bash
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{"session_id": "demo1", "message": "What is this document about?"}'
```

**Request**

```json
{ "session_id": "demo1", "message": "What is this document about?" }
```

**200**

```json
{
  "session_id": "demo1",
  "answer": "The document describes ... [1]",
  "route": "retrieve",
  "sources": [
    { "source": "sample_doc.md", "snippet": "first 200 chars of the chunk..." }
  ]
}
```

`route` is `"retrieve"` when the knowledge base was used, `"chat"` for small talk.

---

## GET /sessions

List known session ids (for the current server process).

**200**

```json
{ "sessions": ["demo1", "a1b2c3d4"] }
```

---

## GET /sessions/{session_id}/history

Full turn-by-turn history for a session.

**200**

```json
{
  "session_id": "demo1",
  "turns": [
    { "role": "user", "content": "What is this document about?" },
    { "role": "assistant", "content": "The document describes ... [1]" }
  ]
}
```
