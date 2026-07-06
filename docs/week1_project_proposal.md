# Week 1 Project Proposal / 1. Hafta Proje Önerisi

## English

### Project Title

BizPilot AI: An Agentic RAG-Powered Chatbot for Digital Business Development

### Student Context

This project is being developed as an internship project at Graphic Era University. The work follows the objectives, tools, timeline, and deliverables provided by the professor.

### Problem Statement

Digital business development teams often work with scattered information: product sheets, pricing documents, FAQs, past proposals, lead records, and public competitor information. This makes it difficult to answer sales questions quickly, prioritize the right leads, write personalized outreach, and evaluate whether AI-generated answers are grounded in reliable sources.

BizPilot AI aims to solve this by building a shareable web application that combines retrieval-augmented generation, lead scoring, agentic outreach drafting, lightweight competitor intelligence, and RAG-specific evaluation.

### Project Objectives

1. Build a RAG pipeline that lets the chatbot answer questions grounded in company documents such as product sheets, pricing, past proposals, and FAQs, with cited sources.
2. Design a lead-qualification module that scores and ranks inbound leads using a hybrid rule-based + machine learning model, explained in natural language by the LLM.
3. Implement an agentic outreach generator that drafts personalized cold emails and LinkedIn messages using retrieved prospect and company context.
4. Add a lightweight competitor-intelligence retriever that pulls and summarizes publicly available competitor information on demand.
5. Evaluate the system using RAG-specific metrics: faithfulness, context precision, and answer relevancy.
6. Deploy the chatbot as a live, shareable web app with a clean UI and a documented GitHub repository.

### Proposed Technology Stack

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

### MVP Architecture

1. User opens the Streamlit web app.
2. A routing layer will direct the user request to one of the modules: RAG Q&A, lead qualification, outreach generation, or competitor intelligence.
3. For RAG Q&A, company documents will be loaded, chunked, embedded, stored in ChromaDB/FAISS, retrieved, and cited in the final answer.
4. For lead qualification, the trained ML model will estimate conversion probability and a rule-based layer will adjust the score.
5. For outreach, retrieved prospect/company context will be used to draft a cold email and LinkedIn message.
6. For competitor intelligence, Tavily or SerpAPI will retrieve public web information and the LLM will summarize it with source links.
7. For evaluation, RAGAS will measure faithfulness, context precision, and answer relevancy.

### Week 1 Work Completed

Dates: 06 July - 12 July 2026

Requirement study was completed by reviewing the professor-provided objectives, tools, timeline, and deliverables. The project direction remains focused on BizPilot AI and digital business development.

Tool setup was completed with a Python project structure, `requirements.txt`, `.env.example`, `.gitignore`, Streamlit configuration, Git, and GitHub. The local environment currently supports Streamlit, pandas, scikit-learn, NumPy, openpyxl, and joblib for Week 1 dataset preparation and demo UI.

Sample company documents were created under `data/company_docs/`: product sheet, pricing sheet, FAQ, and past proposal. These documents will be used in the next step for RAG ingestion and retrieval.

The selected Kaggle dataset is the Lead Scoring Dataset. The local raw file is `data/lead_scoring/raw/Lead Scoring.csv`, and the data dictionary is `data/lead_scoring/raw/Leads Data Dictionary.xlsx`. The target column is `Converted`.

The raw dataset contains 9,240 rows and 37 columns. After cleaning, the prepared dataset contains 7,484 rows and 28 columns. Cleaning decisions included replacing `Select` values with missing values, removing ID columns, removing likely leakage columns, and preserving useful lead activity/source features.

A Logistic Regression baseline model was trained using scikit-learn. Baseline results:

- Accuracy: 0.7902
- Precision: 0.7261
- Recall: 0.7555
- F1: 0.7405
- ROC-AUC: 0.8703

Generated files:

- `src/lead_scoring_baseline.py`
- `src/lead_scoring_predictor.py`
- `reports/lead_scoring_baseline.md`

A professional Streamlit interface was created in `app.py`. The UI includes Dashboard, Lead Qualification, Company Documents workspace, Outreach Preview, Roadmap, and Turkish / English language switching. The local app was verified at `http://127.0.0.1:8501`.

The repository was initialized, committed, and pushed to GitHub:

```text
https://github.com/SemihSan/Graphic-Era-University-Internship-Project---BizPilot-AI-
```

