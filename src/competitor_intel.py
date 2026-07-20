"""Week 4 competitor-intelligence retriever for BizPilot AI.

Retrieves public web information about a competitor or market topic and
summarizes it with the configured LLM. The retrieval layer tries Tavily first,
then SerpAPI, and finally falls back to the local synthetic competitor-intelligence
notes in the RAG corpus so the prototype always works offline.

The HTTP calls use the standard library ``urllib`` (same lightweight approach as
``lead_scoring_llm_explainer``) so no extra SDK dependency is required.
"""

from __future__ import annotations

import argparse
import json
import os
import socket
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path
from typing import Any

try:
    from src.lead_scoring_llm_explainer import (
        build_url_opener,
        call_configured_llm,
        get_llm_timeout_seconds,
        load_env_file,
    )
except ImportError:  # pragma: no cover - supports direct script execution
    from lead_scoring_llm_explainer import (
        build_url_opener,
        call_configured_llm,
        get_llm_timeout_seconds,
        load_env_file,
    )

try:
    from src.rag_pipeline import COMPANY_DOCS_DATASET
except ImportError:  # pragma: no cover - supports direct script execution
    from rag_pipeline import COMPANY_DOCS_DATASET


TAVILY_SEARCH_URL = "https://api.tavily.com/search"
SERPAPI_SEARCH_URL = "https://serpapi.com/search.json"
DEFAULT_MAX_RESULTS = 5

COMPETITOR_SYSTEM_PROMPT = (
    "You are BizPilot AI's competitor-intelligence analyst for a digital "
    "business-development team. Summarize only the provided public search "
    "snippets. Do not invent facts that are not in the snippets. Return only "
    "the final summary."
)


def run_competitor_intelligence(
    query: str,
    max_results: int = DEFAULT_MAX_RESULTS,
    use_llm: bool = True,
) -> dict[str, Any]:
    """Retrieve public web info for ``query`` and optionally summarize it.

    Returns a dict with the retrieval provider, the raw results, and a
    natural-language summary (or an extractive fallback summary).
    """
    load_env_file()
    query = query.strip()
    if not query:
        raise ValueError("Competitor-intelligence query must not be empty.")

    retrieval = retrieve_competitor_info(query, max_results=max_results)
    results = retrieval["results"]

    summary = ""
    summary_provider = "none"
    summary_error = ""

    if not results:
        summary = (
            "No public web results were retrieved for this query. Configure a "
            "TAVILY_API_KEY or SERPAPI_API_KEY, or ask about a topic covered by "
            "the local competitor-intelligence notes."
        )
        summary_provider = "empty"
    elif use_llm:
        llm = summarize_with_llm(query, results)
        if llm["llm_used"]:
            summary = llm["text"]
            summary_provider = f"llm:{llm['provider']}"
        else:
            summary = build_extractive_summary(query, results)
            summary_provider = "extractive_fallback"
            summary_error = llm["error"]
    else:
        summary = build_extractive_summary(query, results)
        summary_provider = "extractive_fallback"

    return {
        "query": query,
        "retrieval_provider": retrieval["provider"],
        "retrieval_note": retrieval["note"],
        "results": results,
        "summary": summary,
        "summary_provider": summary_provider,
        "summary_error": summary_error,
    }


def retrieve_competitor_info(query: str, max_results: int = DEFAULT_MAX_RESULTS) -> dict[str, Any]:
    """Try Tavily, then SerpAPI, then the local corpus fallback."""
    tavily_key = os.getenv("TAVILY_API_KEY", "").strip()
    serpapi_key = os.getenv("SERPAPI_API_KEY", "").strip()

    if tavily_key:
        try:
            results = search_tavily(query, tavily_key, max_results)
            if results:
                return {"provider": "tavily", "results": results, "note": ""}
        except RuntimeError as exc:
            fallback = search_local_corpus(query, max_results)
            return {
                "provider": "local_corpus_fallback",
                "results": fallback,
                "note": f"Tavily failed, used local corpus. {exc}",
            }

    if serpapi_key:
        try:
            results = search_serpapi(query, serpapi_key, max_results)
            if results:
                return {"provider": "serpapi", "results": results, "note": ""}
        except RuntimeError as exc:
            fallback = search_local_corpus(query, max_results)
            return {
                "provider": "local_corpus_fallback",
                "results": fallback,
                "note": f"SerpAPI failed, used local corpus. {exc}",
            }

    results = search_local_corpus(query, max_results)
    note = (
        "No TAVILY_API_KEY or SERPAPI_API_KEY configured; used local synthetic "
        "competitor-intelligence notes."
    )
    return {"provider": "local_corpus_fallback", "results": results, "note": note}


def search_tavily(query: str, api_key: str, max_results: int) -> list[dict[str, str]]:
    body = json.dumps(
        {
            "api_key": api_key,
            "query": query,
            "max_results": max_results,
            "search_depth": "basic",
            "include_answer": False,
        }
    ).encode("utf-8")

    request = urllib.request.Request(
        TAVILY_SEARCH_URL,
        data=body,
        headers={"Content-Type": "application/json", "Accept": "application/json"},
        method="POST",
    )
    payload = _open_json(request)

    results: list[dict[str, str]] = []
    for item in payload.get("results", [])[:max_results]:
        if not isinstance(item, dict):
            continue
        results.append(
            {
                "title": str(item.get("title", "")).strip(),
                "url": str(item.get("url", "")).strip(),
                "content": str(item.get("content", "")).strip(),
                "source": "tavily",
            }
        )
    return results


