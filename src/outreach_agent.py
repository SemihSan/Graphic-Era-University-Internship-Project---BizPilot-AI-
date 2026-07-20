"""Week 4 agentic outreach generator for BizPilot AI.

Implements a small multi-step agent graph that turns a prospect + lead signal
into a personalized cold email and LinkedIn message:

    qualify -> research -> draft -> critique/refine

If ``langgraph`` is installed it is used to build a real ``StateGraph``. When it
is not available the same nodes run through a lightweight sequential runner, so
the module is always functional. The LLM calls reuse the project's stdlib-based
``call_configured_llm`` wrapper and gracefully fall back to a template draft when
no LLM provider is reachable.
"""

from __future__ import annotations

import argparse
import json
from typing import Any, Callable, TypedDict

try:
    from src.lead_scoring_llm_explainer import call_configured_llm, load_env_file
except ImportError:  # pragma: no cover - supports direct script execution
    from lead_scoring_llm_explainer import call_configured_llm, load_env_file

try:
    from src.lead_scoring_predictor import score_lead
except ImportError:  # pragma: no cover
    from lead_scoring_predictor import score_lead

try:
    from src.rag_pipeline import retrieve as rag_retrieve
except ImportError:  # pragma: no cover
    from rag_pipeline import retrieve as rag_retrieve


OUTREACH_SYSTEM_PROMPT = (
    "You are BizPilot AI's outreach copywriter for a digital business-development "
    "team. Write concise, personalized B2B outreach. Never invent metrics or "
    "customer names. Return only the requested JSON."
)
CRITIQUE_SYSTEM_PROMPT = (
    "You are a senior sales editor. Improve outreach drafts for clarity, brevity, "
    "and personalization without inventing facts. Return only the requested JSON."
)


class OutreachState(TypedDict, total=False):
    company: str
    contact: str
    pain_point: str
    lead_data: dict[str, Any]
    use_rag: bool
    use_llm: bool
    # populated by nodes
    score: int
    label: str
    score_source: str
    research: list[dict[str, str]]
    research_note: str
    email: str
    linkedin: str
    draft_provider: str
    critique_provider: str
    steps: list[str]
    notes: list[str]


# --------------------------------------------------------------------------- #
# Agent nodes
# --------------------------------------------------------------------------- #
def qualify_node(state: OutreachState) -> OutreachState:
    """Attach a lead score so the outreach can reference qualification signals."""
    state.setdefault("steps", []).append("qualify")
    state.setdefault("notes", [])

    lead_data = state.get("lead_data")
    if lead_data:
        try:
            result = score_lead(lead_data, use_llm_explanation=False)
            state["score"] = int(result["final_score"])
            state["label"] = str(result["label"])
            state["score_source"] = "lead_scoring_model"
            return state
        except Exception as exc:  # pragma: no cover - defensive
            state["notes"].append(f"Lead scoring failed, using neutral score. {exc}")

    state["score"] = 70
    state["label"] = "Orta Potansiyel"
    state["score_source"] = "default"
    return state


def research_node(state: OutreachState) -> OutreachState:
    """Retrieve BizPilot value props from the RAG corpus to ground the message."""
    state.setdefault("steps", []).append("research")
    state["research"] = []
    state["research_note"] = ""

    if not state.get("use_rag", True):
        state["research_note"] = "RAG research skipped."
        return state

    query = (
        f"BizPilot AI value proposition for {state.get('pain_point', '')} "
        "lead qualification outreach automation pricing plans"
    )
    try:
        rows = rag_retrieve(query, top_k=3)
        for row in rows:
            metadata = row.get("metadata", {})
            state["research"].append(
                {
                    "title": str(metadata.get("title", metadata.get("document_type", "context"))),
                    "snippet": _compact(row.get("text", ""), 320),
                    "source_url": str(metadata.get("source_url", "")),
                }
            )
    except Exception as exc:
        state["research_note"] = f"RAG research unavailable, drafting without it. {exc}"
    return state


def draft_node(state: OutreachState) -> OutreachState:
    """Generate the first cold email + LinkedIn draft."""
    state.setdefault("steps", []).append("draft")

    if not state.get("use_llm", True):
        _apply_template_draft(state)
        state["draft_provider"] = "template"
        return state

    prompt = _build_draft_prompt(state)
    llm = call_configured_llm(prompt, OUTREACH_SYSTEM_PROMPT, max_tokens=600, clean_response=False)

    if llm["llm_used"]:
        parsed = _parse_outreach_json(llm["text"])
        if parsed:
            state["email"] = parsed.get("email", "").strip()
            state["linkedin"] = parsed.get("linkedin", "").strip()
            state["draft_provider"] = f"llm:{llm['provider']}"
            return state
        state.setdefault("notes", []).append("LLM draft was not valid JSON, used template.")
    else:
        state.setdefault("notes", []).append(f"LLM draft unavailable: {llm['error']}")

    _apply_template_draft(state)
    state["draft_provider"] = "template_fallback"
    return state