### Week 1 Deliverables

Completed:

- Project proposal
- Dataset selected, downloaded locally, cleaned, and modeled
- Sample company documents for the RAG pipeline
- Literature review
- Tool setup documentation
- Streamlit MVP UI
- GitHub repository with structured files

### Next Week Direction

The next technical step is to implement the real RAG Q&A module:

1. Load company documents.
2. Split documents into chunks.
3. Generate embeddings with sentence-transformers all-MiniLM-L6-v2.
4. Store embeddings in ChromaDB.
5. Retrieve relevant chunks for a user question.
6. Generate an answer with citations.

### Risks and Mitigation

- API key availability: keep Groq/Ollama/OpenAI/Gemini options flexible within the professor-approved stack.
- Dataset quality: use Logistic Regression as baseline and keep XGBoost as an improvement option.
- RAG hallucination: require retrieved context and source citations, then evaluate with RAGAS.
- Scope growth: keep the MVP simple first, then add polish and additional agentic behavior.

## Türkçe

### Proje Başlığı

BizPilot AI: An Agentic RAG-Powered Chatbot for Digital Business Development

### Öğrenci Bağlamı

Bu proje Graphic Era University kapsamında bir internship projesi olarak geliştirilmektedir. Çalışma, profesör tarafından verilen objectives, tools, timeline ve deliverables doğrultusunda ilerlemektedir.

### Problem Tanımı

Dijital iş geliştirme ekipleri genellikle dağınık bilgilerle çalışır: product sheets, pricing documents, FAQs, past proposals, lead records ve public competitor information. Bu durum satış sorularına hızlı cevap vermeyi, doğru lead'leri önceliklendirmeyi, kişiselleştirilmiş outreach yazmayı ve AI-generated cevapların güvenilir kaynaklara dayanıp dayanmadığını değerlendirmeyi zorlaştırır.

BizPilot AI; retrieval-augmented generation, lead scoring, agentic outreach drafting, lightweight competitor intelligence ve RAG-specific evaluation özelliklerini bir araya getiren paylaşılabilir bir web uygulaması geliştirerek bu problemi çözmeyi amaçlar.

### Proje Hedefleri

1. Chatbot'un product sheets, pricing, past proposals ve FAQs gibi şirket dokümanlarına dayalı, kaynak gösteren cevaplar üretebildiği bir RAG pipeline kurmak.
2. Inbound lead'leri hybrid rule-based + machine learning modeliyle puanlayan ve sıralayan, LLM tarafından doğal dilde açıklanan bir lead-qualification modülü tasarlamak.
3. Retrieved prospect ve company context kullanarak kişiselleştirilmiş cold email ve LinkedIn mesajları taslaklayan agentic outreach generator geliştirmek.
4. İstendiğinde publicly available competitor information çeken ve özetleyen lightweight competitor-intelligence retriever eklemek.
5. Sistemi RAG-specific metrics ile değerlendirmek: faithfulness, context precision ve answer relevancy.
6. Chatbot'u temiz UI'a sahip, canlı ve paylaşılabilir bir web app olarak deploy etmek ve GitHub repository ile dokümante etmek.

### Önerilen Teknoloji Stack'i

- LLM: Groq veya Ollama üzerinden Llama 3.1 / Mistral 7B ya da GPT-4o-mini / Gemini 1.5 Flash API
- Orchestration: RAG chains için LangChain, agentic outreach ve routing için LangGraph veya CrewAI
- Vector database: önce ChromaDB, fallback olarak FAISS
- Embeddings: önce sentence-transformers all-MiniLM-L6-v2, opsiyonel API alternatifi olarak OpenAI text-embedding-3-small
- Lead scoring: scikit-learn Logistic Regression baseline, iyileştirme için XGBoost
- Web retrieval: önce Tavily API, fallback olarak SerpAPI
- Evaluation: faithfulness, context precision ve answer relevancy için RAGAS
- Backend: Python
- UI: Streamlit
- Deployment: Hugging Face Spaces veya Render free tier
- Version control: Git ve GitHub

### MVP Mimarisi

