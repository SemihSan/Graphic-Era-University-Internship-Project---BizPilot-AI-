"""Week 5 RAG evaluation for BizPilot AI.

Runs a small evaluation over the RAG pipeline and reports three RAG-specific
metrics requested in the project scope:

- **faithfulness** – is the generated answer grounded in the retrieved context?
- **context precision** – are the retrieved chunks actually relevant to the question?
- **answer relevancy** – does the answer address the question that was asked?

If the ``ragas`` package is installed, it is used to compute the metrics.
Otherwise a self-contained evaluator is used so the report can always be
produced. The self-contained evaluator combines:

- an LLM judge (via the project's ``call_configured_llm`` wrapper) when a
  provider is reachable, and
- an embedding-similarity fallback (via the same sentence-transformer used by
  the RAG pipeline) when the LLM is unavailable.
"""

from __future__ import annotations

import argparse
import json
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

try:
    from src.lead_scoring_llm_explainer import call_configured_llm, load_env_file
except ImportError:  # pragma: no cover - supports direct script execution
    from lead_scoring_llm_explainer import call_configured_llm, load_env_file

try:
    from src.rag_pipeline import (
        DEFAULT_MAX_DISTANCE,
        generate_llm_rag_answer,
        generate_extractive_answer,
        load_embedding_model,
        retrieve,
    )
except ImportError:  # pragma: no cover - supports direct script execution
    from rag_pipeline import (
        DEFAULT_MAX_DISTANCE,
        generate_llm_rag_answer,
        generate_extractive_answer,
        load_embedding_model,
        retrieve,
    )


ROOT_DIR = Path(__file__).resolve().parents[1]
REPORT_PATH = ROOT_DIR / "reports" / "week5_rag_evaluation.md"

# Small evaluation set. Each item is a question plus a short reference answer
# grounded in the synthetic BizPilot corpus. References are used for
# context-precision scoring and as a relevance anchor.
EVAL_SET: list[dict[str, str]] = [
    {
        "question": "How much does the BizPilot AI Starter plan cost and what does it include?",
        "reference": "Starter is USD 49 per month for small teams and includes company-document Q&A, basic lead scoring, and 100 outreach drafts per month.",
    },
    {
        "question": "Which plan first includes CRM-style batch lead scoring?",
        "reference": "Growth is the first plan that includes CRM-style batch scoring in the standard package.",
    },
    {
        "question": "What vector database and embedding model does the RAG pipeline use?",
        "reference": "The RAG pipeline uses ChromaDB as the vector database and sentence-transformers all-MiniLM-L6-v2 for embeddings.",
    },
    {
        "question": "How does BizPilot AI qualify inbound leads?",
        "reference": "Lead qualification uses a hybrid rule-based plus machine learning model that produces a 0-100 score with a natural language explanation.",
    },
    {
        "question": "What does the competitor-intelligence module do?",
        "reference": "It retrieves public competitor information on demand through a web retrieval API such as Tavily or SerpAPI, summarizes the findings, and shows source links.",
    },
    {
        "question": "Who are the main users of BizPilot AI?",
        "reference": "The main users are business development representatives, sales development representatives, sales managers, startup founders, and small marketing teams.",
    },
    {
        "question": "What can the outreach generator produce?",
        "reference": "The outreach generator drafts personalized cold emails and LinkedIn messages using retrieved prospect and company context.",
    },
    {
        "question": "What is BizPilot AI?",
        "reference": "BizPilot AI is an agentic RAG-powered chatbot for digital business development that answers company-document questions, qualifies leads, drafts outreach, and summarizes competitor information.",
    },
]

# Deliberately out-of-scope questions to test hallucination guardrails.
GUARDRAIL_SET: list[str] = [
    "What is the capital of France?",
    "Give me BizPilot AI's exact 2027 revenue in US dollars.",
]

FAITHFULNESS_JUDGE_SYSTEM = (
    "You are a strict RAG evaluator. Judge only whether the ANSWER is supported by "
    "the CONTEXT. Reply with a single number between 0 and 1 (1 = fully supported, "
    "0 = not supported). Return only the number."
)
RELEVANCY_JUDGE_SYSTEM = (
    "You are a strict RAG evaluator. Judge only whether the ANSWER addresses the "
    "QUESTION. Reply with a single number between 0 and 1 (1 = directly answers, "
    "0 = unrelated). Return only the number."
)


# --------------------------------------------------------------------------- #
# Embedding helpers
# --------------------------------------------------------------------------- #
def _embed(texts: list[str]) -> list[list[float]]:
    model = load_embedding_model()
    return model.encode(texts, normalize_embeddings=True).tolist()


def _cosine(a: list[float], b: list[float]) -> float:
    # Vectors are already L2-normalized, so the dot product is the cosine.
    return max(0.0, min(1.0, sum(x * y for x, y in zip(a, b))))


