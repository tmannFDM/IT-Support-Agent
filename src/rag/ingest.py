from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path

import chromadb

from src.rag.embeddings import embed_texts

POLICY_DOCS_DIR = Path(__file__).resolve().parent / "policy_docs"
CHROMA_DIR = Path(__file__).resolve().parent / ".chroma"
COLLECTION_NAME = "policy_chunks"

_CATEGORY_PATTERN = re.compile(r"^\*\*Policy Category:\*\*\s*(.+?)\s*$", re.MULTILINE)
_HEADER_PATTERN = re.compile(r"^##\s+(.+?)\s*$")


@dataclass(frozen=True)
class PolicyChunk:
    chunk_id: str
    text: str
    policy_category: str
    source_document: str


def parse_policy_category(markdown: str) -> str:
    match = _CATEGORY_PATTERN.search(markdown)
    if not match:
        raise ValueError("Missing required markdown header: Policy Category")
    return match.group(1).strip()


def parse_markdown_headers(markdown: str) -> dict[str, str]:
    return {"policy_category": parse_policy_category(markdown)}


def chunk_policy_markdown(markdown: str, source_document: str) -> list[PolicyChunk]:
    headers = parse_markdown_headers(markdown)
    policy_category = headers["policy_category"]

    chunks: list[PolicyChunk] = []
    section_title = "General"
    paragraph_lines: list[str] = []

    def flush_paragraph() -> None:
        if not paragraph_lines:
            return
        paragraph_text = " ".join(line.strip() for line in paragraph_lines if line.strip()).strip()
        paragraph_lines.clear()
        if not paragraph_text:
            return

        chunk_text = f"{section_title}: {paragraph_text}" if section_title else paragraph_text
        chunk_id = f"{source_document}:{len(chunks) + 1}"
        chunks.append(
            PolicyChunk(
                chunk_id=chunk_id,
                text=chunk_text,
                policy_category=policy_category,
                source_document=source_document,
            )
        )

    for raw_line in markdown.splitlines():
        line = raw_line.strip()

        header_match = _HEADER_PATTERN.match(line)
        if header_match:
            flush_paragraph()
            section_title = header_match.group(1).strip()
            continue

        if line.startswith("#"):
            continue

        if line.startswith("**") and line.endswith("**") and ":" in line:
            continue

        if not line:
            flush_paragraph()
            continue

        paragraph_lines.append(line)

    flush_paragraph()
    return chunks


def load_policy_chunks(policy_docs_dir: Path = POLICY_DOCS_DIR) -> list[PolicyChunk]:
    chunks: list[PolicyChunk] = []

    for policy_file in sorted(policy_docs_dir.glob("*.md")):
        markdown = policy_file.read_text(encoding="utf-8")
        chunks.extend(chunk_policy_markdown(markdown, policy_file.name))

    return chunks


def get_chroma_collection(chroma_dir: Path = CHROMA_DIR):
    chroma_dir.mkdir(parents=True, exist_ok=True)
    client = chromadb.PersistentClient(path=str(chroma_dir))
    return client.get_or_create_collection(
        name=COLLECTION_NAME,
        metadata={"hnsw:space": "cosine"},
    )


def upsert_policy_chunks(chunks: list[PolicyChunk]) -> int:
    if not chunks:
        return 0

    collection = get_chroma_collection()
    documents = [chunk.text for chunk in chunks]
    embeddings = embed_texts(documents)

    collection.upsert(
        ids=[chunk.chunk_id for chunk in chunks],
        documents=documents,
        embeddings=embeddings,
        metadatas=[
            {
                "policy_category": chunk.policy_category,
                "source_document": chunk.source_document,
            }
            for chunk in chunks
        ],
    )
    return len(chunks)


def ingest_policy_documents() -> int:
    chunks = load_policy_chunks()
    return upsert_policy_chunks(chunks)
