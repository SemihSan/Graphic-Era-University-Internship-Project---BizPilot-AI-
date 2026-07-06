# Week 1 Tool Setup

Project: BizPilot AI

Date: 06 July 2026

## Local Environment

- Operating system: Windows
- Python version: 3.12.10
- UI framework: Streamlit
- Version control: Git and GitHub

## Virtual Environment

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

For the Week 1 working demo, the following packages were installed and used:

- pandas
- numpy
- scikit-learn
- openpyxl
- joblib
- streamlit

The full `requirements.txt` also includes the professor-approved stack for later modules:

- LangChain
- LangGraph
- ChromaDB
- FAISS
- sentence-transformers
- XGBoost
- RAGAS
- Tavily
- Groq / OpenAI / Gemini client libraries

## API Key Setup

API keys should not be committed to GitHub. The project includes `.env.example` as a template.

Create a local `.env` file:

```powershell
Copy-Item .env.example .env
```

Then fill only the keys needed for the chosen provider:

```text
GROQ_API_KEY=
OPENAI_API_KEY=
GOOGLE_API_KEY=
TAVILY_API_KEY=
SERPAPI_API_KEY=
OLLAMA_BASE_URL=http://localhost:11434
```

The `.env` file is ignored by Git.

## Dataset Setup

The Kaggle lead-scoring dataset was placed locally in:

```text
data/lead_scoring/raw/Lead Scoring.csv
data/lead_scoring/raw/Leads Data Dictionary.xlsx
```

Raw and processed dataset folders are ignored by Git to avoid uploading downloaded Kaggle data directly.

## Lead Scoring Baseline

Run the baseline training script:

```powershell
.venv\Scripts\python src\lead_scoring_baseline.py
```

This generates:

```text
data/lead_scoring/processed/lead_scoring_cleaned.csv
models/lead_scoring_logreg.joblib
reports/lead_scoring_baseline.md
```

The model file and processed dataset are local artifacts and are ignored by Git.

## Lead Scoring Prediction Test

Run the prediction wrapper:

```powershell
.venv\Scripts\python src\lead_scoring_predictor.py
```

Expected output:

- ML conversion probability
- ML score out of 100
- Rule-based adjustment
- Final lead score
- Potential label
- Short explanation

## Streamlit App

Run the local app:

```powershell
.venv\Scripts\streamlit run app.py
```

Local URL:

```text
http://127.0.0.1:8501
```

Current screens:

- Dashboard
- Lead Qualification
- Company Docs
- Outreach Preview
- Roadmap

The UI supports Turkish and English.

## GitHub

Repository:

```text
https://github.com/SemihSan/Graphic-Era-University-Internship-Project---BizPilot-AI-
```

Initial commit:

```text
Initial BizPilot AI MVP setup
```
