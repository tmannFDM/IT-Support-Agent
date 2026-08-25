from __future__ import annotations

from dataclasses import dataclass
from threading import Lock

from src.rag.embeddings import embed_texts
from src.rag.ingest import get_chroma_collection, load_policy_chunks, upsert_policy_chunks

_INDEX_READY = False
_INDEX_LOCK = Lock()


@dataclass(frozen=True)
class RetrievalResultItem:
    chunk_id: str
    text: str
    score: float
    policy_category: str
    source_document: str


@dataclass(frozen=True)
class RetrievalResultSet:
    query: str
    items: list[RetrievalResultItem]
    threshold: float
    above_threshold_items: list[RetrievalResultItem]


def ensure_policy_index() -> None:
    global _INDEX_READY
    if _INDEX_READY:
        return

    with _INDEX_LOCK:
        if _INDEX_READY:
            return
        upsert_policy_chunks(load_policy_chunks())
        _INDEX_READY = True


def retrieve_policy_chunks(query: str, top_k: int = 3, threshold: float = 0.35) -> RetrievalResultSet:
    ensure_policy_index()

    collection = get_chroma_collection()
    query_vector = embed_texts([query])[0]
    result = collection.query(
        query_embeddings=[query_vector],
        n_results=top_k,
        include=["documents", "metadatas", "distances"],
    )

    documents = result.get("documents", [[]])[0]
    metadatas = result.get("metadatas", [[]])[0]
    distances = result.get("distances", [[]])[0]
    ids = result.get("ids", [[]])[0]

    items: list[RetrievalResultItem] = []
    for chunk_id, text, metadata, distance in zip(ids, documents, metadatas, distances):
        similarity_score = max(0.0, 1.0 - float(distance))
        items.append(
            RetrievalResultItem(
                chunk_id=str(chunk_id),
                text=str(text),
                score=similarity_score,
                policy_category=str((metadata or {}).get("policy_category", "")),
                source_document=str((metadata or {}).get("source_document", "")),
            )
        )

    above_threshold = [item for item in items if item.score >= threshold]
    return RetrievalResultSet(
        query=query,
        items=items,
        threshold=threshold,
        above_threshold_items=above_threshold,
    )