1. Kullanıcı Streamlit web app'i açar.
2. Routing layer kullanıcı isteğini RAG Q&A, lead qualification, outreach generation veya competitor intelligence modüllerinden birine yönlendirir.
3. RAG Q&A için company documents yüklenir, chunk'lara bölünür, embed edilir, ChromaDB/FAISS içinde saklanır, retrieve edilir ve final cevapta citation gösterilir.
4. Lead qualification için eğitilmiş ML model conversion probability tahmin eder ve rule-based layer skoru düzeltir.
5. Outreach için retrieved prospect/company context cold email ve LinkedIn message taslaklarında kullanılır.
6. Competitor intelligence için Tavily veya SerpAPI public web information getirir ve LLM bunu source links ile özetler.
7. Evaluation için RAGAS faithfulness, context precision ve answer relevancy ölçer.

### Week 1 Tamamlanan Çalışmalar

Tarih: 06 Temmuz - 12 Temmuz 2026

Requirement study, profesör tarafından verilen objectives, tools, timeline ve deliverables incelenerek tamamlandı. Proje yönü BizPilot AI ve digital business development odağında tutuldu.

Tool setup; Python proje yapısı, `requirements.txt`, `.env.example`, `.gitignore`, Streamlit configuration, Git ve GitHub ile tamamlandı. Lokal ortam Week 1 dataset hazırlığı ve demo UI için Streamlit, pandas, scikit-learn, NumPy, openpyxl ve joblib desteklemektedir.

Sample company documents `data/company_docs/` altında oluşturuldu: product sheet, pricing sheet, FAQ ve past proposal. Bu dokümanlar sonraki adımda RAG ingestion ve retrieval için kullanılacaktır.

Seçilen Kaggle dataset, Lead Scoring Dataset'tir. Lokal raw dosya `data/lead_scoring/raw/Lead Scoring.csv`, data dictionary ise `data/lead_scoring/raw/Leads Data Dictionary.xlsx` konumundadır. Hedef kolon `Converted` olarak belirlenmiştir.

Raw dataset 9,240 satır ve 37 sütun içerir. Temizlik sonrası prepared dataset 7,484 satır ve 28 sütun içermektedir. Temizlik kararları arasında `Select` değerlerini missing value olarak işaretleme, ID kolonlarını çıkarma, leakage riski taşıyan kolonları çıkarma ve useful lead activity/source features koruma yer alır.

scikit-learn kullanılarak Logistic Regression baseline modeli eğitildi. Baseline sonuçları:

- Accuracy: 0.7902
- Precision: 0.7261
- Recall: 0.7555
- F1: 0.7405
- ROC-AUC: 0.8703

Oluşturulan dosyalar:

- `src/lead_scoring_baseline.py`
- `src/lead_scoring_predictor.py`
- `reports/lead_scoring_baseline.md`

`app.py` içinde profesyonel bir Streamlit interface oluşturuldu. UI; Dashboard, Lead Qualification, Company Documents workspace, Outreach Preview, Roadmap ve Turkish / English language switching içerir. Lokal app `http://127.0.0.1:8501` adresinde doğrulandı.

Repository initialize edildi, commit alındı ve GitHub'a push edildi:

```text
https://github.com/SemihSan/Graphic-Era-University-Internship-Project---BizPilot-AI-
```

### Week 1 Teslimleri

Tamamlandı:

- Project proposal
- Dataset seçimi, lokal indirme, temizleme ve modelleme
- RAG pipeline için sample company documents
- Literature review
- Tool setup documentation
- Streamlit MVP UI
- Structured files içeren GitHub repository

### Sonraki Hafta Yönü

Sonraki teknik adım gerçek RAG Q&A modülünü kurmaktır:

1. Company documents yükle.
2. Dokümanları chunk'lara böl.
3. sentence-transformers all-MiniLM-L6-v2 ile embeddings üret.
4. Embeddings'i ChromaDB içinde sakla.
5. Kullanıcı sorusu için relevant chunks retrieve et.
6. Citation içeren cevap üret.

### Riskler ve Önlemler

- API key availability: profesör tarafından onaylanan stack içinde Groq/Ollama/OpenAI/Gemini seçeneklerini esnek tutmak.
- Dataset quality: Logistic Regression'ı baseline olarak kullanmak ve XGBoost'u improvement option olarak tutmak.
- RAG hallucination: retrieved context ve source citations zorunlu tutmak, ardından RAGAS ile değerlendirmek.
- Scope growth: önce simple MVP kurmak, sonra polish ve additional agentic behavior eklemek.
