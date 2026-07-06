# Week 1 Professor Update

Dear Professor,

I have started the internship project "BizPilot AI: An Agentic RAG-Powered Chatbot for Digital Business Development" according to the provided objectives, tools, timeline, and deliverables.

During Week 1, I focused on requirement study, tool setup, sample company documents, Kaggle lead-scoring dataset preparation, initial literature review, and a simple Streamlit MVP interface.

Current progress:

- Reviewed the project requirements and kept the scope focused on digital business development.
- Created the initial GitHub-ready project structure.
- Prepared sample company documents for the future RAG pipeline:
  - product sheet
  - pricing sheet
  - FAQ
  - past proposal
- Selected and downloaded the Kaggle Lead Scoring Dataset locally.
- Cleaned the dataset and prepared it for machine learning.
- Trained a Logistic Regression baseline model for lead conversion prediction.
- Created a lead-scoring prediction wrapper that returns:
  - ML conversion probability
  - score out of 100
  - rule-based adjustment
  - final lead potential label
  - short explanation
- Built a professional Streamlit MVP interface with Turkish / English language switching.
- Started the literature review with RAG, RAGAS, and B2B predictive scoring references.
- Initialized Git and pushed the project to GitHub.

Dataset and model status:

- Raw dataset size: 9,240 rows and 37 columns
- Cleaned dataset size: 7,484 rows and 28 columns
- Target column: `Converted`
- Model: scikit-learn Logistic Regression
- Accuracy: 0.7902
- Precision: 0.7261
- Recall: 0.7555
- F1: 0.7405
- ROC-AUC: 0.8703

GitHub repository:

https://github.com/SemihSan/Graphic-Era-University-Internship-Project---BizPilot-AI-

Next, I will implement the real RAG Q&A pipeline using LangChain, sentence-transformers embeddings, and ChromaDB/FAISS so the chatbot can answer questions from the sample company documents with cited sources.

Regards,
Semih
