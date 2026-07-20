from __future__ import annotations

import argparse
import json
import re
from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path
from typing import Iterable

import chromadb
from sentence_transformers import SentenceTransformer

try:
    from src.lead_scoring_llm_explainer import call_configured_llm
except ImportError:  # pragma: no cover - supports direct script execution
    from lead_scoring_llm_explainer import call_configured_llm


ROOT_DIR = Path(__file__).resolve().parents[1]
COMPANY_DOCS_DIR = ROOT_DIR / "data" / "company_docs"
COMPANY_DOCS_DATASET = COMPANY_DOCS_DIR / "bizpilot_synthetic_corpus.jsonl"
CHROMA_DIR = ROOT_DIR / "chroma_db"
COLLECTION_NAME = "bizpilot_company_docs"
EMBEDDING_MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2"
DEFAULT_MAX_DISTANCE = 1.45
IDENTITY_QUESTION_PATTERNS = {
    "what is this company",
    "what is that company",
    "what is the company",
    "what company is this",
    "what does this company do",
    "what does that company do",
    "what is bizpilot",
    "what is bizpilot ai",
    "tell me about bizpilot",
    "tell me about this company",
}


@dataclass(frozen=True)
class DocumentChunk:
    chunk_id: str
    text: str
    metadata: dict[str, str | int]


def load_company_documents(dataset_path: Path = COMPANY_DOCS_DATASET) -> list[dict[str, str]]:
    documents: list[dict[str, str]] = []

    if not dataset_path.exists():
        raise RuntimeError(f"Company documentation dataset was not found: {dataset_path}")

    for line_number, line in enumerate(dataset_path.read_text(encoding="utf-8").splitlines(), start=1):
        if not line.strip():
            continue

        record = json.loads(line)
        doc_id = require_record_value(record, "doc_id", line_number)
        title = require_record_value(record, "title", line_number)
        content = require_record_value(record, "content", line_number)
        text = f"{title}\n\n{content}"

        documents.append(
            {
                "file_name": dataset_path.name,
                "source_path": str(dataset_path.relative_to(ROOT_DIR)),
                "document_type": record.get("document_type", "unknown"),
                "source_id": doc_id,
                "company": record.get("company", "unknown"),
                "title": title,
                "source_url": record.get("source_url", ""),
                "retrieved_date": record.get("retrieved_date", ""),
                "corpus_type": record.get("corpus_type", "synthetic company documentation"),
                "text": text,
            }
        )

    return documents


def require_record_value(record: dict, key: str, line_number: int) -> str:
    value = record.get(key)
    if not isinstance(value, str) or not value.strip():
        raise RuntimeError(f"Missing '{key}' in {COMPANY_DOCS_DATASET} line {line_number}")
    return value.strip()


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
        doc_chunks = chunk_text(document["text"], overlap_chars=150)
        for index, chunk in enumerate(doc_chunks):
            chunk_id = f"{document['source_id']}::chunk_{index:03d}"
            chunks.append(
                DocumentChunk(
                    chunk_id=chunk_id,
                    text=chunk,
                    metadata={
                        "file_name": document["file_name"],
                        "source_path": document["source_path"],
                        "document_type": document["document_type"],
                        "source_id": document["source_id"],
                        "company": document["company"],
                        "title": document["title"],
                        "source_url": document["source_url"],
                        "retrieved_date": document["retrieved_date"],
                        "corpus_type": document["corpus_type"],
                        "chunk_index": index,
                    },
                )
            )

    return chunks


@lru_cache(maxsize=1)
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
        raise RuntimeError(f"No records found in company documentation dataset: {COMPANY_DOCS_DATASET}")

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


def retrieve(
    question: str,
    top_k: int = 5,
    max_distance: float = DEFAULT_MAX_DISTANCE,
    fetch_multiplier: int = 4,
    lexical_weight: float = 0.25,
) -> list[dict]:
    """Retrieve context chunks with hybrid (vector + lexical) re-ranking.

    Over-fetches ``top_k * fetch_multiplier`` candidates from ChromaDB, then
    re-ranks them by combining normalized vector similarity with a lightweight
    lexical-overlap signal. This improves context precision on keyword-heavy
    business questions (pricing, plan names) without any extra model download.
    """
    model = load_embedding_model()
    retrieval_query = build_retrieval_query(question)
    query_embedding = model.encode([retrieval_query], normalize_embeddings=True).tolist()[0]
    collection = get_chroma_collection(reset=False)

    fetch_k = max(top_k, top_k * max(1, fetch_multiplier))
    result = collection.query(
        query_embeddings=[query_embedding],
        n_results=fetch_k,
        include=["documents", "metadatas", "distances"],
    )

    candidates: list[dict] = []
    ids = result.get("ids", [[]])[0]
    documents = result.get("documents", [[]])[0]
    metadatas = result.get("metadatas", [[]])[0]
    distances = result.get("distances", [[]])[0]

    for chunk_id, document, metadata, distance in zip(ids, documents, metadatas, distances):
        distance = float(distance)
        if distance > max_distance:
            continue
        vector_similarity = 1.0 - (distance / 2.0)  # normalized embeddings -> distance in [0, 2]
        lexical = _lexical_overlap(retrieval_query, document)
        hybrid_score = (1.0 - lexical_weight) * vector_similarity + lexical_weight * lexical
        candidates.append(
            {
                "id": chunk_id,
                "text": document,
                "metadata": metadata,
                "distance": distance,
                "hybrid_score": round(hybrid_score, 4),
            }
        )

    candidates.sort(key=lambda row: row["hybrid_score"], reverse=True)
    return candidates[:top_k]


