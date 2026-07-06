# Week 1 Tool Setup / 1. Hafta Araç Kurulumu

## English

Project: BizPilot AI

Date: 06 July 2026

### Local Environment

- Operating system: Windows
- Python version: 3.12.10
- UI framework: Streamlit
- Version control: Git and GitHub

### Virtual Environment

Create the virtual environment:

```powershell
python -m venv .venv
```

Activate the virtual environment:

```powershell
.venv\Scripts\Activate.ps1
```

Install dependencies:

```powershell
.venv\Scripts\python -m pip install -r requirements.txt
```

Week 1 working packages:

- pandas
- numpy
- scikit-learn
- openpyxl
- joblib
- streamlit

The full `requirements.txt` also includes LangChain, LangGraph, ChromaDB, FAISS, sentence-transformers, XGBoost, RAGAS, Tavily, Groq, OpenAI, and Gemini client libraries for later modules.

### API Key Setup

API keys should not be committed to GitHub. The project includes `.env.example` as a template.

Create a local `.env` file:

```powershell
Copy-Item .env.example .env
```

Fill only the keys needed for the selected provider:

```text
GROQ_API_KEY=
OPENAI_API_KEY=
GOOGLE_API_KEY=
TAVILY_API_KEY=
SERPAPI_API_KEY=
OLLAMA_BASE_URL=http://localhost:11434
```

The `.env` file is ignored by Git.

### Dataset Setup

The Kaggle lead-scoring dataset was placed locally in:

```text
data/lead_scoring/raw/Lead Scoring.csv
data/lead_scoring/raw/Leads Data Dictionary.xlsx
```

Raw and processed dataset folders are ignored by Git.

### Run Lead Scoring Baseline

```powershell
.venv\Scripts\python src\lead_scoring_baseline.py
```

Generated local outputs:

```text
data/lead_scoring/processed/lead_scoring_cleaned.csv
models/lead_scoring_logreg.joblib
reports/lead_scoring_baseline.md
```

### Run Prediction Wrapper

```powershell
.venv\Scripts\python src\lead_scoring_predictor.py
```

### Run Streamlit App

```powershell
.venv\Scripts\streamlit run app.py
```

Local URL:

```text
http://127.0.0.1:8501
```

### GitHub

Repository:

```text
https://github.com/SemihSan/Graphic-Era-University-Internship-Project---BizPilot-AI-
```

## Türkçe

Proje: BizPilot AI

Tarih: 06 Temmuz 2026

### Lokal Ortam

- İşletim sistemi: Windows
- Python versiyonu: 3.12.10
- UI framework: Streamlit
- Versiyon kontrolü: Git ve GitHub

### Virtual Environment

Virtual environment oluştur:

```powershell
python -m venv .venv
```

Virtual environment aktifleştir:

```powershell
.venv\Scripts\Activate.ps1
```

Bağımlılıkları yükle:

```powershell
.venv\Scripts\python -m pip install -r requirements.txt
```

Week 1'de kullanılan paketler:

- pandas
- numpy
- scikit-learn
- openpyxl
- joblib
- streamlit

Tam `requirements.txt` dosyası ileride kullanılacak LangChain, LangGraph, ChromaDB, FAISS, sentence-transformers, XGBoost, RAGAS, Tavily, Groq, OpenAI ve Gemini client library paketlerini de içerir.

### API Key Kurulumu

API key'ler GitHub'a commit edilmemelidir. Projede `.env.example` dosyası template olarak bulunur.

Lokal `.env` dosyası oluştur:

```powershell
Copy-Item .env.example .env
```

Yalnızca seçilen provider için gereken key'leri doldur:

```text
GROQ_API_KEY=
OPENAI_API_KEY=
GOOGLE_API_KEY=
TAVILY_API_KEY=
SERPAPI_API_KEY=
OLLAMA_BASE_URL=http://localhost:11434
```

`.env` dosyası Git tarafından ignore edilir.

### Dataset Kurulumu

Kaggle lead-scoring dataset lokal olarak şu konuma yerleştirildi:

```text
data/lead_scoring/raw/Lead Scoring.csv
data/lead_scoring/raw/Leads Data Dictionary.xlsx
```

Raw ve processed dataset klasörleri Git tarafından ignore edilir.

### Lead Scoring Baseline Çalıştırma

```powershell
.venv\Scripts\python src\lead_scoring_baseline.py
```

Oluşan lokal çıktılar:

```text
data/lead_scoring/processed/lead_scoring_cleaned.csv
models/lead_scoring_logreg.joblib
reports/lead_scoring_baseline.md
```

### Prediction Wrapper Çalıştırma

```powershell
.venv\Scripts\python src\lead_scoring_predictor.py
```

### Streamlit App Çalıştırma

```powershell
.venv\Scripts\streamlit run app.py
```

Lokal adres:

```text
http://127.0.0.1:8501
```

### GitHub

Repository:

```text
https://github.com/SemihSan/Graphic-Era-University-Internship-Project---BizPilot-AI-
```
