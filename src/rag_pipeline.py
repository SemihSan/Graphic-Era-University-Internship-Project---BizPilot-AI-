from __future__ import annotations

import argparse
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable

import chromadb
from sentence_transformers import SentenceTransformer


ROOT_DIR = Path(__file__).resolve().parents[1]
COMPANY_DOCS_DIR = ROOT_DIR / "data" / "company_docs"
CHROMA_DIR = ROOT_DIR / "chroma_db"
COLLECTION_NAME = "bizpilot_company_docs"
EMBEDDING_MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2"


@dataclass(frozen=True)
class DocumentChunk:
    chunk_id: str
    text: str
    metadata: dict[str, str | int]


def load_company_documents(docs_dir: Path = COMPANY_DOCS_DIR) -> list[dict[str, str]]:
    documents: list[dict[str, str]] = []

    for path in sorted(docs_dir.glob("*.md")):
        text = path.read_text(encoding="utf-8")
        documents.append(
            {
                "file_name": path.name,
                "source_path": str(path.relative_to(ROOT_DIR)),
                "document_type": extract_metadata_value(text, "Document type") or "unknown",
                "source_id": extract_metadata_value(text, "Source ID") or path.stem,
                "text": text,
            }
        )

    return documents


def extract_metadata_value(text: str, key: str) -> str | None:
    match = re.search(rf"^{re.escape(key)}:\s*(.+)$", text, flags=re.MULTILINE)
    return match.group(1).strip() if match else None


def chunk_text(text: str, max_chars: int = 900, overlap_chars: int = 0) -> list[str]:
    paragraphs = [paragraph.strip() for paragraph in re.split(r"\n\s*\n", text) if paragraph.strip()]
    chunks: list[str] = []
    current = ""

    for paragraph in paragraphs:
        candidate = f"{current}\n\n{paragraph}".strip() if current else paragraph
        if len(candidate) <= max_chars:
            current = candidate
            continue

        if current:
            chunks.append(current)
        current = paragraph

        while len(current) > max_chars:
            chunks.append(current[:max_chars].strip())
            current = current[max_chars - overlap_chars :].strip()

    if current:
        chunks.append(current)

    if overlap_chars <= 0 or len(chunks) <= 1:
        return chunks

    overlapped: list[str] = []
    previous_tail = ""
    for chunk in chunks:
        combined = f"{previous_tail}\n\n{chunk}".strip() if previous_tail else chunk
        overlapped.append(combined)
        previous_tail = chunk[-overlap_chars:]

    return overlapped


def build_chunks(documents: Iterable[dict[str, str]]) -> list[DocumentChunk]:
    chunks: list[DocumentChunk] = []

    for document in documents:
        doc_chunks = chunk_text(document["text"])
        for index, chunk in enumerate(doc_chunks):
            chunk_id = f"{Path(document['file_name']).stem}::chunk_{index:03d}"
            chunks.append(
                DocumentChunk(
                    chunk_id=chunk_id,
                    text=chunk,
                    metadata={
                        "file_name": document["file_name"],
                        "source_path": document["source_path"],
                        "document_type": document["document_type"],
                        "source_id": document["source_id"],
                        "chunk_index": index,
                    },
                )
            )

    return chunks


def load_embedding_model() -> SentenceTransformer:
    try:
        return SentenceTransformer(EMBEDDING_MODEL_NAME, local_files_only=True)
    except Exception:
        return SentenceTransformer(EMBEDDING_MODEL_NAME)


def get_chroma_collection(reset: bool = False):
    client = chromadb.PersistentClient(path=str(CHROMA_DIR))

    if reset:
        try:
            client.delete_collection(COLLECTION_NAME)
        except Exception:
            pass

    return client.get_or_create_collection(
        name=COLLECTION_NAME,
        metadata={"description": "BizPilot AI company document chunks"},
    )


def build_index(reset: bool = True) -> int:
    documents = load_company_documents()
    if not documents:
        raise RuntimeError(f"No Markdown documents found in {COMPANY_DOCS_DIR}")

    chunks = build_chunks(documents)
    if not chunks:
        raise RuntimeError("No chunks were created from company documents.")

    model = load_embedding_model()
    embeddings = model.encode([chunk.text for chunk in chunks], normalize_embeddings=True).tolist()
    collection = get_chroma_collection(reset=reset)

    collection.upsert(
        ids=[chunk.chunk_id for chunk in chunks],
        documents=[chunk.text for chunk in chunks],
        embeddings=embeddings,
        metadatas=[chunk.metadata for chunk in chunks],
    )

    return len(chunks)


def retrieve(question: str, top_k: int = 4) -> list[dict]:
    model = load_embedding_model()
    query_embedding = model.encode([question], normalize_embeddings=True).tolist()[0]
    collection = get_chroma_collection(reset=False)

    result = collection.query(
        query_embeddings=[query_embedding],
        n_results=top_k,
        include=["documents", "metadatas", "distances"],
    )

    rows: list[dict] = []
    ids = result.get("ids", [[]])[0]
    documents = result.get("documents", [[]])[0]
    metadatas = result.get("metadatas", [[]])[0]
    distances = result.get("distances", [[]])[0]

    for chunk_id, document, metadata, distance in zip(ids, documents, metadatas, distances):
        rows.append(
            {
                "id": chunk_id,
                "text": document,
                "metadata": metadata,
                "distance": float(distance),
            }
        )

    return rows


