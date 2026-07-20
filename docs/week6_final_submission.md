# Week 6 — Final Report, PPT Outline & Demo Script

- **Task window:** 10 Aug – 16 Aug 2026
- **Final submission:** Live demo + GitHub + Report
- **Due:** Sun, 16 Aug

---

## English

### 1. Final Report

#### 1.1 Title & Abstract
**BizPilot AI: An Agentic RAG-Powered Chatbot for Digital Business Development.**
BizPilot AI answers questions from company documentation with citations, qualifies
inbound leads with an ML model, drafts personalized outreach, summarizes public
competitor information, and self-evaluates its RAG quality. It is built with
Streamlit, ChromaDB, sentence-transformers, and scikit-learn, and degrades
gracefully when LLM or web-search APIs are unavailable.

#### 1.2 Problem & Objectives
Digital business teams spend time on repetitive research, lead triage, and outreach
drafting. BizPilot AI consolidates these into one assistant. Objectives (professor scope):
1. RAG Q&A over company docs with citations.
2. ML lead scoring on a public Kaggle dataset.
3. Agentic outreach generation.
4. Competitor intelligence via web retrieval.
5. RAGAS-style evaluation (faithfulness, context precision, answer relevancy).
6. Streamlit UI deployed to Hugging Face Spaces / Render, with Git/GitHub + README + diagram.

#### 1.3 System Architecture
- **UI:** Streamlit, 7 tabs, EN/TR toggle.
- **Router:** keyword intent classification routes chat to RAG / lead / outreach / competitor.
- **RAG:** ChromaDB vector store + all-MiniLM-L6-v2 embeddings; retrieval then LLM
  generation constrained to retrieved context, with extractive fallback and citations.
- **Lead scoring:** Logistic Regression pipeline (ROC-AUC ≈ 0.87), rule reasons + optional LLM explanation.
- **Outreach agent:** qualify → research → draft → critique (LangGraph-optional, sequential fallback).
- **Competitor intel:** Tavily → SerpAPI → local corpus fallback.
- **Evaluation:** LLM-judge faithfulness/relevancy, embedding-based context precision, guardrail refusal checks.
- See the architecture diagram in `README.md`.

#### 1.4 Data
- **RAG corpus:** synthetic BizPilot company docs (`data/company_docs/bizpilot_synthetic_corpus.jsonl`).
- **Lead scoring:** public Kaggle Lead Scoring dataset (cleaned pipeline).

#### 1.5 Results
| Metric | Value |
| --- | --- |
| Lead scoring ROC-AUC | ~0.87 |
| RAG faithfulness | 0.80 |
| RAG answer relevancy | 0.74 |
| RAG context precision | 0.56 |
| Guardrail refusals | 2 / 2 |

#### 1.6 Deployment
Hugging Face Spaces (Streamlit SDK) and Render (Docker). Secrets set on-platform;
ChromaDB rebuilt on first run; model committed. See `docs/week6_deployment_guide.md`.

#### 1.7 Limitations & Future Work
- Synthetic RAG corpus (not real proprietary docs).
- Context precision has room to improve (chunking / re-ranking).
- LLM features require an API key; offline mode is extractive/rule-based.
- Future: re-ranking, larger eval set, XGBoost comparison, CRM integration.

#### 1.8 Reproducibility
- Weekly docs in `docs/`, reports in `reports/`, pinned `requirements.txt`.
- Run instructions in `README.md` for every module.

### 2. Presentation (PPT) Outline

1. **Title** — BizPilot AI, name, course, date.
2. **Problem** — repetitive research / lead triage / outreach.
3. **Solution overview** — one agentic assistant, 7 capabilities.
4. **Architecture diagram** — from README.
5. **RAG Q&A** — retrieval + citations + fallback (screenshot).
6. **Lead scoring** — dataset, model, ROC-AUC, explanation.
7. **Outreach agent** — qualify→research→draft→critique.
8. **Competitor intelligence** — Tavily/local fallback.
9. **Evaluation** — metrics table + guardrails.
10. **Deployment** — HF Spaces / Render, graceful degradation.
11. **Results & limitations.**
12. **Live demo + Q&A.**

### 3. Demo Video Script (~4–5 min)

1. **Intro (20s):** "This is BizPilot AI, an agentic RAG chatbot for digital business development." Show the running app + tab bar.
2. **Chatbot / RAG (60s):** Ask *"How much does the Starter plan cost?"* → show cited answer ("USD 49 per month [1][2]") and the meta line (RAG Q&A · llm).
3. **Lead Qualification (45s):** Enter a natural-language lead prompt → show score, label, and reasons.
4. **Outreach Preview (45s):** Generate an outreach draft for the scored lead → show cold email + LinkedIn draft and the critique note.
5. **Competitor Intelligence (45s):** Query *"HubSpot CRM pricing"* → show summary + provider (Tavily/local).
6. **RAG Evaluation (30s):** Open `reports/week5_rag_evaluation.md` → show faithfulness / precision / relevancy + 2/2 guardrails.
7. **Deployment (30s):** Show the live Hugging Face Space URL loading.
8. **Close (15s):** GitHub repo + README architecture diagram; mention graceful degradation.

