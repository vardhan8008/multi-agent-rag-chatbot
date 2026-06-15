from functools import lru_cache
from typing import List

from chromadb.errors import InvalidDimensionException
from langchain_chroma import Chroma
from langchain_core.documents import Document

from app.config import get_settings
from app.rag.llm import get_embeddings

COLLECTION_NAME = "documents"


@lru_cache
def get_store() -> Chroma:
    settings = get_settings()
    return Chroma(
        collection_name=COLLECTION_NAME,
        embedding_function=get_embeddings(),
        persist_directory=settings.chroma_dir,
    )


def _reset_store() -> Chroma:
    store = get_store()
    try:
        store.delete_collection()
    except Exception:
        pass
    get_store.cache_clear()
    return get_store()


def add_documents(docs: List[Document]) -> int:
    try:
        get_store().add_documents(docs)
    except InvalidDimensionException:
        _reset_store().add_documents(docs)
    return len(docs)


def search(query: str) -> List[Document]:
    settings = get_settings()
    try:
        return get_store().similarity_search(query, k=settings.top_k)
    except InvalidDimensionException:
        return _reset_store().similarity_search(query, k=settings.top_k)


def count() -> int:
    return get_store()._collection.count()

 