from typing import List

from pydantic import BaseModel


class ChatRequest(BaseModel):
    session_id: str
    message: str


class Source(BaseModel):
    source: str
    snippet: str


class ChatResponse(BaseModel):
    session_id: str
    answer: str
    route: str
    sources: List[Source] = []


class UploadResponse(BaseModel):
    filename: str
    chunks_added: int
    message: str


class Turn(BaseModel):
    role: str
    content: str


class HistoryResponse(BaseModel):
    session_id: str
    turns: List[Turn] = []


class SessionList(BaseModel):
    sessions: List[str] = []
 