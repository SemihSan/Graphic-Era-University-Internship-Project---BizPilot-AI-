# Week 5 Integration & Evaluation / 5. Hafta Entegrasyon ve Değerlendirme

## English

Week 5 task:

- Dates: 03 August - 09 August 2026
- Goal: integrate all modules into one Streamlit chatbot UI, run RAGAS evaluation, and fix hallucination / edge cases
- Deliverable: fully integrated chatbot + evaluation report
- Due date: Sunday, 09 August 2026

### 1. Unified chatbot UI

A new **Chatbot** tab (now the first tab in `app.py`) turns the separate modules into
one conversational surface. It uses `st.chat_input` / `st.chat_message` and keeps
history in `st.session_state["chat_history"]`.

An intent router (`classify_chat_intent`) sends each message to the right module
using lightweight keyword rules, then `route_chat_message` dispatches it:

| Intent | Trigger examples | Module used |
| --- | --- | --- |
| `rag` (default) | pricing, plans, architecture, "what is BizPilot" | `rag_pipeline` retrieve + `generate_llm_rag_answer` |
| `competitor` | "competitor", "rakip", "HubSpot", "compare" | `competitor_intel.run_competitor_intelligence` |
| `outreach` | "cold email", "write an email for X", "LinkedIn" | `outreach_agent.generate_outreach` |
| `lead` | "score this lead", "skorla", "qualify" | guided handoff to the Lead Qualification tab |

Each assistant reply shows the routed module, the answer, and citations / sources.
Verified live in the browser: *"How much does the Starter plan cost?"* → routed to
`rag`, answered **"The Starter plan costs USD 49 per month. [1][2]"** with citations
and `RAG Q&A · llm:openai`.

The existing per-module tabs (Dashboard, Lead Qualification, RAG Q&A, Outreach
Preview, Competitor Intelligence, Roadmap) remain available for detailed work.

### 2. RAG evaluation (RAGAS-style)

New module: `src/rag_eval.py`. It evaluates the RAG pipeline over a small labelled
set and reports the three scope-required metrics:

- **faithfulness** – is the answer grounded in the retrieved context?
- **context precision** – are the retrieved chunks relevant to the question?
- **answer relevancy** – does the answer address the question?

If the `ragas` package is installed it can be used; otherwise a self-contained
evaluator runs so a report is always produced. It combines an **LLM judge**
(via `call_configured_llm`) when a provider is reachable and an
**embedding-similarity fallback** (via the same all-MiniLM-L6-v2 model) otherwise.

Latest run (8 questions, top_k=5, LLM generation on):

| Metric | Score |
| --- | --- |
| Faithfulness | 0.800 |
| Context Precision | 0.531 |
| Answer Relevancy | 0.743 |
| Guardrails passed | 2 / 2 |

The full report is written to `reports/week5_rag_evaluation.md`.

CLI:

```powershell
.\.venv\Scripts\python.exe -m src.rag_eval --top-k 5
# embedding-only metrics (no LLM):
.\.venv\Scripts\python.exe -m src.rag_eval --no-llm
```

### 3. Hallucination / edge-case guardrails

- **No-context refusal:** if retrieval returns nothing, the chatbot and RAG pipeline
  say the answer is not in the company documents instead of guessing.
- **Low-confidence caveat:** if the best retrieved chunk distance is high (> 1.2),
  the chatbot prepends a caution note.
- **Grounding system prompt:** the RAG generation prompt forbids inventing prices,
  features, sources, or company details and requires citation markers.
- **Guardrail evaluation:** `rag_eval` includes deliberately out-of-scope questions
  ("capital of France", "exact 2027 revenue"); the system refused both (2/2).

### Verification

- `python -m src.rag_eval` → metrics computed, report written, guardrails 2/2.
- Streamlit Chatbot tab live-tested → correct routing + cited RAG answer.
- `app.py` imports and parses cleanly with the new Chatbot tab.

### Notes

- `ragas` is listed in `requirements.txt` but not installed in the current venv; the
  evaluator uses an optional/guarded path plus a self-contained fallback, so it runs
  today and can upgrade to real RAGAS when installed.