def search_serpapi(query: str, api_key: str, max_results: int) -> list[dict[str, str]]:
    params = urllib.parse.urlencode(
        {"engine": "google", "q": query, "api_key": api_key, "num": max_results}
    )
    request = urllib.request.Request(
        f"{SERPAPI_SEARCH_URL}?{params}",
        headers={"Accept": "application/json"},
        method="GET",
    )
    payload = _open_json(request)

    results: list[dict[str, str]] = []
    for item in payload.get("organic_results", [])[:max_results]:
        if not isinstance(item, dict):
            continue
        results.append(
            {
                "title": str(item.get("title", "")).strip(),
                "url": str(item.get("link", "")).strip(),
                "content": str(item.get("snippet", "")).strip(),
                "source": "serpapi",
            }
        )
    return results


def search_local_corpus(query: str, max_results: int) -> list[dict[str, str]]:
    """Keyword search over the synthetic competitor-intelligence corpus notes."""
    dataset_path: Path = COMPANY_DOCS_DATASET
    if not dataset_path.exists():
        return []

    keywords = {token for token in _tokenize(query) if len(token) > 2}
    scored: list[tuple[int, dict[str, str]]] = []

    for line in dataset_path.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        try:
            record = json.loads(line)
        except json.JSONDecodeError:
            continue

        doc_type = str(record.get("document_type", "")).lower()
        title = str(record.get("title", ""))
        content = str(record.get("content", ""))
        haystack = _tokenize(f"{title} {content} {doc_type}")

        score = sum(1 for keyword in keywords if keyword in haystack)
        if "competitor" in doc_type or "competitor" in title.lower():
            score += 2

        if score > 0:
            scored.append(
                (
                    score,
                    {
                        "title": title,
                        "url": str(record.get("source_url", "")),
                        "content": content[:600],
                        "source": "local_corpus",
                    },
                )
            )

    scored.sort(key=lambda pair: pair[0], reverse=True)
    return [item for _, item in scored[:max_results]]


def summarize_with_llm(query: str, results: list[dict[str, str]]) -> dict[str, Any]:
    snippets = []
    for index, item in enumerate(results, start=1):
        snippets.append(
            f"[{index}] {item.get('title', '')}\n{item.get('content', '')}\nURL: {item.get('url', '')}"
        )
    joined = "\n\n".join(snippets)

    prompt = (
        f"Competitor-intelligence query: {query}\n\n"
        "Summarize the public search snippets below into a concise briefing for a "
        "sales team. Cover positioning, notable strengths or weaknesses, and how "
        "BizPilot AI (an agentic RAG lead-qualification and outreach assistant) "
        "could differentiate. Write 3 to 5 sentences and reference snippet numbers "
        "like [1] where relevant. Use plain ASCII punctuation.\n\n"
        f"Public search snippets:\n{joined}"
    )

    return call_configured_llm(prompt, COMPETITOR_SYSTEM_PROMPT, max_tokens=420, clean_response=False)


def build_extractive_summary(query: str, results: list[dict[str, str]]) -> str:
    lines = [f"Competitor-intelligence briefing for: {query}", ""]
    for index, item in enumerate(results, start=1):
        title = item.get("title", "Untitled")
        content = item.get("content", "").strip()
        if len(content) > 260:
            content = content[:260].rstrip() + "..."
        lines.append(f"[{index}] {title}")
        if content:
            lines.append(content)
        if item.get("url"):
            lines.append(f"Source: {item['url']}")
        lines.append("")
    return "\n".join(lines).strip()


def _open_json(request: urllib.request.Request) -> dict[str, Any]:
    timeout_seconds = get_llm_timeout_seconds()
    try:
        opener = build_url_opener()
        with opener.open(request, timeout=timeout_seconds) as response:
            return json.loads(response.read().decode("utf-8"))
    except urllib.error.HTTPError as exc:
        detail = exc.read().decode("utf-8", errors="replace")
        raise RuntimeError(f"Search API returned HTTP {exc.code}: {detail[:200]}") from exc
    except (TimeoutError, socket.timeout) as exc:
        raise RuntimeError(f"Search API request timed out after {timeout_seconds} seconds.") from exc
    except urllib.error.URLError as exc:
        raise RuntimeError(f"Search API request failed: {exc.reason}") from exc


def _tokenize(text: str) -> set[str]:
    cleaned = "".join(char.lower() if char.isalnum() else " " for char in text)
    return set(cleaned.split())


def _format_cli_output(result: dict[str, Any]) -> str:
    lines = [
        f"Query: {result['query']}",
        f"Retrieval provider: {result['retrieval_provider']}",
    ]
    if result["retrieval_note"]:
        lines.append(f"Retrieval note: {result['retrieval_note']}")
    lines.append(f"Summary provider: {result['summary_provider']}")
    if result["summary_error"]:
        lines.append(f"Summary note: {result['summary_error']}")
    lines.extend(["", "Summary:", result["summary"], "", "Results:"])
    for index, item in enumerate(result["results"], start=1):
        lines.append(f"[{index}] {item.get('title', '')} ({item.get('source', '')})")
        if item.get("url"):
            lines.append(f"    {item['url']}")
    return "\n".join(lines)


def main() -> None:
    parser = argparse.ArgumentParser(description="BizPilot AI competitor-intelligence retriever.")
    parser.add_argument("query", nargs="?", default="AI lead scoring and outreach SaaS competitors")
    parser.add_argument("--max-results", type=int, default=DEFAULT_MAX_RESULTS)
    parser.add_argument("--no-llm", action="store_true", help="Skip the LLM summary layer.")
    args = parser.parse_args()

    result = run_competitor_intelligence(
        args.query,
        max_results=args.max_results,
        use_llm=not args.no_llm,
    )
    print(_format_cli_output(result))


if __name__ == "__main__":
    main()