def critique_node(state: OutreachState) -> OutreachState:
    """Agentic refine step: review and tighten the draft once."""
    state.setdefault("steps", []).append("critique")
    state["critique_provider"] = "skipped"

    if not state.get("use_llm", True):
        return state
    if state.get("draft_provider", "").startswith("template"):
        # Nothing to refine on a deterministic template draft.
        return state
    if not state.get("email") and not state.get("linkedin"):
        return state

    prompt = (
        "Review and improve this outreach. Keep the cold email under 130 words and "
        "the LinkedIn message under 60 words. Make the first line specific to the "
        "prospect, keep one clear call to action, and remove filler. Do not invent "
        "facts. Return only JSON with keys \"email\" and \"linkedin\".\n\n"
        f"Current draft JSON:\n{json.dumps({'email': state.get('email', ''), 'linkedin': state.get('linkedin', '')}, ensure_ascii=False)}"
    )
    llm = call_configured_llm(prompt, CRITIQUE_SYSTEM_PROMPT, max_tokens=600, clean_response=False)
    if llm["llm_used"]:
        parsed = _parse_outreach_json(llm["text"])
        if parsed and (parsed.get("email") or parsed.get("linkedin")):
            state["email"] = parsed.get("email", state.get("email", "")).strip()
            state["linkedin"] = parsed.get("linkedin", state.get("linkedin", "")).strip()
            state["critique_provider"] = f"llm:{llm['provider']}"
            return state
    state.setdefault("notes", []).append("Critique step skipped or failed; kept first draft.")
    return state


# --------------------------------------------------------------------------- #
# Graph orchestration (LangGraph if available, else sequential runner)
# --------------------------------------------------------------------------- #
NODES: list[tuple[str, Callable[[OutreachState], OutreachState]]] = [
    ("qualify", qualify_node),
    ("research", research_node),
    ("draft", draft_node),
    ("critique", critique_node),
]


def _build_langgraph_app():  # pragma: no cover - only runs if langgraph installed
    from langgraph.graph import END, StateGraph

    graph = StateGraph(OutreachState)
    for name, fn in NODES:
        graph.add_node(name, fn)
    graph.set_entry_point(NODES[0][0])
    for (name, _), (next_name, _) in zip(NODES, NODES[1:]):
        graph.add_edge(name, next_name)
    graph.add_edge(NODES[-1][0], END)
    return graph.compile()


def generate_outreach(
    company: str,
    contact: str,
    pain_point: str,
    lead_data: dict[str, Any] | None = None,
    use_rag: bool = True,
    use_llm: bool = True,
) -> dict[str, Any]:
    """Run the agentic outreach graph and return the drafts + trace."""
    load_env_file()
    state: OutreachState = {
        "company": company.strip() or "the prospect company",
        "contact": contact.strip() or "there",
        "pain_point": pain_point.strip() or "inbound lead response and sales productivity",
        "lead_data": lead_data or {},
        "use_rag": use_rag,
        "use_llm": use_llm,
        "steps": [],
        "notes": [],
    }

    orchestrator = "sequential"
    try:
        app = _build_langgraph_app()
        state = app.invoke(state)
        orchestrator = "langgraph"
    except Exception:
        # langgraph not installed or failed to build -> run nodes sequentially.
        for _, fn in NODES:
            state = fn(state)

    return {
        "orchestrator": orchestrator,
        "company": state.get("company", ""),
        "contact": state.get("contact", ""),
        "pain_point": state.get("pain_point", ""),
        "score": state.get("score"),
        "label": state.get("label"),
        "score_source": state.get("score_source"),
        "email": state.get("email", ""),
        "linkedin": state.get("linkedin", ""),
        "draft_provider": state.get("draft_provider", ""),
        "critique_provider": state.get("critique_provider", ""),
        "research": state.get("research", []),
        "research_note": state.get("research_note", ""),
        "steps": state.get("steps", []),
        "notes": state.get("notes", []),
    }


