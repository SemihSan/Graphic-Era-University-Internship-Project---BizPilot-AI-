# Week 1 Status Checklist / 1. Hafta Durum Kontrol Listesi

## English

Date: 06 July 2026

Week 1 deadline: Sunday, 12 July 2026

### Completed

- Requirement study source file exists: `anagorev.md`
- Project README created
- Project proposal finalized: `docs/week1_project_proposal.md`
- Literature review finalized: `docs/week1_literature_review.md`
- Tool setup documentation added: `docs/week1_tool_setup.md`
- Professor update prepared: `docs/week1_professor_update.md`
- Streamlit UI created: `app.py`
- Turkish / English UI language switch added
- Sample company documents created under `data/company_docs/`
- Kaggle lead-scoring dataset downloaded locally into `data/lead_scoring/raw/`
- Dataset cleaned locally into `data/lead_scoring/processed/lead_scoring_cleaned.csv`
- Logistic Regression baseline trained
- Lead scoring baseline report generated: `reports/lead_scoring_baseline.md`
- Lead scoring predictor created: `src/lead_scoring_predictor.py`
- Local Streamlit app verified at `http://127.0.0.1:8501`
- Git repository initialized
- GitHub remote connected
- Initial project commit pushed to GitHub

### Week 1 Deliverable Status

The Week 1 deliverable is ready:

- Project proposal: ready
- Dataset: selected, downloaded locally, cleaned, and modeled
- Sample company documents: ready
- Literature review: ready
- GitHub repository: ready
- Streamlit MVP demo: ready

### GitHub Repository

```text
https://github.com/SemihSan/Graphic-Era-University-Internship-Project---BizPilot-AI-
```

### Next Technical Task For Week 2

Implement the true RAG Q&A pipeline:

1. Load sample company documents.
2. Split documents into chunks.
3. Generate embeddings with sentence-transformers all-MiniLM-L6-v2.
4. Store chunks in ChromaDB or FAISS.
5. Retrieve relevant chunks for a user question.
6. Generate a cited answer.
7. Connect the RAG Q&A module to the Streamlit UI.

## Türkçe

Tarih: 06 Temmuz 2026

1. hafta son teslim tarihi: Pazar, 12 Temmuz 2026

### Tamamlananlar

- Requirement study kaynak dosyası mevcut: `anagorev.md`
- Project README oluşturuldu
- Project proposal final hale getirildi: `docs/week1_project_proposal.md`
- Literature review final hale getirildi: `docs/week1_literature_review.md`
- Tool setup dokümantasyonu eklendi: `docs/week1_tool_setup.md`
- Professor update hazırlandı: `docs/week1_professor_update.md`
- Streamlit UI oluşturuldu: `app.py`
- Türkçe / English UI language switch eklendi
- Sample company documents `data/company_docs/` altında oluşturuldu
- Kaggle lead-scoring dataset lokal olarak `data/lead_scoring/raw/` içine indirildi
- Dataset lokal olarak `data/lead_scoring/processed/lead_scoring_cleaned.csv` dosyasına temizlendi
- Logistic Regression baseline eğitildi
- Lead scoring baseline raporu oluşturuldu: `reports/lead_scoring_baseline.md`
- Lead scoring predictor oluşturuldu: `src/lead_scoring_predictor.py`
- Local Streamlit app `http://127.0.0.1:8501` adresinde doğrulandı
- Git repository başlatıldı
- GitHub remote bağlandı
- İlk project commit GitHub'a push edildi

### Week 1 Teslim Durumu

Week 1 teslimi hazır:

- Project proposal: hazır
- Dataset: seçildi, lokal olarak indirildi, temizlendi ve modellendi
- Sample company documents: hazır
- Literature review: hazır
- GitHub repository: hazır
- Streamlit MVP demo: hazır

### GitHub Repository

```text
https://github.com/SemihSan/Graphic-Era-University-Internship-Project---BizPilot-AI-
```

### Week 2 İçin Sonraki Teknik Görev

Gerçek RAG Q&A pipeline'ını kur:

1. Sample company documents yükle.
2. Dokümanları chunk'lara böl.
3. sentence-transformers all-MiniLM-L6-v2 ile embeddings üret.
4. Chunk'ları ChromaDB veya FAISS içine kaydet.
5. Kullanıcı sorusu için relevant chunks getir.
6. Kaynaklı cevap üret.
7. RAG Q&A modülünü Streamlit UI'a bağla.
