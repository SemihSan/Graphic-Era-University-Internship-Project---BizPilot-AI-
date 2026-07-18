from __future__ import annotations

import json
from pathlib import Path


ROOT_DIR = Path(__file__).resolve().parents[1]
OUTPUT_PATH = ROOT_DIR / "data" / "company_docs" / "bizpilot_synthetic_corpus.jsonl"

COMPANY = "BizPilot AI"
RETRIEVED_DATE = "2026-07-15"
CORPUS_TYPE = "synthetic company documentation"

PLAN_FACTS = (
    "BizPilot AI has four commercial packages. Starter is USD 49 per month for small teams and includes "
    "company-document Q&A, basic lead scoring, and 100 outreach drafts per month. Growth is USD 149 per month "
    "for growing sales and marketing teams and includes everything in Starter, competitor summaries, custom "
    "lead-scoring rules, CRM-style batch scoring, and 1,000 outreach drafts per month. Scale is USD 399 per month "
    "for larger teams and includes advanced analytics, RAGAS evaluation reports, priority onboarding, and 5,000 "
    "outreach drafts per month. Enterprise is custom priced after a discovery call and adds SSO, private deployment, "
    "custom connectors, and dedicated success support."
)

SHARED_PRODUCT_FACTS = (
    "BizPilot AI is an agentic RAG-powered chatbot for digital business development. It combines company-document "
    "question answering, lead qualification, personalized outreach generation, competitor-intelligence retrieval, "
    "and RAG evaluation in one Streamlit web application. The system is intended for business development "
    "representatives, sales managers, startup founders, and marketing teams that need grounded answers and faster "
    "lead follow-up."
)

LEAD_SCORING_FACTS = (
    "The lead qualification module uses a hybrid model. A scikit-learn Logistic Regression model predicts the base "
    "conversion probability from CRM-style fields, and a rule-based layer adjusts the score using business signals "
    "such as email permission, lead origin, occupation, visit count, time spent on website, and page views per visit. "
    "The final score is expressed from 0 to 100 and labeled Low Potential, Medium Potential, or High Potential. "
    "The LLM is not responsible for the numeric score; it explains the score in natural language after the model "
    "and rules finish."
)

RAG_FACTS = (
    "The RAG pipeline ingests JSONL company documentation, splits each record into chunks, generates embeddings "
    "with sentence-transformers/all-MiniLM-L6-v2, stores vectors in ChromaDB, retrieves the most relevant chunks "
    "for a user question, and asks the configured LLM to answer only from the retrieved context. Answers must include "
    "citation markers and source metadata. If no relevant context is found, the chatbot should say that the answer "
    "is not available in the provided company documents."
)

OUTREACH_FACTS = (
    "The outreach module drafts cold emails and LinkedIn messages using the retrieved company context, lead score, "
    "prospect role, industry, pain point, and recommended next action. Outreach drafts must avoid unsupported claims, "
    "must use a helpful business-development tone, and should include one clear call to action."
)

COMPETITOR_FACTS = (
    "The competitor-intelligence module is designed to retrieve public competitor information on demand through a "
    "web retrieval API such as Tavily or SerpAPI, summarize the relevant findings, and show source links. It is "
    "lightweight and should not replace a full market research platform."
)


def paragraph(*parts: str) -> str:
    return " ".join(part.strip() for part in parts if part.strip())


def make_record(doc_id: str, document_type: str, title: str, content: str) -> dict[str, str]:
    return {
        "doc_id": doc_id,
        "company": COMPANY,
        "document_type": document_type,
        "title": title,
        "source_url": f"synthetic://bizpilot-ai/{doc_id}",
        "retrieved_date": RETRIEVED_DATE,
        "corpus_type": CORPUS_TYPE,
        "content": content,
    }


