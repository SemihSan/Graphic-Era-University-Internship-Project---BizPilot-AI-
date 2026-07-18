# Week 2 RAG Prototype / 2. Hafta RAG Prototipi

## English

Week 2 task:

- Dates: 13 July - 19 July 2026
- Goal: build the core RAG pipeline
- Scope: document ingestion, chunking, embeddings, ChromaDB indexing, and basic Q&A with citations
- Deliverable: working RAG prototype through CLI or notebook
- Due date: Sunday, 19 July 2026

### Dataset Update

After professor feedback, the active RAG corpus was changed from short hand-written Markdown files and a small public reference corpus to a larger AI-synthesized JSONL dataset for a fictional but consistent BizPilot AI company. This gives the RAG pipeline enough related material to retrieve four or five chunks for realistic multi-context answers.

Active dataset:

```text
data/company_docs/bizpilot_synthetic_corpus.jsonl
```

The dataset contains synthetic product, pricing, FAQ, RAG architecture, lead scoring, outreach, competitor intelligence, onboarding, support, security, implementation, and case-study records. Each JSONL row includes:

- document ID
- company name
- document type
- title
- source URL
- retrieved date
- corpus type
- cleaned content

The earlier synthetic Markdown files were moved to:

```text
data/company_docs_synthetic_archive/
```

They are kept only as an archive of the first pipeline test and are not used by the active RAG pipeline.

### Current Implementation

The CLI-based RAG prototype is implemented in:

```text
src/rag_pipeline.py
```

It currently supports:

- loading the synthetic JSONL company documentation dataset,
- reading metadata such as company, document type, source URL, and retrieved date,
- splitting records into chunks,
- generating embeddings using `sentence-transformers/all-MiniLM-L6-v2`,
- indexing chunks in persistent ChromaDB under `chroma_db/`,
- retrieving relevant chunks for a user question,
- returning a basic grounded answer with citations to source URLs.

### Build The Index

```powershell
.venv\Scripts\python src\rag_pipeline.py build
```

### Ask A Question

```powershell
.venv\Scripts\python src\rag_pipeline.py ask "Which plan is best for a growing sales team and why?" --top-k 5
```

```powershell
.venv\Scripts\python src\rag_pipeline.py ask "How does prompt-only lead qualification work?" --top-k 5
```

### Show Index Stats

```powershell
.venv\Scripts\python src\rag_pipeline.py stats
```

Verified local result after the synthetic JSONL dataset update:

```text
Collection: bizpilot_company_docs
Chunk count: 46
```

### Notes

This is now a working RAG Q&A prototype with an LLM generation layer. The system retrieves relevant ChromaDB chunks first, sends only the retrieved context to the configured LLM provider, and returns a cited answer. The Streamlit RAG tab includes a custom answer prompt so the user can control tone, format, and business focus while keeping the answer grounded in retrieved sources. If the LLM provider is unavailable, the CLI can still use the extractive fallback with `--no-llm`.

## Türkçe

2. hafta görevi:

- Tarihler: 13 Temmuz - 19 Temmuz 2026
- Hedef: core RAG pipeline kurmak
- Kapsam: document ingestion, chunking, embeddings, ChromaDB indexing ve citation içeren basic Q&A
- Teslim: CLI veya notebook üzerinden çalışan RAG prototype
- Son teslim tarihi: Pazar, 19 Temmuz 2026

### Dataset Güncellemesi

Profesör geri bildiriminden sonra aktif RAG corpus, kısa elle yazılmış Markdown dosyalarından ve küçük public reference corpus'tan çıkarıldı. Bunun yerine fictional ama tutarlı BizPilot AI şirketi için daha büyük AI-synthesized JSONL dataset formatına taşındı. Böylece RAG pipeline gerçekçi multi-context cevaplar için dört veya beş ilgili chunk retrieve edebilir.

Aktif dataset:

```text
data/company_docs/bizpilot_synthetic_corpus.jsonl
```

Dataset; product, pricing, FAQ, RAG architecture, lead scoring, outreach, competitor intelligence, onboarding, support, security, implementation ve synthetic case-study kayıtları içerir. Her JSONL satırında şunlar bulunur:

- document ID
- company name
- document type
- title
- source URL
- retrieved date
- corpus type
- cleaned content

Önceki sentetik Markdown dosyaları şu klasöre taşındı:

```text
data/company_docs_synthetic_archive/
```

Bu dosyalar sadece ilk pipeline testinin arşivi olarak tutulur ve aktif RAG pipeline tarafından kullanılmaz.

### Mevcut Implementasyon

CLI tabanlı RAG prototipi şu dosyada implement edildi:

```text
src/rag_pipeline.py
```

Şu anda şunları destekler:

- synthetic JSONL company documentation dataset yükleme,
- company, document type, source URL ve retrieved date gibi metadata alanlarını okuma,
- dataset kayıtlarını chunk'lara bölme,
- `sentence-transformers/all-MiniLM-L6-v2` ile embeddings üretme,
- chunk'ları `chroma_db/` altında persistent ChromaDB içine indexleme,
- kullanıcı sorusu için relevant chunks retrieve etme,
- source URL citation içeren basic grounded answer döndürme.

### Index Oluşturma

```powershell
.venv\Scripts\python src\rag_pipeline.py build
```

### Soru Sorma

```powershell
.venv\Scripts\python src\rag_pipeline.py ask "Which plan is best for a growing sales team and why?" --top-k 5
```

```powershell
.venv\Scripts\python src\rag_pipeline.py ask "How does prompt-only lead qualification work?" --top-k 5
```

### Index İstatistiklerini Gösterme

```powershell
.venv\Scripts\python src\rag_pipeline.py stats
```

Synthetic JSONL dataset güncellemesinden sonra doğrulanan lokal sonuç:

```text
Collection: bizpilot_company_docs
Chunk count: 46
```

### Notlar

Bu artık LLM generation layer içeren çalışan bir RAG Q&A prototipidir. Sistem önce ChromaDB üzerinden relevant chunk'ları retrieve eder, sadece retrieved context'i yapılandırılmış LLM provider'a gönderir ve citation içeren cevap döndürür. Streamlit RAG tab'ında custom answer prompt alanı bulunur; kullanıcı tone, format ve business focus verebilir ama cevap yine retrieved source'lara grounded kalır. LLM provider erişilemezse CLI hâlâ `--no-llm` ile extractive fallback modunda çalışabilir.