**Recording tips:** 1080p, hide API keys, pre-build the index so there's no first-run wait, keep each step tight.

### 4. Submission Checklist
- [ ] Live demo URL (HF Spaces / Render) working.
- [ ] GitHub repo public with README + architecture diagram.
- [ ] Final report (this doc + README).
- [ ] PPT built from the outline above.
- [ ] Demo video recorded and linked.
- [ ] No secrets committed; exposed keys rotated.

---

## Türkçe

### 1. Final Rapor

#### 1.1 Başlık & Özet
**BizPilot AI: Dijital İş Geliştirme için Agentic RAG Destekli Chatbot.**
BizPilot AI; şirket dokümanlarından kaynak göstererek cevap verir, gelen lead'leri
bir ML modeliyle puanlar, kişiselleştirilmiş outreach taslaklar, herkese açık rakip
bilgisini özetler ve RAG kalitesini kendi kendine değerlendirir. Streamlit, ChromaDB,
sentence-transformers ve scikit-learn ile geliştirildi; LLM/web-arama API'leri yoksa
graceful degradation ile çalışmaya devam eder.

#### 1.2 Problem & Hedefler
Dijital iş ekipleri tekrarlı araştırma, lead triyajı ve outreach taslaklamaya zaman
harcar. BizPilot AI bunları tek asistanda birleştirir. Hedefler (profesör kapsamı):
1. Kaynak gösteren RAG Q&A.
2. Public Kaggle dataset üzerinde ML lead scoring.
3. Agentic outreach üretimi.
4. Web retrieval ile rakip analizi.
5. RAGAS tarzı değerlendirme (faithfulness, context precision, answer relevancy).
6. Hugging Face Spaces / Render'a deploy edilen Streamlit UI + Git/GitHub + README + diyagram.

#### 1.3 Sistem Mimarisi
- **UI:** Streamlit, 7 sekme, EN/TR.
- **Router:** anahtar kelime intent sınıflandırması ile RAG / lead / outreach / rakip yönlendirmesi.
- **RAG:** ChromaDB + all-MiniLM-L6-v2; retrieval sonrası bağlamla sınırlı LLM üretimi, extractive fallback ve citation.
- **Lead scoring:** Logistic Regression (ROC-AUC ≈ 0.87), kural gerekçeleri + opsiyonel LLM açıklaması.
- **Outreach agent:** qualify → research → draft → critique.
- **Rakip analizi:** Tavily → SerpAPI → yerel korpus fallback.
- **Değerlendirme:** LLM-judge faithfulness/relevancy, embedding tabanlı context precision, guardrail red kontrolleri.
- Mimari diyagram `README.md` içinde.

#### 1.4 Veri
- **RAG korpusu:** synthetic BizPilot dokümanları (`data/company_docs/bizpilot_synthetic_corpus.jsonl`).
- **Lead scoring:** public Kaggle Lead Scoring dataset.

#### 1.5 Sonuçlar
| Metrik | Değer |
| --- | --- |
| Lead scoring ROC-AUC | ~0.87 |
| RAG faithfulness | 0.80 |
| RAG answer relevancy | 0.74 |
| RAG context precision | 0.56 |
| Guardrail red | 2 / 2 |

#### 1.6 Deployment
Hugging Face Spaces (Streamlit SDK) ve Render (Docker). Secret'lar platformda;
ChromaDB ilk açılışta yeniden kurulur; model commit edildi. Bkz. `docs/week6_deployment_guide.md`.

#### 1.7 Kısıtlar & Gelecek İş
- Synthetic RAG korpusu (gerçek özel doküman değil).
- Context precision iyileştirilebilir (chunking / re-ranking).
- LLM özellikleri API key ister; offline mod extractive/kural tabanlı.
- Gelecek: re-ranking, daha büyük eval seti, XGBoost karşılaştırması, CRM entegrasyonu.

#### 1.8 Tekrarlanabilirlik
- `docs/` haftalık dokümanlar, `reports/` raporlar, sabitlenmiş `requirements.txt`.
- Her modül için `README.md`'de çalıştırma talimatları.

### 2. Sunum (PPT) Taslağı
İngilizce bölümdeki 12 slayt sırasını takip et (Başlık → Problem → Çözüm → Mimari →
RAG → Lead scoring → Outreach → Rakip → Değerlendirme → Deployment → Sonuç → Canlı demo).

### 3. Demo Video Senaryosu (~4–5 dk)
İngilizce bölümdeki 8 adımı takip et: Giriş → Chatbot/RAG → Lead → Outreach →
Rakip → Değerlendirme → Deployment → Kapanış. Kayıt ipuçları: 1080p, API key'leri
gizle, indeksi önceden kur, adımları kısa tut.

### 4. Teslim Kontrol Listesi
- [ ] Canlı demo URL'i (HF Spaces / Render) çalışıyor.
- [ ] GitHub repo public, README + mimari diyagram var.
- [ ] Final rapor (bu doküman + README).
- [ ] PPT taslaktan hazırlandı.
- [ ] Demo video kaydedildi ve linklendi.
- [ ] Repoda secret yok; sızan anahtarlar yenilendi.
