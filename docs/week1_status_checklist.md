# Week 1 Status Checklist

Date: 06 July 2026

Week 1 deadline: Sunday, 12 July 2026

## Completed

- Requirement study source file exists: `anagorev.md`
- Project README created
- Project proposal finalized: `docs/week1_project_proposal.md`
- Literature review finalized: `docs/week1_literature_review.md`
- Tool setup documentation added: `docs/week1_tool_setup.md`
- Professor update prepared: `docs/week1_professor_update.md`
- Streamlit UI created: `app.py`
- Turkish / English UI language switch added
- Sample company documents created under `data/company_docs/`
- Kaggle lead-scoring dataset downloaded locally into `data/lead_scoring/raw/`
- Dataset cleaned locally into `data/lead_scoring/processed/lead_scoring_cleaned.csv`
- Logistic Regression baseline trained
- Lead scoring baseline report generated: `reports/lead_scoring_baseline.md`
- Lead scoring predictor created: `src/lead_scoring_predictor.py`
- Local Streamlit app verified at `http://127.0.0.1:8501`
- Git repository initialized
- GitHub remote connected
- Initial project commit pushed to GitHub

## Week 1 Deliverable Status

The Week 1 deliverable is ready:

- Project proposal: ready
- Dataset: selected, downloaded locally, cleaned, and modeled
- Sample company documents: ready
- Literature review: ready
- GitHub repository: ready
- Streamlit MVP demo: ready

## GitHub Repository

```text
https://github.com/SemihSan/Graphic-Era-University-Internship-Project---BizPilot-AI-
```

## Next Technical Task For Week 2

Implement the true RAG Q&A pipeline:

1. Load sample company documents.
2. Split documents into chunks.
3. Generate embeddings with sentence-transformers all-MiniLM-L6-v2.
4. Store chunks in ChromaDB or FAISS.
5. Retrieve relevant chunks for a user question.
6. Generate a cited answer.
7. Connect the RAG Q&A module to the Streamlit UI.
