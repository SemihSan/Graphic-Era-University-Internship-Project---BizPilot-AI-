"""Smoke tests for BizPilot AI.

Fast, network-free checks that the core building blocks import and behave
sensibly. Heavy paths (embedding downloads, live LLM calls) are avoided so the
suite runs in CI without secrets or model downloads.
"""
from __future__ import annotations

from pathlib import Path

import pytest

ROOT_DIR = Path(__file__).resolve().parents[1]
MODEL_PATH = ROOT_DIR / "models" / "lead_scoring_logreg.joblib"


# --------------------------------------------------------------------------- #
# RAG pipeline: pure text logic (no embeddings / no network)
# --------------------------------------------------------------------------- #
def test_chunk_text_splits_long_text():
    from src.rag_pipeline import chunk_text

    text = "\n\n".join(f"Paragraph {i} " + ("x" * 400) for i in range(5))
    chunks = chunk_text(text, max_chars=500, overlap_chars=0)

    assert len(chunks) >= 2
    assert all(isinstance(c, str) and c.strip() for c in chunks)


def test_chunk_text_short_text_single_chunk():
    from src.rag_pipeline import chunk_text

    chunks = chunk_text("A short paragraph.", max_chars=900)
    assert chunks == ["A short paragraph."]


def test_chunk_text_overlap_adds_context():
    from src.rag_pipeline import chunk_text

    text = "\n\n".join(f"Section {i} " + ("y" * 400) for i in range(4))
    no_overlap = chunk_text(text, max_chars=500, overlap_chars=0)
    with_overlap = chunk_text(text, max_chars=500, overlap_chars=80)

    assert len(with_overlap) == len(no_overlap)
    # Overlapped chunks (after the first) should be at least as long.
    assert len(with_overlap[1]) >= len(no_overlap[1])


def test_load_company_documents_parses_dataset():
    from src.rag_pipeline import COMPANY_DOCS_DATASET, load_company_documents

    if not COMPANY_DOCS_DATASET.exists():
        pytest.skip("Company docs dataset not present")

    docs = load_company_documents()
    assert len(docs) > 0
    first = docs[0]
    for key in ("title", "text", "document_type", "source_id"):
        assert key in first and first[key]


def test_build_chunks_produces_ids():
    from src.rag_pipeline import build_chunks, load_company_documents, COMPANY_DOCS_DATASET

    if not COMPANY_DOCS_DATASET.exists():
        pytest.skip("Company docs dataset not present")

    chunks = build_chunks(load_company_documents())
    assert len(chunks) > 0
    ids = [c.chunk_id for c in chunks]
    assert len(ids) == len(set(ids))  # ids are unique
    assert all("::chunk_" in cid for cid in ids)


# --------------------------------------------------------------------------- #
# Chat intent routing (keyword rules, no network)
# --------------------------------------------------------------------------- #
@pytest.mark.parametrize(
    "text,expected",
    [
        ("Compare us with HubSpot", "competitor"),
        ("Write a cold email to Acme", "outreach"),
        ("Score this lead please", "lead"),
        ("How much does the Starter plan cost?", "rag"),
    ],
)
def test_classify_chat_intent(text, expected):
    import app

    assert app.classify_chat_intent(text) == expected


def test_extract_outreach_company():
    import app

    assert app._extract_outreach_company("Write an email to Acme Corp") == "Acme Corp"
    assert app._extract_outreach_company("no company here") == ""


def test_classify_chat_intent_scored_prefers_stronger_signal():
    import app

    # Two competitor keywords ("compare", "hubspot", "salesforce") outweigh a
    # single incidental match, so the message routes to competitor.
    assert app.classify_chat_intent("Compare HubSpot and Salesforce pricing") == "competitor"


def test_classify_chat_intent_empty_falls_back_to_rag():
    import app

    assert app.classify_chat_intent("") == "rag"
    assert app.classify_chat_intent("Tell me about the product") == "rag"



# --------------------------------------------------------------------------- #
# Lead scoring (uses committed model if available)
# --------------------------------------------------------------------------- #
def test_score_lead_returns_expected_keys():
    if not MODEL_PATH.exists():
        pytest.skip("Trained model not present")

    from src.lead_scoring_predictor import score_lead

    lead = {
        "Lead Origin": "API",
        "Lead Source": "Google",
        "TotalVisits": 5,
        "Total Time Spent on Website": 600,
        "Page Views Per Visit": 3.0,
    }
    result = score_lead(lead)

    assert {"final_score", "label"}.issubset(result.keys())
    assert 0 <= result["final_score"] <= 100
