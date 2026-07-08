# Source Code / Kaynak Kod

## English

This folder contains the source code for the BizPilot AI MVP modules.

Current files:

- `lead_scoring_baseline.py`: cleans the Kaggle lead-scoring dataset, trains the Logistic Regression baseline model, and generates the report.
- `lead_scoring_predictor.py`: loads the trained model and produces a 0-100 lead score for a new lead.
- `rag_pipeline.py`: loads company documents, chunks them, embeds them, indexes them in ChromaDB, and answers CLI questions with citations.
- `__init__.py`: marks `src` as a Python package so modules can be imported from the Streamlit app.

Planned modules:

- RAG ingestion and retrieval
- Agentic routing and outreach
- Competitor intelligence retrieval
- Streamlit UI integration
- RAGAS evaluation

## Türkçe

Bu klasör BizPilot AI MVP modüllerinin kaynak kodlarını içerir.

Mevcut dosyalar:

- `lead_scoring_baseline.py`: Kaggle lead-scoring dataset'ini temizler, Logistic Regression baseline modelini eğitir ve rapor oluşturur.
- `lead_scoring_predictor.py`: eğitilmiş modeli yükler ve yeni bir lead için 0-100 arası skor üretir.
- `rag_pipeline.py`: şirket dokümanlarını yükler, chunk'lara böler, embed eder, ChromaDB içinde indexler ve CLI sorularını citations ile cevaplar.
- `__init__.py`: `src` klasörünü Python paketi olarak tanımlar; böylece modüller Streamlit uygulamasından import edilebilir.

Planlanan modüller:

- RAG ingestion ve retrieval
- Agentic routing ve outreach
- Competitor intelligence retrieval
- Streamlit UI entegrasyonu
- RAGAS evaluation
