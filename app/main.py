import shutil
from pathlib import Path

from fastapi import FastAPI, File, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware

from app import memory
from app.config import get_settings
from app.rag import graph, vectorstore
from app.rag.loader import file_to_documents
from app.schemas import (
    ChatRequest,
    ChatResponse,
    HistoryResponse,
    SessionList,
    Source,
    UploadResponse,
)

app = FastAPI(title="Conversational RAG")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

ALLOWED_EXTENSIONS = {".pdf", ".txt", ".md"}


@app.get("/health")
def health():
    return {"status": "ok", "indexed_chunks": vectorstore.count()}


@app.post("/upload", response_model=UploadResponse)
def upload(file: UploadFile = File(...)):
    suffix = Path(file.filename).suffix.lower()
    if suffix not in ALLOWED_EXTENSIONS:
        raise HTTPException(400, f"Unsupported file type '{suffix}'. Use pdf, txt or md.")

    settings = get_settings()
    destination = Path(settings.upload_dir) / file.filename
    with destination.open("wb") as out:
        shutil.copyfileobj(file.file, out)

    documents = file_to_documents(str(destination))
    added = vectorstore.add_documents(documents)
    return UploadResponse(
        filename=file.filename,
        chunks_added=added,
        message=f"Indexed {added} chunks from {file.filename}.",
    )


@app.post("/chat", response_model=ChatResponse)
def chat(request: ChatRequest):
    if not request.message.strip():
        raise HTTPException(400, "Message cannot be empty.")

    memory.remember(request.session_id)
    result = graph.run_turn(request.session_id, request.message)
    return ChatResponse(
        session_id=request.session_id,
        answer=result["answer"],
        route=result["route"],
        sources=[Source(**source) for source in result["sources"]],
    )


@app.get("/sessions", response_model=SessionList)
def sessions():
    return SessionList(sessions=memory.all_sessions())


@app.get("/sessions/{session_id}/history", response_model=HistoryResponse)
def history(session_id: str):
    turns = graph.get_history(session_id)
    return HistoryResponse(session_id=session_id, turns=turns)

 