def build_records() -> list[dict[str, str]]:
    specs = [
        (
            "bizpilot_product_overview",
            "product overview",
            "BizPilot AI product overview",
            [
                SHARED_PRODUCT_FACTS,
                RAG_FACTS,
                LEAD_SCORING_FACTS,
                "The MVP prioritizes a simple working workflow before adding advanced automation. A user should be able to ask grounded product questions, score a lead, review the explanation, and draft outreach from the same application. The system is intentionally designed for digital business development rather than healthcare, finance, or unrelated domains.",
            ],
        ),
        (
            "bizpilot_user_personas",
            "buyer personas",
            "Primary users and buyer personas",
            [
                "The primary user personas are business development representatives, sales development representatives, sales managers, startup founders, and small marketing teams. Business development representatives need fast answers about pricing, features, proposal details, and qualification fit while speaking with prospects.",
                "Sales managers need ranked leads, clear explanations, and batch scoring output from CRM-style datasets. Startup founders need low-cost tooling that combines company knowledge, lead prioritization, and outreach drafting without requiring a large operations team.",
                "Marketing teams use the system to understand which inbound leads show stronger intent. Strong signals include form submission, allowed email outreach, working professional occupation, multiple visits, long website time, and high page views per visit.",
            ],
        ),
        (
            "bizpilot_pricing_summary",
            "pricing",
            "Pricing summary and plan positioning",
            [
                PLAN_FACTS,
                "Starter is best for a two-person team validating AI-assisted business development. Growth is the recommended plan for a growing sales team because it combines competitor summaries, custom scoring rules, and enough outreach drafts for active pipeline work. Scale is best for teams that need analytics, evaluation reports, and priority onboarding.",
                "Annual billing gives a 15 percent discount. Academic demo pricing may be offered for internship and classroom evaluation. Enterprise pricing is not listed publicly because it depends on deployment model, connector scope, SSO requirements, and security review.",
            ],
        ),
        (
            "bizpilot_pricing_faq",
            "FAQ",
            "Pricing frequently asked questions",
            [
                PLAN_FACTS,
                "Monthly billing renews every month and can be changed before the next billing cycle. Annual billing charges once for the year and applies the 15 percent discount. Starter users can upgrade to Growth without losing existing documents, lead scores, or outreach drafts.",
                "Competitor summaries are not included in Starter because they require external web retrieval. RAGAS evaluation reports are included in Scale because they are intended for teams that measure faithfulness, context precision, and answer relevancy on a regular basis.",
            ],
        ),
        (
            "bizpilot_feature_matrix",
            "feature comparison",
            "Feature matrix by plan",
            [
                "Starter includes document Q&A, ChromaDB indexing, basic lead scoring, English-only outreach templates, and email support. Growth adds competitor summaries, custom lead scoring rules, CRM-style batch scoring, prompt-only lead qualification, bilingual UI labels, and 1,000 outreach drafts per month.",
                "Scale adds advanced analytics, saved RAG evaluation sets, RAGAS reports, priority onboarding, team-level reporting, and 5,000 outreach drafts per month. Enterprise adds SSO, private deployment, custom connectors, dedicated support, and security review assistance.",
                "The most common upgrade path is Starter to Growth after the team validates the RAG Q&A workflow. Growth to Scale usually happens when managers need evaluation reports and repeatable quality measurements.",
            ],
        ),
        (
            "bizpilot_rag_architecture",
            "technical architecture",
            "RAG architecture and retrieval flow",
            [
                RAG_FACTS,
                "Each JSONL record contains a document ID, company name, document type, title, source URL, retrieved date, corpus type, and cleaned content. The chunker uses paragraph-aware splitting so that related sentences stay together when possible. ChromaDB stores chunk text, embeddings, and metadata such as source ID, company, document type, title, and chunk index.",
                "The retrieval step uses top-k nearest vector search and a maximum distance threshold. This threshold prevents nonsense questions from forcing irrelevant context into the answer. The answer layer then sends only the retrieved context to the LLM with instructions to cite sources and avoid hallucination.",
            ],
        ),
        (
            "bizpilot_rag_chunking_policy",
            "technical guide",
            "Chunking policy for company documents",
            [
                "BizPilot AI uses chunking because long documents are too broad to embed as a single vector. A single vector for a full policy, pricing page, or proposal would blur several topics together. Smaller chunks make retrieval more precise and allow the chatbot to combine information from product, pricing, FAQ, and support documents.",
                "The prototype uses approximately 900 characters per chunk with no overlap for compact synthetic records. For long PDFs or HTML pages, the recommended production setup is a recursive text splitter with overlap between 100 and 200 characters. Overlap is useful when an important sentence crosses a chunk boundary, but it also increases duplicate retrieval.",
                "For professor demonstration, the synthetic corpus is intentionally larger than the first public corpus. Multi-part questions should retrieve four or five related chunks so the LLM has to combine pricing, feature, policy, and case-study evidence instead of answering from one paragraph.",
            ],
        ),
        (
            "bizpilot_rag_prompt_policy",
            "prompt policy",
            "RAG answer prompt policy",
            [
                "The RAG Q&A screen lets the user provide an answer prompt for tone, format, and business focus. For example, the user may ask the answer to be written for a sales manager, summarized in bullet points, or focused on onboarding risk. This prompt is allowed to shape presentation but must not override the retrieved evidence.",
                "The system prompt tells the LLM to answer only from retrieved company-document context. If context is insufficient, the answer should say that the information is not available in the provided documents. The model should not invent prices, discounts, integration names, customer claims, or security promises.",
                "Citation markers such as [1], [2], and [3] should be attached to factual claims. The source list below the answer shows the synthetic source URL, source ID, document type, chunk index, and distance score.",
            ],
        ),
        (
            "bizpilot_lead_scoring_overview",
            "lead scoring",
            "Lead scoring model overview",
            [
                LEAD_SCORING_FACTS,
                "The baseline model is trained on a public Kaggle lead-scoring dataset. Data cleaning replaces placeholder values, removes leakage-prone manual labels, imputes missing values, scales numeric fields, one-hot encodes categorical fields, and trains Logistic Regression with class balancing.",
                "The model outputs a probability of conversion. A probability of 0.72 becomes an ML score of 72. The rules may then increase or decrease the score. A final score of 75 or above is High Potential, 50 to 74 is Medium Potential, and below 50 is Low Potential.",
            ],
        ),
        (
            "bizpilot_lead_prompt_qualification",
            "lead qualification",
            "Prompt-only lead qualification",
            [
                "The Lead Qualification screen supports prompt-only scoring. The user can write a natural-language lead description instead of filling the structured form. The parser extracts CRM-style fields such as lead origin, lead source, email permission, occupation, total visits, time spent on website, page views per visit, last activity, and last notable activity.",
                "If the prompt contains no recognizable CRM-style fields, the system warns the user instead of scoring a random sentence. This prevents misleading scores for unrelated text. If the prompt contains useful fields but not every possible field, the model still scores using the extracted values and treats missing model columns as missing values through the preprocessing pipeline.",
                "A good prompt example is: Lead came from Lead Add Form via Google, email allowed, working professional, 6 visits, spent 1250 seconds, 3.5 page views per visit, last activity SMS Sent. This should produce a strong score because form submission, email permission, professional occupation, visits, time, and page views are positive signals.",
            ],
        ),
        (
            "bizpilot_lead_rules",
            "lead scoring rules",
            "Rule-based adjustment logic",
            [
                "The rule layer is intentionally transparent. Email allowed adds 4 points, while Do Not Email subtracts 10 points. Lead Add Form adds 8 points because a form submission suggests stronger intent than a passive page visit. Working Professional adds 6 points, while Student or Unemployed subtracts 4 points.",
                "Website behavior also affects the score. Spending 900 seconds or more on the website adds 7 points, while 60 seconds or less subtracts 6 points. Five or more visits adds 4 points, one or fewer visits subtracts 3 points, and page views per visit of 3 or more adds 3 points.",
                "Rules are not a replacement for the ML model. They act as a business-readable adjustment layer so the final explanation can show why the score moved up or down.",
            ],
        ),
        (
            "bizpilot_lead_batch_scoring",
            "CRM workflow",
            "CRM-style batch lead scoring",
            [
                "The batch scoring workflow reads a CRM-style CSV file, scores each row using the saved Logistic Regression pipeline, applies rule adjustments, and writes a scored output CSV. The output includes ML probability, ML score, rule adjustment, final score, label, explanation, explanation provider, and any LLM error.",
                "Sales managers use the output to prioritize follow-up. High Potential leads should receive immediate outreach, Medium Potential leads should enter nurture, and Low Potential leads should wait until stronger buying intent appears.",
                "The batch script can optionally call the configured LLM provider for natural-language explanations. If the provider times out or returns a bad response, the system uses a deterministic template fallback so batch scoring still completes.",
            ],
        ),
        (
            "bizpilot_llm_explanation_policy",
            "LLM policy",
            "LLM explanation policy for scores",
            [
                "The LLM explains lead scores but does not calculate them. Numeric scoring is performed by the ML model and rule layer. The LLM receives a JSON summary of the lead profile and score breakdown, then writes a concise sales-focused explanation.",
                "The explanation should mention the ML base score, rule-based adjustment, final priority, top reasons, and recommended next action. It must not invent missing CRM data. If the LLM provider is unavailable, a template explanation is used.",
                "Supported providers include PersorAI, G0I, Groq, and local Ollama depending on available API keys. Provider errors are recorded so the demo can show whether a row was explained by the LLM or by fallback.",
            ],
        ),
        (
            "bizpilot_outreach_overview",
            "outreach generation",
            "Personalized outreach generator overview",
            [
                OUTREACH_FACTS,
                "The outreach generator should use the lead score and retrieved company context. A High Potential lead may receive a direct call-to-action for a discovery meeting. A Medium Potential lead may receive a softer nurture message that offers a resource or product comparison. A Low Potential lead should not be pushed aggressively.",
                "Cold email drafts should include a relevant observation, a short value statement, one proof point grounded in retrieved context, and one clear next step. LinkedIn messages should be shorter and more conversational while still avoiding unsupported claims.",
            ],
        ),
        (
            "bizpilot_outreach_templates",
            "outreach templates",
            "Cold email and LinkedIn templates",
            [
                "A recommended cold email format is: subject line, personalized opening, pain point, BizPilot AI value statement, score-based reason for priority, and a short meeting request. The message should stay under 140 words unless the user asks for a longer proposal-style email.",
                "A recommended LinkedIn message format is: greeting, one sentence about the prospect context, one sentence about BizPilot AI, and one question. LinkedIn messages should not include long pricing detail unless the user specifically asks for pricing.",
                "The system should cite retrieved context internally when drafting, but the final outreach message normally does not include bracketed citations because it is customer-facing. The UI can show the sources separately for review.",
            ],
        ),
        (
            "bizpilot_competitor_intel_overview",
            "competitor intelligence",
            "Competitor intelligence retriever overview",
            [
                COMPETITOR_FACTS,
                "A typical competitor query is: summarize public information about a CRM competitor's pricing, AI features, and support options. The retriever should collect public snippets, summarize only what was retrieved, and show links. It should avoid legal, financial, or private claims that are not in the retrieved material.",
                "Competitor intelligence is separate from internal company-document RAG. Internal RAG uses the local ChromaDB index. Competitor intelligence uses live public web retrieval on demand. Both modules follow the same grounding principle: retrieve first, summarize second, cite sources.",
            ],
        ),
        (
            "bizpilot_evaluation_ragas",
            "evaluation",
            "RAGAS evaluation plan",
            [
                "BizPilot AI will evaluate the RAG pipeline with RAGAS metrics: faithfulness, context precision, and answer relevancy. Faithfulness checks whether the generated answer is supported by retrieved context. Context precision checks whether retrieved chunks are useful and focused. Answer relevancy checks whether the final answer addresses the user question.",
                "A small evaluation set should include pricing questions, feature comparison questions, onboarding questions, lead qualification questions, and policy questions. Each question should have expected supporting documents so retrieval quality can be inspected.",
                "The Scale plan includes saved RAGAS evaluation reports because teams using production RAG need repeatable quality measurement rather than one-time manual inspection.",
            ],
        ),
        (
            "bizpilot_security_overview",
            "security",
            "Security and privacy overview",
            [
                "BizPilot AI is designed for business-development documents and CRM-style lead records. The MVP should not store highly sensitive personal data, medical data, payment card data, or private secrets in the RAG corpus. API keys are stored in a local .env file and should never be committed to GitHub.",
                "Enterprise customers can request private deployment, SSO, and custom connector review. Scale customers receive priority onboarding and guidance on document hygiene. Starter and Growth users are responsible for uploading only safe company documents.",
                "The system should show citations so users can verify answers before sharing them with prospects. This is especially important for pricing, security, legal, or contractual claims.",
            ],
        ),
        (
            "bizpilot_data_governance",
            "data governance",
            "Document governance and source control",
            [
                "Each company-document record must have a source ID, title, document type, and source URL. Synthetic documents use synthetic:// URLs so reviewers can see that the corpus is generated and not scraped from a private company. Public documents should use real URLs when allowed by the source and project policy.",
                "The active synthetic corpus is used to demonstrate RAG behavior with many consistent documents. The earlier public SaaS corpus is kept as a small reference corpus, but it is not large enough to demonstrate multi-chunk retrieval well.",
                "When real company documents become available, they can replace the synthetic corpus without changing the ingestion, chunking, embedding, indexing, or Q&A architecture.",
            ],
        ),
        (
            "bizpilot_onboarding_plan",
            "onboarding",
            "Customer onboarding plan",
            [
                "Onboarding starts with a discovery call to identify the customer's sales process, common prospect questions, key documents, CRM fields, and outreach approval rules. The team then uploads product sheets, pricing notes, FAQs, proposals, security documents, and case studies into the RAG corpus.",
                "For Starter, onboarding is self-guided with email support. Growth includes a guided setup checklist and custom lead-scoring rules. Scale includes priority onboarding, RAGAS evaluation setup, and analytics review. Enterprise includes dedicated success support and connector planning.",
                "A successful onboarding outcome is a working chatbot that answers pricing and product questions with citations, scores sample leads, explains scores, and drafts outreach for a realistic prospect scenario.",
            ],
        ),
        (
            "bizpilot_support_policy",
            "support policy",
            "Support policy by plan",
            [
                "Starter includes email support with a target response time of two business days. Growth includes faster email support and configuration guidance for custom scoring rules. Scale includes priority support, onboarding sessions, and review of evaluation reports. Enterprise includes dedicated success support based on contract terms.",
                "Support can help with RAG index rebuilds, document formatting, lead scoring workflow questions, and API provider configuration. Support does not guarantee external LLM provider uptime because providers such as PersorAI, G0I, Groq, or Ollama may fail independently.",
                "When an LLM provider fails, BizPilot AI should degrade gracefully. Lead scoring can use template explanations and RAG Q&A can use extractive fallback with citations.",
            ],
        ),
        (
            "bizpilot_integrations_crm",
            "integrations",
            "CRM and data integrations",
            [
                "The MVP supports CSV-style CRM data for lead scoring. Future integrations may include HubSpot, Pipedrive, Salesforce, Google Sheets, and webhook-based lead capture. Growth is the first plan that includes CRM-style batch scoring in the standard package.",
                "A CRM integration should map source fields to the model's expected columns, including Lead Origin, Lead Source, Do Not Email, TotalVisits, Total Time Spent on Website, Page Views Per Visit, occupation, Last Activity, and Last Notable Activity.",
                "Enterprise customers can request custom connectors and private deployment. Connector scope affects pricing because each CRM has different authentication, field mapping, and rate-limit behavior.",
            ],
        ),
        (
            "bizpilot_integrations_docs",
            "integrations",
            "Document source integrations",
            [
                "Company documents can come from Markdown, JSONL, PDFs, help-center exports, proposal repositories, and knowledge-base pages. The current MVP uses JSONL because it keeps content and metadata together in a simple format.",
                "A production ingestion workflow should normalize source text, remove navigation noise, keep source URLs, preserve titles, and avoid mixing unrelated companies in the same document record. Clean metadata improves citations and reviewer trust.",
                "Document updates require rebuilding the ChromaDB index. If documents change frequently, a scheduled ingestion job can refresh embeddings and replace outdated chunks.",
            ],
        ),
        (
            "bizpilot_case_study_northstar",
            "case study",
            "Northstar CRM Solutions case study",
            [
                "Northstar CRM Solutions is a synthetic 48-person sales consultancy that tested BizPilot AI Growth for inbound lead triage. Before BizPilot AI, the team manually read form submissions, checked pricing questions, and wrote outreach drafts in spreadsheets.",
                "After onboarding product FAQs, pricing notes, and proposal examples, the team used RAG Q&A to answer common questions about CRM automation, lead response time, and reporting. They used lead scoring to rank new demo requests and prioritized leads with form submission, email permission, working professional profile, and long website sessions.",
                "The case study outcome was faster follow-up, more consistent explanations for why a lead was prioritized, and cleaner outreach drafts. This is a synthetic example for RAG testing and should not be presented as a real customer claim.",
            ],
        ),
        (
            "bizpilot_case_study_edutech",
            "case study",
            "EduTech Growth Lab case study",
            [
                "EduTech Growth Lab is a synthetic education technology startup using BizPilot AI Starter during a product launch. The founder uploaded product notes, pricing assumptions, and FAQs to test whether a small team could answer prospect questions with citations.",
                "The team later upgraded to Growth because they needed competitor summaries and custom scoring rules. Growth helped them identify leads who came from lead forms, allowed email outreach, and spent more than 900 seconds reading product pages.",
                "The main lesson from the synthetic case study is that small teams can start with document Q&A and later add lead scoring, competitor summaries, and outreach generation as their pipeline grows.",
            ],
        ),
        (
            "bizpilot_case_study_manufacturing",
            "case study",
            "Manufacturing CRM pilot case study",
            [
                "A synthetic manufacturing software vendor piloted BizPilot AI Scale to support a distributed sales team. The team needed consistent answers about product modules, security review, onboarding, and pricing tiers.",
                "Scale was selected because it includes RAGAS evaluation reports, priority onboarding, advanced analytics, and 5,000 outreach drafts per month. Managers reviewed context precision and answer relevancy before allowing representatives to use the chatbot for prospect preparation.",
                "The pilot demonstrated why larger corpora matter. Questions about implementation timelines required retrieving onboarding, integration, pricing, and support policy chunks before the LLM could produce a reliable answer.",
            ],
        ),
        (
            "bizpilot_sales_objections",
            "sales enablement",
            "Common sales objections and responses",
            [
                "Common objection: We already use a CRM. Suggested response: BizPilot AI does not replace the CRM; it adds document-grounded Q&A, lead scoring explanations, and outreach drafting on top of CRM-style data. Growth and Scale are designed to work with CRM exports and future CRM connectors.",
                "Common objection: We do not trust AI answers. Suggested response: BizPilot AI retrieves context from company documents first and shows citations. The RAGAS evaluation plan measures faithfulness, context precision, and answer relevancy so teams can inspect quality.",
                "Common objection: We are too small for automation. Suggested response: Starter is designed for small teams and costs USD 49 per month. Teams can start with document Q&A and upgrade to Growth when they need competitor summaries and custom scoring rules.",
            ],
        ),
        (
            "bizpilot_roi_model",
            "ROI guide",
            "ROI model for sales teams",
            [
                "BizPilot AI's ROI argument is based on faster lead response, more consistent qualification, fewer repeated document searches, and faster first-draft outreach. For a small team, saving thirty minutes per representative per day can justify Starter or Growth if the saved time is used for qualified follow-up.",
                "Growth is usually justified when the team handles enough inbound leads that manual prioritization becomes slow. Scale is justified when managers also need evaluation reports, analytics, and repeatable quality checks.",
                "The ROI model should be positioned as an estimate, not a guarantee. Any customer-facing ROI statement should cite the assumptions used, such as number of representatives, hourly cost, lead volume, and current response time.",
            ],
        ),
        (
            "bizpilot_implementation_timeline",
            "implementation",
            "Implementation timeline",
            [
                "A simple Starter implementation can be completed in one day if documents are ready. The team uploads documents, builds the ChromaDB index, tests several RAG questions, and verifies citations. Growth implementation usually takes two to five days because custom rules, batch scoring, and outreach examples must be reviewed.",
                "Scale implementation may take one to two weeks because evaluation sets, analytics, onboarding sessions, and team review are included. Enterprise timelines depend on SSO, private deployment, and custom connector requirements.",
                "Implementation success depends more on document quality than on model choice. Clean product sheets, pricing notes, FAQs, and proposal examples produce better grounded answers than messy or outdated files.",
            ],
        ),
        (
            "bizpilot_admin_roles",
            "admin guide",
            "Admin roles and permissions",
            [
                "The MVP does not include full role-based access control, but the planned product has Admin, Manager, and Representative roles. Admins configure documents, API keys, and deployment settings. Managers review lead scoring outputs, RAGAS reports, and outreach quality. Representatives ask RAG questions, score leads, and draft outreach.",
                "Enterprise customers can request SSO and private deployment. In that setup, permissions should align with the customer's identity provider and CRM policies.",
                "For internship demonstration, role behavior is described in documentation but not fully enforced in the Streamlit MVP.",
            ],
        ),
        (
            "bizpilot_api_provider_setup",
            "setup guide",
            "LLM provider setup",
            [
                "BizPilot AI can use several professor-approved LLM routes depending on availability. Groq can run Llama or Mistral-style models when accessible. Ollama can run local models such as llama3.1:8b. OpenAI-compatible providers such as PersorAI or G0I can be used by setting provider name, base URL, model, and API key in the .env file.",
                "The system should never print API keys in logs or documentation. The .env.example file contains placeholder values only. If a key is accidentally exposed, it should be rotated immediately.",
                "Provider reliability can vary. For this reason, BizPilot AI includes fallback behavior for lead explanations and RAG answers.",
            ],
        ),
        (
            "bizpilot_streamlit_ui",
            "UI guide",
            "Streamlit UI guide",
            [
                "The Streamlit UI includes Dashboard, Lead Qualification, RAG Q&A, Outreach Preview, and Roadmap tabs. Dashboard summarizes project status. Lead Qualification supports prompt-only scoring, structured form scoring, and CRM-style batch output. RAG Q&A builds the ChromaDB index, asks questions, applies an optional answer prompt, and shows citations.",
                "Outreach Preview is currently template-based and will later use retrieved context and LLM generation more deeply. Roadmap describes competitor intelligence and RAGAS evaluation as next modules.",
                "The interface is intentionally simple so the internship MVP can be demonstrated quickly without needing a React frontend.",
            ],
        ),
        (
            "bizpilot_deployment_plan",
            "deployment",
            "Deployment plan",
            [
                "The professor-approved deployment options are Hugging Face Spaces or Render free tier. Streamlit is the preferred frontend because it is quick to deploy and fits the MVP. Environment variables must be configured on the deployment platform rather than committed to the repository.",
                "Before deployment, the repository should include README instructions, architecture diagram, requirements.txt, sample data, and clear notes about synthetic data. The ChromaDB index can be rebuilt at startup or generated during setup.",
                "A shareable deployment should avoid storing private customer documents or real API keys in the repository. Synthetic data is suitable for demonstration because it is safe and consistent.",
            ],
        ),
        (
            "bizpilot_risk_register",
            "risk register",
            "Project risks and mitigations",
            [
                "Risk: hallucinated answers. Mitigation: retrieve context first, require citations, use max-distance filtering, and add RAGAS evaluation. Risk: weak retrieval. Mitigation: create a larger synthetic corpus with repeated consistent concepts across product, pricing, FAQ, onboarding, and case-study documents.",
                "Risk: LLM provider outage. Mitigation: support multiple providers and fallback to extractive answers or template explanations. Risk: data leakage in lead scoring. Mitigation: remove manual labels and leakage-prone columns before training.",
                "Risk: professor rejects unrealistic data. Mitigation: mark the corpus as synthetic, keep facts consistent, use JSONL metadata, and generate enough records for multi-chunk retrieval.",
            ],
        ),
        (
            "bizpilot_academic_scope",
            "academic note",
            "Academic project scope note",
            [
                "BizPilot AI is an applied internship MVP rather than a new research algorithm. The contribution is integration: RAG Q&A with citations, hybrid lead scoring, LLM explanations, outreach generation, competitor retrieval, and RAGAS evaluation planning in one digital business development workflow.",
                "The project should remain strictly focused on digital business development. It should not move into healthcare, finance, or unrelated domains unless explicitly requested by the professor.",
                "Synthetic company data is used because real company documents may be unavailable or confidential. The synthetic corpus allows repeatable testing while preserving the structure of product sheets, pricing pages, FAQs, proposals, case studies, onboarding guides, and support policies.",
            ],
        ),
    ]

    records = []
    for doc_id, document_type, title, paragraphs in specs:
        content = "\n\n".join(paragraphs)
        records.append(make_record(doc_id, document_type, title, content))
    return records


def main() -> None:
    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    records = build_records()
    with OUTPUT_PATH.open("w", encoding="utf-8", newline="\n") as file:
        for record in records:
            file.write(json.dumps(record, ensure_ascii=False, separators=(",", ":")) + "\n")
    print(f"Wrote {len(records)} records to {OUTPUT_PATH}")


if __name__ == "__main__":
    main()