def answer_question(question: str, top_k: int = 4) -> str:
    retrieved_chunks = retrieve(question, top_k=top_k)

    if not retrieved_chunks:
        return "No relevant context was found. Build the index first with: python src/rag_pipeline.py build"

    lines = [
        "Answer:",
        generate_extractive_answer(question, retrieved_chunks),
        "",
        "Relevant context:",
    ]

    for index, row in enumerate(retrieved_chunks, start=1):
        metadata = row["metadata"]
        snippet = compact_text(row["text"], max_chars=520)
        lines.extend(
            [
                f"[{index}] {snippet}",
                f"Source: {metadata['source_path']} | type: {metadata['document_type']} | source_id: {metadata['source_id']} | chunk: {metadata['chunk_index']} | distance: {row['distance']:.4f}",
                "",
            ]
        )

    lines.append("Citations:")
    for index, row in enumerate(retrieved_chunks, start=1):
        metadata = row["metadata"]
        lines.append(f"- [{index}] {metadata['source_path']} ({metadata['source_id']}, chunk {metadata['chunk_index']})")

    return "\n".join(lines)


def generate_extractive_answer(question: str, retrieved_chunks: list[dict], max_points: int = 4) -> str:
    question_tokens = tokenize(question)
    candidates: list[tuple[float, str, int]] = []

    for source_index, row in enumerate(retrieved_chunks, start=1):
        lines = [line.strip() for line in row["text"].splitlines() if line.strip()]
        for line_index, line in enumerate(lines):
            scored_text = line
            if line.startswith("#") and line_index + 1 < len(lines):
                scored_text = f"{line} {lines[line_index + 1]}"
            score = score_text(scored_text, question_tokens)
            if score > 0:
                cleaned = re.sub(r"^#+\s*", "", scored_text)
                candidates.append((score, cleaned, source_index))

    candidates.sort(key=lambda item: item[0], reverse=True)

    answer_points: list[str] = []
    seen: set[str] = set()
    for _, text, source_index in candidates:
        compact = compact_text(text, max_chars=220)
        normalized = compact.lower()
        if normalized in seen:
            continue
        seen.add(normalized)
        answer_points.append(f"- {compact} [{source_index}]")
        if len(answer_points) >= max_points:
            break

    if not answer_points:
        return (
            "I found relevant company-document chunks, but the extractive answer layer could not isolate a short answer. "
            "Please review the cited context below."
        )

    return "\n".join(answer_points)


def tokenize(text: str) -> set[str]:
    stopwords = {
        "a",
        "an",
        "and",
        "are",
        "as",
        "at",
        "for",
        "from",
        "how",
        "is",
        "it",
        "of",
        "on",
        "or",
        "the",
        "to",
        "what",
        "which",
        "with",
    }
    tokens = {token.lower() for token in re.findall(r"[A-Za-z0-9]+", text)}
    return {token for token in tokens if len(token) > 2 and token not in stopwords}


def score_text(text: str, question_tokens: set[str]) -> float:
    text_tokens = tokenize(text)
    if not text_tokens or not question_tokens:
        return 0.0

    overlap = question_tokens.intersection(text_tokens)
    score = float(len(overlap))

    lowered = text.lower()
    if "price" in question_tokens and ("usd" in lowered or "price" in lowered):
        score += 1.5
    if "lead" in question_tokens and "lead" in lowered:
        score += 1.0
    if "qualification" in question_tokens and "qualification" in lowered:
        score += 1.0
    if "growth" in question_tokens and "growth" in lowered:
        score += 1.0

    return score


def compact_text(text: str, max_chars: int = 520) -> str:
    text = re.sub(r"\s+", " ", text).strip()
    if len(text) <= max_chars:
        return text
    return text[: max_chars - 3].rstrip() + "..."


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="BizPilot AI Week 2 RAG CLI prototype")
    subparsers = parser.add_subparsers(dest="command", required=True)

    build_parser = subparsers.add_parser("build", help="Ingest company docs, chunk them, embed them, and index in ChromaDB")
    build_parser.add_argument("--no-reset", action="store_true", help="Do not reset the existing ChromaDB collection before indexing")

    ask_parser = subparsers.add_parser("ask", help="Ask a question against the ChromaDB RAG index")
    ask_parser.add_argument("question", help="Question to ask")
    ask_parser.add_argument("--top-k", type=int, default=4, help="Number of chunks to retrieve")

    subparsers.add_parser("stats", help="Show basic ChromaDB collection stats")

    return parser.parse_args()


def main() -> None:
    args = parse_args()

    if args.command == "build":
        count = build_index(reset=not args.no_reset)
        print(f"RAG index built successfully.")
        print(f"Documents directory: {COMPANY_DOCS_DIR}")
        print(f"ChromaDB directory: {CHROMA_DIR}")
        print(f"Collection: {COLLECTION_NAME}")
        print(f"Embedding model: {EMBEDDING_MODEL_NAME}")
        print(f"Indexed chunks: {count}")
        return

    if args.command == "ask":
        print(answer_question(args.question, top_k=args.top_k))
        return

    if args.command == "stats":
        collection = get_chroma_collection(reset=False)
        print(f"Collection: {COLLECTION_NAME}")
        print(f"ChromaDB directory: {CHROMA_DIR}")
        print(f"Chunk count: {collection.count()}")
        return

    raise ValueError(f"Unsupported command: {args.command}")


if __name__ == "__main__":
    main()
