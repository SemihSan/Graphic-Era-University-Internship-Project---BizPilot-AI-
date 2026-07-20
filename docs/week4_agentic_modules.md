# Week 4 Agentic Modules / 4. Hafta Agentic Modüller

## English

Week 4 task:

- Dates: 27 July - 02 August 2026
- Goal: build an agentic outreach generator (LangGraph/CrewAI) plus a competitor-intelligence retriever using Tavily/SerpAPI
- Deliverable: agentic modules functional
- Due date: Sunday, 02 August 2026

### What was built

Two new modules were added and wired into the Streamlit app:

```text
src/outreach_agent.py      # agentic outreach generator
src/competitor_intel.py    # competitor-intelligence retriever
```

#### 1. Agentic outreach generator (`src/outreach_agent.py`)

A small agent graph turns a prospect + lead signal into a personalized cold email
and LinkedIn message. It runs four nodes:

1. **qualify** – computes the lead score with the Week 3 `score_lead` model, so the
   message can reference qualification signals.
2. **research** – retrieves BizPilot value props from the RAG corpus
   (`rag_pipeline.retrieve`) to ground the message in real product context.
3. **draft** – an LLM (`call_configured_llm`) generates the first cold email + LinkedIn draft.
4. **critique** – the "agentic" refine step: an LLM reviews and tightens the draft once.

If `langgraph` is installed a real `StateGraph` is compiled and executed;
otherwise the same nodes run through a lightweight pure-Python sequential runner,
so the module is always functional. Every step degrades gracefully:

- no LLM / no network → deterministic template draft
- no RAG index → drafting continues without retrieved context

Entry point: `generate_outreach(company, contact, pain_point, lead_data, use_rag, use_llm)`.

CLI:

```powershell
.\.venv\Scripts\python.exe -m src.outreach_agent --company "Northstar CRM Solutions" --contact "Aarav"
# offline template only:
.\.venv\Scripts\python.exe -m src.outreach_agent --no-llm --no-rag
```

#### 2. Competitor-intelligence retriever (`src/competitor_intel.py`)

Retrieves public web information and summarizes it with an LLM. Retrieval provider
fallback chain:

1. **Tavily** (`TAVILY_API_KEY`) – POST `https://api.tavily.com/search`
2. **SerpAPI** (`SERPAPI_API_KEY`) – GET `https://serpapi.com/search.json`
3. **Local corpus fallback** – keyword search over the synthetic company corpus
   (used when no API keys are configured, so the module still works offline).

The retrieved snippets are summarized with `call_configured_llm`, with an
extractive summary fallback when no LLM is reachable.

Entry point: `run_competitor_intelligence(query, max_results, use_llm)`.

CLI:

```powershell
.\.venv\Scripts\python.exe -m src.competitor_intel "AI lead scoring SaaS competitors" --max-results 4
```

### Streamlit integration

`app.py` now exposes both modules:

- **Outreach Preview** tab → upgraded from a static template to the agentic
  generator (Generate button, spinner, pipeline trace, lead score, email +
  LinkedIn output, retrieved-context expander).
- **Competitor Intelligence** tab (new) → query input, retrieval provider,
  LLM summary, and source list.

Run the app:

```powershell
.\.venv\Scripts\python.exe -m streamlit run app.py
```

### Verification

- `python -m src.outreach_agent` → pipeline `qualify → research → draft → critique`,
  lead score from the ML model, draft + critique both served by the OpenAI LLM.
- `python -m src.competitor_intel` → `local_corpus_fallback` retrieval (no API keys),
  LLM summary served by OpenAI, ranked source list.
- `app.py` imports and parses cleanly with both new tabs.

### Notes

- `langgraph`, `tavily`, and `serpapi` are listed in `requirements.txt` but are not
  installed in the current venv; the modules use guarded/optional imports and stdlib
  `urllib`, so they run today and automatically upgrade if those packages are installed.
