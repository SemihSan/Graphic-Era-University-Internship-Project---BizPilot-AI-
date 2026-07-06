# Week 1 Project Proposal

## Project Title

BizPilot AI: An Agentic RAG-Powered Chatbot for Digital Business Development

## Student Context

This project is being developed as an internship project at Graphic Era University. The work follows the professor-provided objectives, tools, timeline, and deliverables.

## Problem Statement

Digital business development teams need fast access to accurate company knowledge, better lead prioritization, personalized outreach, and quick competitor summaries. Manual workflows are slow and inconsistent, especially when information is spread across product sheets, pricing documents, FAQs, past proposals, lead data, and public web sources.

BizPilot AI will address this by combining retrieval-augmented generation, lead scoring, agentic outreach, competitor-intelligence retrieval, and RAG evaluation into one shareable chatbot application.

## Objectives

1. Build a RAG pipeline that answers questions grounded in company documents such as product sheets, pricing, past proposals, and FAQs, with cited sources.
2. Design a lead-qualification module that scores and ranks inbound leads using a hybrid rule-based + machine learning model, explained in natural language by the LLM.
3. Implement an agentic outreach generator that drafts personalized cold emails and LinkedIn messages using retrieved prospect and company context.
4. Add a lightweight competitor-intelligence retriever that pulls and summarizes publicly available competitor information on demand.
5. Evaluate the system using RAG-specific metrics: faithfulness, context precision, and answer relevancy.
6. Deploy the chatbot as a live, shareable web app with a clean UI and a documented GitHub repository.

## Proposed MVP Stack

- UI: Streamlit
- Backend language: Python
- RAG orchestration: LangChain
- Agentic routing/outreach: LangGraph
- Vector store: ChromaDB first, FAISS as local fallback
- Embeddings: sentence-transformers all-MiniLM-L6-v2
- LLM: Groq-hosted Llama 3.1 if API key is available; Ollama or another approved API as fallback
- Lead scoring: scikit-learn Logistic Regression first, XGBoost as improvement option
- Competitor retrieval: Tavily API first, SerpAPI as fallback
- Evaluation: RAGAS metrics for faithfulness, context precision, and answer relevancy
- Deployment: Hugging Face Spaces or Render free tier

## System Modules

1. RAG Q&A module
   - Load sample company documents.
   - Split documents into chunks.
   - Embed chunks and store them in ChromaDB.
   - Retrieve relevant chunks for each user question.
   - Generate grounded answers with source citations.

2. Lead qualification module
   - Prepare a Kaggle lead-scoring dataset.
   - Train Logistic Regression for conversion prediction.
   - Combine ML probability with simple business rules.
   - Explain the score in natural language using the LLM.

3. Agentic outreach module
   - Retrieve company and prospect context.
   - Generate a cold email draft.
   - Generate a shorter LinkedIn message.
   - Keep messages personalized and business-development focused.

4. Competitor intelligence module
   - Accept a competitor/company query.
   - Use Tavily or SerpAPI for public web retrieval.
   - Summarize findings with retrieved source links.

5. RAG evaluation module
   - Create a small test set of business-development questions.
   - Run RAGAS metrics: faithfulness, context precision, answer relevancy.
   - Record scores and improvement notes.

## Week 1 Work Plan

Dates: 06 July - 12 July 2026

- Requirement study: finalize objectives, scope, and MVP definition.
- Tool setup: Python environment, API key placeholders, LangChain dependencies.
- Company documents: create sample product sheet, pricing, FAQ, and past proposal documents.
- Dataset: select and prepare a Kaggle lead-scoring dataset.
- Literature review: summarize RAG, RAG evaluation, and lead-scoring references.

## Week 1 Deliverable

Deadline: Sunday, 12 July 2026

- Project proposal drafted.
- Sample company documents organized for RAG.
- Kaggle lead-scoring dataset selected and prepared.
- Initial literature review notes completed.
- GitHub-ready repository structure started.

## Dataset Plan

Primary candidate:

- Kaggle: Lead Scoring Dataset
- URL: https://www.kaggle.com/datasets/amritachatterjee09/lead-scoring-dataset

Fallback candidate:

- Kaggle: Leads Dataset
- URL: https://www.kaggle.com/datasets/ashydv/leads-dataset

Acceptance criteria:

- Contains lead records relevant to marketing/sales conversion.
- Has a binary target column such as `Converted`, `conversion`, or similar.
- Includes enough structured features for a baseline classifier.
- Can be cleaned into a train/test split for Logistic Regression.
- Allows explanation through features such as source, activity, engagement, company profile, or interest level.

## Expected Output

The final system will be a live Streamlit chatbot that can:

- Answer company-document questions with citations.
- Score leads and explain rankings.
- Draft personalized outreach messages.
- Retrieve and summarize public competitor information.
- Report RAGAS evaluation metrics.

## Risk and Mitigation

- API key availability: keep local/Ollama and open-source embedding options available.
- Dataset quality: define acceptance criteria and keep one fallback Kaggle dataset.
- Scope growth: build simple MVP first, then polish modules.
- RAG hallucination: require retrieved context and source citations, then evaluate with RAGAS.