- Metric scores depend on LLM availability; the embedding fallback keeps them stable
  offline.

## Türkçe

5. hafta görevi:

- Tarih: 03 Ağustos - 09 Ağustos 2026
- Hedef: tüm modülleri tek bir Streamlit chatbot arayüzünde birleştirmek, RAGAS
  değerlendirmesi çalıştırmak, halüsinasyon / edge-case'leri düzeltmek
- Teslimat: tam entegre chatbot + değerlendirme raporu
- Bitiş: Pazar, 09 Ağustos 2026

### 1. Birleşik chatbot arayüzü

`app.py` içinde artık ilk sekme olan yeni bir **Chatbot** sekmesi, ayrı modülleri tek
bir sohbet yüzeyine dönüştürür. `st.chat_input` / `st.chat_message` kullanır ve
geçmişi `st.session_state["chat_history"]` içinde tutar.

Bir intent router (`classify_chat_intent`) her mesajı anahtar-kelime kurallarıyla
doğru modüle yönlendirir, `route_chat_message` dağıtır:

| Intent | Tetikleyici | Kullanılan modül |
| --- | --- | --- |
| `rag` (varsayılan) | fiyat, plan, mimari, "BizPilot nedir" | RAG retrieve + LLM cevap |
| `competitor` | "rakip", "HubSpot", "compare" | competitor intelligence |
| `outreach` | "cold email", "X için email yaz", "LinkedIn" | outreach agent |
| `lead` | "skorla", "qualify", "lead skor" | Lead Qualification sekmesine yönlendirme |

Tarayıcıda canlı doğrulandı: *"How much does the Starter plan cost?"* → `rag`'e
yönlendi, kaynak göstererek **"USD 49 per month [1][2]"** yanıtı verdi.

Mevcut modül sekmeleri detaylı çalışma için korunur.

### 2. RAG değerlendirmesi (RAGAS tarzı)

Yeni modül: `src/rag_eval.py`. RAG hattını küçük etiketli bir set üzerinde değerlendirir
ve kapsamda istenen üç metriği raporlar: **faithfulness**, **context precision**,
**answer relevancy**. `ragas` kuruluysa kullanılabilir; değilse kendi kendine yeten
bir değerlendirici çalışır (LLM yargıç + embedding-benzerlik fallback), böylece rapor
her zaman üretilir.

Son çalıştırma (8 soru): Faithfulness 0.800, Context Precision 0.531,
Answer Relevancy 0.743, Guardrails 2/2. Tam rapor:
`reports/week5_rag_evaluation.md`.

CLI:

```powershell
.\.venv\Scripts\python.exe -m src.rag_eval --top-k 5
```

### 3. Halüsinasyon / edge-case korumaları

- **Bağlam yoksa reddetme:** retrieve boş dönerse chatbot ve RAG, uydurmak yerine
  "şirket dokümanlarında yok" der.
- **Düşük güven uyarısı:** en iyi parça mesafesi yüksekse (> 1.2) chatbot uyarı ekler.
- **Grounding system prompt:** RAG üretim prompt'u fiyat/özellik/kaynak uydurmayı
  yasaklar ve citation zorunlu kılar.
- **Guardrail değerlendirmesi:** `rag_eval` kapsam-dışı sorular içerir; sistem ikisini
  de reddetti (2/2).

### Doğrulama

- `python -m src.rag_eval` → metrikler hesaplandı, rapor yazıldı, guardrails 2/2.
- Streamlit Chatbot sekmesi canlı test edildi → doğru yönlendirme + kaynaklı cevap.
- `app.py` yeni sekmeyle temiz import/parse edildi.

### Notlar

- `ragas` requirements'ta var ama venv'de kurulu değil; değerlendirici opsiyonel yol +
  kendi fallback'i ile bugün çalışır, kurulunca gerçek RAGAS'a yükselir.
- Metrik skorları LLM erişilebilirliğine bağlıdır; embedding fallback offline'da
  stabil tutar.