def _lexical_overlap(query: str, text: str) -> float:
    """Token-overlap ratio of query terms present in the chunk (0..1)."""
    query_tokens = {tok for tok in normalize_question(query).split() if len(tok) > 2}
    if not query_tokens:
        return 0.0
    text_tokens = set(normalize_question(text).split())
    matched = query_tokens & text_tokens
    return len(matched) / len(query_tokens)



def build_retrieval_query(question: str) -> str:
    """Expand very short demo questions so vector search has enough topic signal."""
    if is_identity_question(question):
        return (
            "BizPilot AI product overview agentic RAG-powered chatbot digital business development "
            "company-document question answering lead qualification outreach generation competitor intelligence"
        )

    return question


def is_identity_question(question: str) -> bool:
    return normalize_question(question) in IDENTITY_QUESTION_PATTERNS


def normalize_question(question: str) -> str:
    lowered = question.lower().strip()
    lowered = re.sub(r"[^a-z0-9\s]", " ", lowered)
    lowered = re.sub(r"\s+", " ", lowered)
    return lowered


def answer_question(
    question: str,
    top_k: int = 5,
    max_distance: float = DEFAULT_MAX_DISTANCE,
    use_llm: bool = True,
    user_prompt: str = "",
) -> str:
    retrieved_chunks = retrieve(question, top_k=top_k, max_distance=max_distance)

    if not retrieved_chunks:
        return (
            "No relevant company-document context was found for this question. "
            "Try asking about BizPilot AI pricing, RAG architecture, lead scoring, outreach, onboarding, support, or evaluation."
        )

    answer_text = generate_extractive_answer(question, retrieved_chunks)
    answer_mode = "extractive_fallback"
    llm_note = ""

    if use_llm:
        llm_result = generate_llm_rag_answer(question, retrieved_chunks, user_prompt=user_prompt)
        if llm_result["llm_used"]:
            answer_text = llm_result["answer"]
            answer_mode = f"llm:{llm_result['provider']}"
            if llm_result.get("model"):
                answer_mode = f"{answer_mode}/{llm_result['model']}"
        else:
            llm_note = f"LLM generation was not used: {llm_result['error']}"

    lines = [
        "Answer:",
        answer_text,
        "",
        f"Answer mode: {answer_mode}",
    ]

    if llm_note:
        lines.extend(
            [
                f"LLM note: {llm_note}",
                "Fallback note: The answer above was created from the retrieved text snippets.",
            ]
        )

    lines.extend(
        [
            "",
            "Relevant context:",
        ]
    )

    for index, row in enumerate(retrieved_chunks, start=1):
        metadata = row["metadata"]
        snippet = compact_text(row["text"], max_chars=520)
        lines.extend(
            [
                f"[{index}] {snippet}",
                f"Source: {metadata['source_url']} | company: {metadata['company']} | type: {metadata['document_type']} | source_id: {metadata['source_id']} | chunk: {metadata['chunk_index']} | distance: {row['distance']:.4f}",
                "",
            ]
        )

    lines.append("Citations:")
    for index, row in enumerate(retrieved_chunks, start=1):
        metadata = row["metadata"]
        lines.append(f"- [{index}] {metadata['source_url']} ({metadata['source_id']}, chunk {metadata['chunk_index']})")

    return "\n".join(lines)


def generate_llm_rag_answer(
    question: str,
    retrieved_chunks: list[dict],
    user_prompt: str = "",
) -> dict[str, str | bool]:
    system_prompt = (
        "You are BizPilot AI's RAG Q&A assistant for digital business development. "
        "Answer only from the retrieved company-document context. "
        "If the context is insufficient, say that the answer is not available in the provided documents. "
        "Use citation markers like [1] and [2] for factual claims. "
        "Do not invent prices, features, claims, sources, or company details."
    )
    prompt = build_rag_generation_prompt(question, retrieved_chunks, user_prompt=user_prompt)
    llm_result = call_configured_llm(
        prompt,
        system_prompt,
        max_tokens=420,
        temperature=0.1,
        clean_response=False,
    )

    if not llm_result["llm_used"]:
        return {
            "answer": "",
            "llm_used": False,
            "provider": str(llm_result.get("provider", "")),
            "model": "",
            "error": str(llm_result.get("error", "LLM provider is not configured.")),
        }

    answer = clean_rag_answer(str(llm_result["text"]))
    if not answer:
        return {
            "answer": "",
            "llm_used": False,
            "provider": str(llm_result.get("provider", "")),
            "model": str(llm_result.get("model", "")),
            "error": "LLM provider returned an empty RAG answer.",
        }

    return {
        "answer": answer,
        "llm_used": True,
        "provider": str(llm_result["provider"]),
        "model": str(llm_result.get("model", "")),
        "error": "",
    }