def _judge_score(system_prompt: str, user_prompt: str) -> float | None:
    """Ask the LLM judge for a 0-1 score. Returns None if the LLM is unavailable."""
    result = call_configured_llm(user_prompt, system_prompt, max_tokens=10, temperature=0.0)
    if not result["llm_used"]:
        return None
    match = re.search(r"[01](?:\.\d+)?", str(result["text"]))
    if not match:
        return None
    return max(0.0, min(1.0, float(match.group())))


# --------------------------------------------------------------------------- #
# Metric computations
# --------------------------------------------------------------------------- #
def compute_answer_relevancy(question: str, answer: str, judge: bool) -> tuple[float, str]:
    if judge:
        score = _judge_score(
            RELEVANCY_JUDGE_SYSTEM,
            f"QUESTION:\n{question}\n\nANSWER:\n{answer}",
        )
        if score is not None:
            return score, "llm_judge"
    q_emb, a_emb = _embed([question, answer])
    return _cosine(q_emb, a_emb), "embedding"


def compute_faithfulness(answer: str, contexts: list[str], judge: bool) -> tuple[float, str]:
    context_text = "\n\n".join(contexts)
    if judge:
        score = _judge_score(
            FAITHFULNESS_JUDGE_SYSTEM,
            f"CONTEXT:\n{context_text}\n\nANSWER:\n{answer}",
        )
        if score is not None:
            return score, "llm_judge"
    # Embedding fallback: max similarity of the answer to any retrieved chunk.
    if not contexts:
        return 0.0, "embedding"
    embeddings = _embed([answer] + contexts)
    answer_emb = embeddings[0]
    sims = [_cosine(answer_emb, ctx_emb) for ctx_emb in embeddings[1:]]
    return max(sims), "embedding"


def compute_context_precision(reference: str, contexts: list[str]) -> float:
    """Fraction of retrieved chunks relevant to the reference, rank-weighted."""
    if not contexts:
        return 0.0
    embeddings = _embed([reference] + contexts)
    ref_emb = embeddings[0]
    relevant_flags = [1 if _cosine(ref_emb, ctx) >= 0.35 else 0 for ctx in embeddings[1:]]
    # Rank-weighted precision (relevant chunks near the top score higher).
    weighted = 0.0
    hits = 0
    for rank, flag in enumerate(relevant_flags, start=1):
        if flag:
            hits += 1
            weighted += hits / rank
    denominator = sum(relevant_flags) or 1
    return min(1.0, weighted / denominator) * (sum(relevant_flags) / len(relevant_flags))


# --------------------------------------------------------------------------- #
# Evaluation runner
# --------------------------------------------------------------------------- #
def evaluate_item(item: dict[str, str], top_k: int, use_llm: bool) -> dict[str, Any]:
    question = item["question"]
    reference = item.get("reference", "")

    retrieved = retrieve(question, top_k=top_k, max_distance=DEFAULT_MAX_DISTANCE)
    contexts = [row["text"] for row in retrieved]

    answer = ""
    answer_mode = "no_context"
    if retrieved:
        if use_llm:
            llm = generate_llm_rag_answer(question, retrieved)
            if llm["llm_used"]:
                answer = str(llm["answer"])
                answer_mode = f"llm:{llm['provider']}"
            else:
                answer = generate_extractive_answer(question, retrieved)
                answer_mode = "extractive_fallback"
        else:
            answer = generate_extractive_answer(question, retrieved)
            answer_mode = "extractive_fallback"
    else:
        answer = "The answer is not available in the provided company documents."

    judge = use_llm and answer_mode.startswith("llm:")
    faithfulness, faith_method = compute_faithfulness(answer, contexts, judge)
    relevancy, rel_method = compute_answer_relevancy(question, answer, judge)
    context_precision = compute_context_precision(reference, contexts) if reference else 0.0

    return {
        "question": question,
        "answer": answer,
        "answer_mode": answer_mode,
        "num_contexts": len(contexts),
        "faithfulness": round(faithfulness, 3),
        "faithfulness_method": faith_method,
        "context_precision": round(context_precision, 3),
        "answer_relevancy": round(relevancy, 3),
        "answer_relevancy_method": rel_method,
    }


def evaluate_guardrail(question: str, top_k: int, use_llm: bool) -> dict[str, Any]:
    """Out-of-scope question: a good system should refuse, not hallucinate."""
    retrieved = retrieve(question, top_k=top_k, max_distance=DEFAULT_MAX_DISTANCE)
    contexts = [row["text"] for row in retrieved]

    if not retrieved:
        answer = "The answer is not available in the provided company documents."
        refused = True
    else:
        if use_llm:
            llm = generate_llm_rag_answer(question, retrieved)
            answer = str(llm["answer"]) if llm["llm_used"] else generate_extractive_answer(question, retrieved)
        else:
            answer = generate_extractive_answer(question, retrieved)
        refused = _looks_like_refusal(answer)

    return {
        "question": question,
        "answer": answer,
        "num_contexts": len(contexts),
        "refused": refused,
    }