# --------------------------------------------------------------------------- #
# Prompt + template helpers
# --------------------------------------------------------------------------- #
def _build_draft_prompt(state: OutreachState) -> str:
    research_lines = []
    for index, item in enumerate(state.get("research", []), start=1):
        research_lines.append(f"[{index}] {item['title']}: {item['snippet']}")
    research_block = "\n".join(research_lines) if research_lines else "No extra product context retrieved."

    payload = {
        "prospect_company": state.get("company"),
        "contact_name": state.get("contact"),
        "observed_need": state.get("pain_point"),
        "lead_score": state.get("score"),
        "lead_priority": state.get("label"),
    }

    return (
        "Write B2B outreach for BizPilot AI, an agentic RAG assistant that answers "
        "company-document questions, qualifies inbound leads, and drafts outreach.\n"
        "Use the prospect details and product context below. Personalize the first "
        "line, keep the cold email under 140 words and the LinkedIn message under 60 "
        "words, include one clear call to action, and do not invent metrics.\n"
        "Return ONLY JSON with keys \"email\" and \"linkedin\".\n\n"
        f"Prospect details JSON:\n{json.dumps(payload, ensure_ascii=False)}\n\n"
        f"BizPilot product context:\n{research_block}"
    )


def _apply_template_draft(state: OutreachState) -> None:
    company = state.get("company", "the prospect company")
    contact = state.get("contact", "there")
    pain_point = state.get("pain_point", "inbound lead response")
    score = state.get("score", 70)
    label = state.get("label", "")

    state["email"] = (
        f"Subject: Helping {company} prioritize inbound leads\n\n"
        f"Hi {contact},\n\n"
        f"I noticed {company} may benefit from improving {pain_point}. BizPilot AI "
        "helps sales teams answer product questions from company documents, qualify "
        "inbound leads, and draft personalized outreach from one workspace.\n\n"
        f"Based on current qualification signals, this prospect scores {score}/100"
        f"{f' ({label})' if label else ''}.\n\n"
        "Would you be open to a short conversation this week?\n\n"
        "Best,\nBizPilot AI Team"
    )
    state["linkedin"] = (
        f"Hi {contact}, I'm building BizPilot AI for digital business development. "
        "It helps teams qualify leads, answer company-document questions, and draft "
        f"outreach faster. Thought it could fit {company}'s {pain_point} workflow. "
        "Open to a quick chat?"
    )


def _parse_outreach_json(text: str) -> dict[str, str] | None:
    text = text.strip()
    start = text.find("{")
    end = text.rfind("}")
    if start == -1 or end == -1 or end <= start:
        return None
    try:
        data = json.loads(text[start : end + 1])
    except json.JSONDecodeError:
        return None
    if not isinstance(data, dict):
        return None
    return {"email": str(data.get("email", "")), "linkedin": str(data.get("linkedin", ""))}


def _compact(text: str, max_chars: int) -> str:
    compact = " ".join(text.split())
    if len(compact) > max_chars:
        compact = compact[:max_chars].rstrip() + "..."
    return compact


def _format_cli_output(result: dict[str, Any]) -> str:
    lines = [
        f"Orchestrator: {result['orchestrator']}",
        f"Steps: {' -> '.join(result['steps'])}",
        f"Lead score: {result['score']}/100 ({result['label']}) [{result['score_source']}]",
        f"Draft provider: {result['draft_provider']} | Critique: {result['critique_provider']}",
    ]
    if result["research_note"]:
        lines.append(f"Research note: {result['research_note']}")
    if result["notes"]:
        lines.append("Notes: " + " | ".join(result["notes"]))
    lines.extend(["", "=== Cold Email ===", result["email"], "", "=== LinkedIn ===", result["linkedin"]])
    return "\n".join(lines)


def main() -> None:
    parser = argparse.ArgumentParser(description="BizPilot AI agentic outreach generator.")
    parser.add_argument("--company", default="Northstar CRM Solutions")
    parser.add_argument("--contact", default="Aarav")
    parser.add_argument("--need", default="inbound lead response and sales team productivity")
    parser.add_argument("--no-rag", action="store_true", help="Skip the RAG research node.")
    parser.add_argument("--no-llm", action="store_true", help="Use the deterministic template draft.")
    args = parser.parse_args()

    result = generate_outreach(
        company=args.company,
        contact=args.contact,
        pain_point=args.need,
        lead_data={
            "Lead Origin": "Lead Add Form",
            "Lead Source": "Google",
            "Do Not Email": "No",
            "What is your current occupation": "Working Professional",
            "TotalVisits": 6,
            "Total Time Spent on Website": 1250,
            "Page Views Per Visit": 3.5,
            "Last Activity": "SMS Sent",
        },
        use_rag=not args.no_rag,
        use_llm=not args.no_llm,
    )
    print(_format_cli_output(result))


if __name__ == "__main__":
    main()
