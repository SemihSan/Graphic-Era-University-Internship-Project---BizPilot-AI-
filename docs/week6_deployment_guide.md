# Week 6 — Deployment Guide (Hugging Face Spaces & Render)

- **Task window:** 10 Aug – 16 Aug 2026
- **Goal:** Ship BizPilot AI as a live, shareable web app.
- **Deliverable:** Public URL + reproducible deploy steps.
- **Due:** Sun, 16 Aug

---

## English

### 1. What ships in the repo

| Artifact | Purpose |
| --- | --- |
| `app.py` | Streamlit entry point (7 tabs). |
| `src/` | Lead scoring, RAG, outreach agent, competitor intel, RAG eval. |
| `requirements.txt` | Pinned core deps (Streamlit, pandas, scikit-learn, chromadb, sentence-transformers). |
| `.streamlit/config.toml` | Theme + headless server config. |
| `Dockerfile` | Container image for Render / Docker Spaces. |
| `models/lead_scoring_logreg.joblib` | Trained model (force-kept in git). |
| `data/company_docs/bizpilot_synthetic_corpus.jsonl` | RAG corpus (index rebuilt on first run). |

**Not committed (rebuilt or secret):**
- `chroma_db/` — rebuilt automatically on first launch by `ensure_rag_index()`.
- `.env` — API keys are set as platform **secrets**, never committed.

### 2. Secrets

Set these as platform secrets (all optional — the app degrades gracefully):

| Key | Effect if missing |
| --- | --- |
| `OPENAI_API_KEY` | Falls back to extractive RAG / rule-based explanations. |
| `OPENAI_MODEL` | Defaults to configured model name. |
| `TAVILY_API_KEY` | Competitor Intelligence uses the local corpus instead of live web. |
| `SERPAPI_API_KEY` | Secondary web search fallback. |

> Security: rotate any key that was ever printed to a terminal or log. Never commit `.env`.

### 3. Deploy to Hugging Face Spaces (Streamlit SDK)

1. Create a new Space → SDK: **Streamlit** → hardware: CPU basic (upgrade if torch build is slow).
2. Add this YAML block at the very top of `README.md` (HF reads it as Space metadata):
   ```yaml
   ---
   title: BizPilot AI
   emoji: 🤖
   colorFrom: blue
   colorTo: indigo
   sdk: streamlit
   sdk_version: 1.58.0
   app_file: app.py
   pinned: false
   ---
   ```
3. Push the repo (or connect GitHub). HF installs `requirements.txt` and runs `app.py`.
4. In **Settings → Variables and secrets**, add `OPENAI_API_KEY`, `OPENAI_MODEL`, `TAVILY_API_KEY`.
5. First boot builds the ChromaDB index once (watch the logs); then the app is live.

### 4. Deploy to Render (Docker)

1. New → **Web Service** → connect the GitHub repo.
2. Runtime: **Docker** (uses the committed `Dockerfile`). Render injects `$PORT`.
3. Environment → add the secrets from the table above.
4. Deploy. Render builds the image, `streamlit run app.py` serves on `$PORT`.

**Alternative (no Docker):** Render "Python" service with
Build command `pip install -r requirements.txt` and
Start command `streamlit run app.py --server.port $PORT --server.address 0.0.0.0`.

### 5. Local smoke test before deploying

```powershell
.\.venv\Scripts\python.exe -m streamlit run app.py
```
Open http://localhost:8501, confirm all 7 tabs load, ask a RAG question, score a lead.

### 6. Post-deploy checklist

- [ ] App URL loads without the "model not found" error.
- [ ] RAG Q&A returns answers with citations (index built).
- [ ] Lead Qualification returns a score/label.
- [ ] Chatbot routes intents (RAG / outreach / competitor / lead).
- [ ] Secrets set; no keys in the repo.

---

## Türkçe

### 1. Repoda ne var

| Dosya | Amaç |
| --- | --- |
| `app.py` | Streamlit giriş noktası (7 sekme). |
| `src/` | Lead scoring, RAG, outreach agent, rakip analizi, RAG değerlendirme. |
| `requirements.txt` | Sabitlenmiş çekirdek bağımlılıklar. |
| `.streamlit/config.toml` | Tema + headless sunucu ayarı. |
| `Dockerfile` | Render / Docker Spaces için imaj. |
| `models/lead_scoring_logreg.joblib` | Eğitilmiş model (git'te tutuluyor). |
| `data/company_docs/bizpilot_synthetic_corpus.jsonl` | RAG korpusu (ilk açılışta indekslenir). |

**Commit edilmeyen (yeniden üretilen veya gizli):**
- `chroma_db/` — ilk açılışta `ensure_rag_index()` ile otomatik yeniden kurulur.
- `.env` — API anahtarları platform **secret**'ı olarak eklenir, asla commit edilmez.

### 2. Secret'lar

Hepsi opsiyonel — uygulama anahtarsız da çalışır (graceful degradation):

| Anahtar | Yoksa ne olur |
| --- | --- |
| `OPENAI_API_KEY` | Extractive RAG / kural tabanlı açıklamaya düşer. |
| `OPENAI_MODEL` | Varsayılan model adını kullanır. |
| `TAVILY_API_KEY` | Rakip Analizi canlı web yerine yerel korpusu kullanır. |
| `SERPAPI_API_KEY` | İkincil web arama yedeği. |

> Güvenlik: terminal/loga yazılmış her anahtarı yenile (rotate). `.env` asla commit edilmez.

### 3. Hugging Face Spaces (Streamlit SDK)

1. Yeni Space → SDK: **Streamlit** → donanım: CPU basic.
2. `README.md` en üstüne 3. adımdaki (İngilizce bölümdeki) YAML bloğunu ekle.
3. Repoyu push et; HF `requirements.txt`'i kurar ve `app.py`'yi çalıştırır.
4. **Settings → Variables and secrets**'ta anahtarları ekle.
5. İlk açılış ChromaDB indeksini bir kez kurar; sonra uygulama canlı olur.

### 4. Render (Docker)

1. New → **Web Service** → GitHub reposunu bağla.
2. Runtime: **Docker** (repodaki `Dockerfile`'ı kullanır). Render `$PORT` enjekte eder.
3. Environment → yukarıdaki secret'ları ekle.
4. Deploy et.

### 5. Deploy öncesi yerel test

```powershell
.\.venv\Scripts\python.exe -m streamlit run app.py
```
http://localhost:8501 aç, 7 sekmeyi kontrol et, bir RAG sorusu sor, lead skorla.

### 6. Deploy sonrası kontrol listesi

- [ ] Uygulama URL'i "model bulunamadı" hatası olmadan açılıyor.
- [ ] RAG Q&A citation'lı cevap veriyor.
- [ ] Lead Qualification skor/etiket döndürüyor.
- [ ] Chatbot intent yönlendirmesi çalışıyor.
- [ ] Secret'lar ayarlı; repoda anahtar yok.

---

## Notes

- `ensure_rag_index()` (app.py) rebuilds ChromaDB once per container via `@st.cache_resource`, so `chroma_db/` does not need to be committed.
- The trained model is force-kept in git (`!models/lead_scoring_logreg.joblib` in `.gitignore`) because raw training data is not committed and cannot be retrained on the deploy host.
- First boot is slow (torch + sentence-transformers download the embedding model). Subsequent loads are cached.
