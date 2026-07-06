# Week 1 Project Proposal

## Project Title

BizPilot AI: An Agentic RAG-Powered Chatbot for Digital Business Development

## Student Context

This project is being developed as an internship project at Graphic Era University. The work follows the objectives, tools, timeline, and deliverables provided by the professor.

## Problem Statement

Digital business development teams often work with scattered information: product sheets, pricing documents, FAQs, past proposals, lead records, and public competitor information. This makes it difficult to answer sales questions quickly, prioritize the right leads, write personalized outreach, and evaluate whether AI-generated answers are grounded in reliable sources.

BizPilot AI aims to solve this by building a shareable web application that combines retrieval-augmented generation, lead scoring, agentic outreach drafting, lightweight competitor intelligence, and RAG-specific evaluation.

## Project Objectives

1. Build a RAG pipeline that lets the chatbot answer questions grounded in company documents such as product sheets, pricing, past proposals, and FAQs, with cited sources.
2. Design a lead-qualification module that scores and ranks inbound leads using a hybrid rule-based + machine learning model, explained in natural language by the LLM.
3. Implement an agentic outreach generator that drafts personalized cold emails and LinkedIn messages using retrieved prospect and company context.
4. Add a lightweight competitor-intelligence retriever that pulls and summarizes publicly available competitor information on demand.
5. Evaluate the system using RAG-specific metrics: faithfulness, context precision, and answer relevancy.
6. Deploy the chatbot as a live, shareable web app with a clean UI and a documented GitHub repository.

## Proposed Technology Stack

- LLM: Llama 3.1 / Mistral 7B through Groq or Ollama, or GPT-4o-mini / Gemini 1.5 Flash API
- Orchestration: LangChain for RAG chains, plus LangGraph or CrewAI for agentic outreach and routing
- Vector database: ChromaDB first, FAISS as fallback
- Embeddings: sentence-transformers all-MiniLM-L6-v2 first, OpenAI text-embedding-3-small as optional API alternative
- Lead scoring: scikit-learn Logistic Regression baseline, XGBoost as improvement option
- Web retrieval: Tavily API first, SerpAPI as fallback
- Evaluation: RAGAS using faithfulness, context precision, and answer relevancy
- Backend: Python
- UI: Streamlit
- Deployment: Hugging Face Spaces or Render free tier
- Version control: Git and GitHub

## MVP Architecture

1. User opens the Streamlit web app.
2. A routing layer will direct the user request to one of the modules: RAG Q&A, lead qualification, outreach generation, or competitor intelligence.
3. For RAG Q&A, company documents will be loaded, chunked, embedded, stored in ChromaDB/FAISS, retrieved, and cited in the final answer.
4. For lead qualification, the trained ML model will estimate conversion probability and a rule-based layer will adjust the score.
5. For outreach, retrieved prospect/company context will be used to draft a cold email and LinkedIn message.
6. For competitor intelligence, Tavily or SerpAPI will retrieve public web information and the LLM will summarize it with source links.
7. For evaluation, RAGAS will measure faithfulness, context precision, and answer relevancy.

## Week 1 Work Completed

Dates: 06 July - 12 July 2026

### 1. Requirement Study

The professor-provided objectives, tools, timeline, and deliverables were reviewed and stored in `anagorev.md`. The project direction remains focused on BizPilot AI and digital business development.

### 2. Tool Setup

A Python project structure was created with:

- `requirements.txt`
- `.env.example`
- `.gitignore`
- Streamlit configuration under `.streamlit/config.toml`
- Git and GitHub repository setup

The working local environment currently supports Streamlit, pandas, scikit-learn, NumPy, openpyxl, and joblib for Week 1 dataset preparation and demo UI.

### 3. Sample Company Documents

Synthetic sample company documents were created under `data/company_docs/`:

- Product sheet
- Pricing sheet
- FAQ
- Past proposal

These documents will be used in the next step for the RAG ingestion and retrieval pipeline.

### 4. Kaggle Lead-Scoring Dataset

The selected dataset is:

- Dataset: Lead Scoring Dataset
- Source: Kaggle
- Local raw file: `data/lead_scoring/raw/Lead Scoring.csv`
- Data dictionary: `data/lead_scoring/raw/Leads Data Dictionary.xlsx`
- Target column: `Converted`

The raw dataset contains 9,240 rows and 37 columns. After cleaning, the prepared dataset contains 7,484 rows and 28 columns.

Cleaning decisions:

- Replaced `Select` values with missing values.
- Removed ID columns.
- Removed likely post-lead/manual scoring columns to reduce leakage risk.
- Preserved useful lead activity and source columns for modeling.

### 5. Lead-Scoring Baseline

A Logistic Regression baseline model was trained using scikit-learn. The model predicts whether a lead will convert.

Baseline results:

- Accuracy: 0.7902
- Precision: 0.7261
- Recall: 0.7555
- F1: 0.7405
- ROC-AUC: 0.8703

Generated files:

- Training script: `src/lead_scoring_baseline.py`
- Prediction wrapper: `src/lead_scoring_predictor.py`
- Baseline report: `reports/lead_scoring_baseline.md`

The prediction wrapper produces:

- ML conversion probability
- ML score out of 100
- Rule-based adjustment
- Final hybrid lead score
- Potential label
- Short explanation

### 6. Streamlit MVP UI

A professional Streamlit interface was created in `app.py`. Current UI features:

- Dashboard
- Lead Qualification screen
- Company Documents workspace
- Outreach Preview
- Roadmap
- Turkish / English language switch

The local app was verified at:

- `http://127.0.0.1:8501`

### 7. GitHub Repository

The repository was initialized, committed, and pushed to GitHub:

- https://github.com/SemihSan/Graphic-Era-University-Internship-Project---BizPilot-AI-

## Week 1 Deliverables

Deadline: Sunday, 12 July 2026

Completed:

- Project proposal
- Dataset selected, downloaded locally, cleaned, and modeled
- Sample company documents for the RAG pipeline
- Literature review
- Streamlit MVP UI
- GitHub repository with structured files

## Next Week Direction

The next technical step is to implement the real RAG Q&A module:

1. Load company documents.
2. Split documents into chunks.
3. Generate embeddings with sentence-transformers all-MiniLM-L6-v2.
4. Store embeddings in ChromaDB.
5. Retrieve relevant chunks for a user question.
6. Generate an answer with citations.

This will move the system from document preview to true retrieval-augmented generation.

## Risks and Mitigation

- API key availability: keep Groq/Ollama/OpenAI/Gemini options flexible within the professor-approved stack.
- Dataset quality: use Logistic Regression as baseline and keep XGBoost as an improvement option.
- RAG hallucination: require retrieved context and source citations, then evaluate with RAGAS.
- Scope growth: keep the MVP simple first, then add polish and additional agentic behavior.