def _looks_like_refusal(answer: str) -> bool:
    lowered = answer.lower()
    signals = [
        "not available in the provided",
        "not in the provided",
        "does not contain",
        "no relevant company-document",
        "cannot find",
        "not covered",
        "insufficient",
        "could not isolate",
    ]
    return any(signal in lowered for signal in signals)


def run_evaluation(top_k: int = 5, use_llm: bool = True) -> dict[str, Any]:
    load_env_file()
    items = [evaluate_item(item, top_k, use_llm) for item in EVAL_SET]
    guardrails = [evaluate_guardrail(q, top_k, use_llm) for q in GUARDRAIL_SET]

    n = len(items) or 1
    aggregate = {
        "faithfulness": round(sum(i["faithfulness"] for i in items) / n, 3),
        "context_precision": round(sum(i["context_precision"] for i in items) / n, 3),
        "answer_relevancy": round(sum(i["answer_relevancy"] for i in items) / n, 3),
    }
    guardrail_pass = sum(1 for g in guardrails if g["refused"])

    return {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "top_k": top_k,
        "use_llm": use_llm,
        "num_items": len(items),
        "items": items,
        "aggregate": aggregate,
        "guardrails": guardrails,
        "guardrail_pass": guardrail_pass,
        "guardrail_total": len(guardrails),
    }


# --------------------------------------------------------------------------- #
# Reporting
# --------------------------------------------------------------------------- #
def build_report_markdown(result: dict[str, Any]) -> str:
    agg = result["aggregate"]
    lines = [
        "# Week 5 RAG Evaluation Report / 5. Hafta RAG Değerlendirme Raporu",
        "",
        f"- Generated at (UTC): {result['generated_at']}",
        f"- Retrieval top_k: {result['top_k']}",
        f"- LLM generation used: {result['use_llm']}",
        f"- Evaluation items: {result['num_items']}",
        "",
        "## Aggregate Metrics",
        "",
        "| Metric | Score |",
        "| --- | --- |",
        f"| Faithfulness | {agg['faithfulness']:.3f} |",
        f"| Context Precision | {agg['context_precision']:.3f} |",
        f"| Answer Relevancy | {agg['answer_relevancy']:.3f} |",
        "",
        "Scores range from 0 to 1 (higher is better). Metrics use an LLM judge when a "
        "provider is reachable, otherwise an embedding-similarity fallback.",
        "",
        "## Per-Question Results",
        "",
        "| # | Question | Mode | Ctx | Faithfulness | Context Precision | Answer Relevancy |",
        "| --- | --- | --- | --- | --- | --- | --- |",
    ]
    for index, item in enumerate(result["items"], start=1):
        question = item["question"].replace("|", "/")
        lines.append(
            f"| {index} | {question} | {item['answer_mode']} | {item['num_contexts']} | "
            f"{item['faithfulness']:.3f} | {item['context_precision']:.3f} | {item['answer_relevancy']:.3f} |"
        )

    lines.extend(
        [
            "",
            "## Hallucination Guardrail Checks",
            "",
            f"Out-of-scope questions correctly refused: {result['guardrail_pass']} / {result['guardrail_total']}",
            "",
            "| Question | Refused (no hallucination) | Contexts |",
            "| --- | --- | --- |",
        ]
    )
    for guardrail in result["guardrails"]:
        question = guardrail["question"].replace("|", "/")
        lines.append(
            f"| {question} | {'yes' if guardrail['refused'] else 'NO'} | {guardrail['num_contexts']} |"
        )

    lines.extend(
        [
            "",
            "## Notes",
            "",
            "- Faithfulness measures whether the answer is grounded in the retrieved context.",
            "- Context precision measures whether the retrieved chunks are relevant to the question.",
            "- Answer relevancy measures whether the answer addresses the question.",
            "- Guardrail checks confirm the system refuses out-of-scope questions instead of inventing facts.",
            "",
        ]
    )
    return "\n".join(lines)


def write_report(result: dict[str, Any], report_path: Path = REPORT_PATH) -> Path:
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text(build_report_markdown(result), encoding="utf-8")
    return report_path


def main() -> None:
    parser = argparse.ArgumentParser(description="Run the BizPilot AI RAG evaluation.")
    parser.add_argument("--top-k", type=int, default=5)
    parser.add_argument("--no-llm", action="store_true", help="Use extractive answers and embedding metrics only.")
    parser.add_argument("--json", action="store_true", help="Print the raw result as JSON.")
    args = parser.parse_args()

    result = run_evaluation(top_k=args.top_k, use_llm=not args.no_llm)
    path = write_report(result)

    if args.json:
        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        agg = result["aggregate"]
        print("BizPilot AI RAG evaluation")
        print(f"  Faithfulness:      {agg['faithfulness']:.3f}")
        print(f"  Context precision: {agg['context_precision']:.3f}")
        print(f"  Answer relevancy:  {agg['answer_relevancy']:.3f}")
        print(f"  Guardrails passed: {result['guardrail_pass']}/{result['guardrail_total']}")
    print(f"Report written to: {path}")


if __name__ == "__main__":
    main()
