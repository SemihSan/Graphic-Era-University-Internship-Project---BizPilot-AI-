# Source Code / Kaynak Kod

## English

This folder contains the source code for the BizPilot AI MVP modules.

Current files:

- `lead_scoring_baseline.py`: cleans the Kaggle lead-scoring dataset, trains the Logistic Regression baseline model, and generates the report.
- `lead_scoring_predictor.py`: loads the trained model and produces a 0-100 lead score for a new lead.
- `lead_scoring_llm_explainer.py`: optionally generates natural language lead-score explanations and provides the shared configured LLM caller used by RAG.
- `lead_scoring_batch.py`: scores the CRM-style sample lead dataset and writes scored output.
- `rag_pipeline.py`: loads the active synthetic company-documentation JSONL dataset, chunks records, embeds them, indexes them in ChromaDB, and answers CLI questions with LLM-generated cited answers or extractive fallback.
- `__init__.py`: marks `src` as a Python package so modules can be imported from the Streamlit app.

Planned modules:

- Agentic routing and outreach
- Competitor intelligence retrieval
- RAGAS evaluation

## Türkçe

Bu klasör BizPilot AI MVP modüllerinin kaynak kodlarını içerir.

Mevcut dosyalar:

- `lead_scoring_baseline.py`: Kaggle lead-scoring dataset'ini temizler, Logistic Regression baseline modelini eğitir ve rapor oluşturur.
- `lead_scoring_predictor.py`: eğitilmiş modeli yükler ve yeni bir lead için 0-100 arası skor üretir.
- `lead_scoring_llm_explainer.py`: opsiyonel olarak LLM provider üzerinden doğal dil lead-score açıklaması üretir ve RAG tarafından kullanılan ortak LLM çağrı fonksiyonunu sağlar.
- `lead_scoring_batch.py`: CRM-style sample lead datasetini skorlar ve scored output dosyası üretir.
- `rag_pipeline.py`: aktif synthetic company-documentation JSONL datasetini yükler, kayıtları chunk'lara böler, embed eder, ChromaDB içinde indexler ve CLI sorularını LLM tarafından üretilen citation'lı cevapla veya extractive fallback ile cevaplar.
- `__init__.py`: `src` klasörünü Python paketi olarak tanımlar; böylece modüller Streamlit uygulamasından import edilebilir.

Planlanan modüller:

- Agentic routing ve outreach
- Competitor intelligence retrieval
- RAGAS evaluation