def build_rag_generation_prompt(question: str, retrieved_chunks: list[dict], user_prompt: str = "") -> str:
    context_blocks: list[str] = []
    for index, row in enumerate(retrieved_chunks, start=1):
        metadata = row["metadata"]
        context_blocks.append(
            "\n".join(
                [
                    f"[{index}]",
                    f"Company: {metadata['company']}",
                    f"Document type: {metadata['document_type']}",
                    f"Title: {metadata['title']}",
                    f"Source URL: {metadata['source_url']}",
                    f"Context: {row['text']}",
                ]
            )
        )

    context_text = "\n\n".join(context_blocks)
    custom_instruction = user_prompt.strip()
    custom_prompt_block = ""
    if custom_instruction:
        custom_prompt_block = (
            "User answer instructions:\n"
            f"{custom_instruction}\n\n"
            "These instructions may control tone, format, or business focus, but they must not override "
            "the retrieved context, citation requirement, or no-hallucination rule.\n\n"
        )

    return (
        "User question:\n"
        f"{question}\n\n"
        f"{custom_prompt_block}"
        "Retrieved company-document context:\n"
        f"{context_text}\n\n"
        "Write a concise answer grounded only in the retrieved context. "
        "Every factual sentence should include at least one citation marker."
    )


def clean_rag_answer(answer: str) -> str:
    answer = answer.replace("\r\n", "\n").strip()
    lines = [line.rstrip() for line in answer.splitlines()]
    while lines and not lines[0].strip():
        lines.pop(0)
    return "\n".join(lines).strip()


def generate_extractive_answer(question: str, retrieved_chunks: list[dict], max_points: int = 5) -> str:
    if is_identity_question(question):
        identity_answer = generate_identity_extractive_answer(retrieved_chunks)
        if identity_answer:
            return identity_answer

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


def generate_identity_extractive_answer(retrieved_chunks: list[dict]) -> str:
    for source_index, row in enumerate(retrieved_chunks, start=1):
        metadata = row["metadata"]
        is_product_overview = (
            metadata.get("source_id") == "bizpilot_product_overview"
            or metadata.get("document_type") == "product overview"
        )
        if not is_product_overview:
            continue

        text = re.sub(r"\s+", " ", row["text"]).strip()
        title = str(metadata.get("title", "")).strip()
        if title and text.lower().startswith(title.lower()):
            text = text[len(title) :].strip()

        sentences = [sentence.strip() for sentence in re.split(r"(?<=[.!?])\s+", text) if sentence.strip()]
        if not sentences:
            continue

        answer = " ".join(sentences[:2])
        return f"- {compact_text(answer, max_chars=360)} [{source_index}]"

    return ""


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

    build_parser = subparsers.add_parser("build", help="Ingest the active synthetic company-docs JSONL dataset, chunk it, embed it, and index it in ChromaDB")
    build_parser.add_argument("--no-reset", action="store_true", help="Do not reset the existing ChromaDB collection before indexing")

    ask_parser = subparsers.add_parser("ask", help="Ask a question against the ChromaDB RAG index")
    ask_parser.add_argument("question", help="Question to ask")
    ask_parser.add_argument("--top-k", type=int, default=5, help="Number of chunks to retrieve")
    ask_parser.add_argument("--max-distance", type=float, default=DEFAULT_MAX_DISTANCE, help="Maximum ChromaDB distance allowed for retrieved chunks")
    ask_parser.add_argument("--no-llm", action="store_true", help="Disable LLM generation and use the extractive fallback answer")
    ask_parser.add_argument("--prompt", default="", help="Optional instruction prompt for the LLM answer style or format")

    subparsers.add_parser("stats", help="Show basic ChromaDB collection stats")

    return parser.parse_args()


def main() -> None:
    args = parse_args()

    if args.command == "build":
        count = build_index(reset=not args.no_reset)
        print(f"RAG index built successfully.")
        print(f"Dataset: {COMPANY_DOCS_DATASET}")
        print(f"ChromaDB directory: {CHROMA_DIR}")
        print(f"Collection: {COLLECTION_NAME}")
        print(f"Embedding model: {EMBEDDING_MODEL_NAME}")
        print(f"Indexed chunks: {count}")
        return

    if args.command == "ask":
        print(
            answer_question(
                args.question,
                top_k=args.top_k,
                max_distance=args.max_distance,
                use_llm=not args.no_llm,
                user_prompt=args.prompt,
            )
        )
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