- API keys (`OPENAI_API_KEY`, `TAVILY_API_KEY`, `SERPAPI_API_KEY`) are read from `.env`,
  which stays gitignored. After editing `.env`, restart Streamlit for changes to apply.

## Türkçe

4. hafta görevi:

- Tarih: 27 Temmuz - 02 Ağustos 2026
- Hedef: agentic outreach üreticisi (LangGraph/CrewAI) ve Tavily/SerpAPI ile rakip-analizi getiricisi
- Teslimat: agentic modüllerin çalışır olması
- Bitiş: Pazar, 02 Ağustos 2026

### Yapılanlar

Streamlit uygulamasına bağlanan iki yeni modül eklendi:

```text
src/outreach_agent.py      # agentic outreach üreticisi
src/competitor_intel.py    # rakip-analizi getiricisi
```

#### 1. Agentic outreach üreticisi (`src/outreach_agent.py`)

Küçük bir agent grafiği, prospect + lead sinyalini kişiselleştirilmiş cold email
ve LinkedIn mesajına dönüştürür. Dört düğüm çalışır:

1. **qualify** – 3. hafta `score_lead` modeliyle lead skorunu hesaplar.
2. **research** – RAG korpusundan (`rag_pipeline.retrieve`) BizPilot değer önerilerini
   getirerek mesajı gerçek ürün bağlamına dayandırır.
3. **draft** – bir LLM (`call_configured_llm`) ilk cold email + LinkedIn taslağını üretir.
4. **critique** – "agentic" iyileştirme adımı: LLM taslağı bir kez gözden geçirip sıkılaştırır.

`langgraph` kuruluysa gerçek bir `StateGraph` derlenip çalıştırılır; değilse aynı
düğümler saf-Python sıralı bir runner ile çalışır, böylece modül her zaman
işlevseldir. Her adım zarifçe düşer: LLM/ağ yoksa deterministik template taslak;
RAG index yoksa bağlam olmadan taslak üretimi devam eder.

CLI:

```powershell
.\.venv\Scripts\python.exe -m src.outreach_agent --company "Northstar CRM Solutions" --contact "Aarav"
```

#### 2. Rakip-analizi getiricisi (`src/competitor_intel.py`)

Public web bilgisini getirip LLM ile özetler. Getirme sağlayıcı sırası: Tavily →
SerpAPI → yerel korpus (API anahtarı yoksa offline çalışır). Getirilen parçalar
`call_configured_llm` ile özetlenir; LLM yoksa extractive özete düşer.

CLI:

```powershell
.\.venv\Scripts\python.exe -m src.competitor_intel "AI lead scoring SaaS competitors" --max-results 4
```

### Streamlit entegrasyonu

`app.py` artık her iki modülü de gösterir:

- **Outreach Preview** sekmesi → statik template yerine agentic üretici (Üret butonu,
  spinner, pipeline izi, lead skoru, email + LinkedIn çıktısı, bağlam expander).
- **Rakip Analizi** sekmesi (yeni) → sorgu girişi, getirme sağlayıcısı, LLM özeti,
  kaynak listesi.

### Doğrulama

- `python -m src.outreach_agent` → `qualify → research → draft → critique` hattı,
  ML modelinden lead skoru, taslak + critique ikisi de OpenAI LLM ile üretildi.
- `python -m src.competitor_intel` → API anahtarı olmadan `local_corpus_fallback`
  getirme, OpenAI ile LLM özeti, sıralı kaynak listesi.
- `app.py` iki yeni sekmeyle temiz şekilde import/parse edildi.

### Notlar

- `langgraph`, `tavily`, `serpapi` `requirements.txt` içinde ama venv'de kurulu değil;
  modüller korumalı/opsiyonel importlar ve stdlib `urllib` kullanır, bu paketler
  kurulunca otomatik yükseltilir.
- API anahtarları `.env`'den okunur (gitignore'da kalır). `.env` düzenlendikten sonra
  değişikliklerin geçerli olması için Streamlit'i yeniden başlat.
