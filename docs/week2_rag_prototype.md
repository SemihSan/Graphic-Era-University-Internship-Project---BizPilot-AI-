# Week 2 RAG Prototype / 2. Hafta RAG Prototipi

## English

Week 2 task:

- Dates: 13 July - 19 July 2026
- Goal: build the core RAG pipeline
- Scope: document ingestion, chunking, embeddings, ChromaDB indexing, and basic Q&A with citations
- Deliverable: working RAG prototype through CLI or notebook
- Due date: Sunday, 19 July 2026

### Current Implementation

The first CLI-based RAG prototype is implemented in:

```text
src/rag_pipeline.py
```

It currently supports:

- loading Markdown company documents from `data/company_docs/`,
- extracting metadata such as `Document type` and `Source ID`,
- splitting documents into overlapping chunks,
- generating embeddings using `sentence-transformers/all-MiniLM-L6-v2`,
- indexing chunks in persistent ChromaDB under `chroma_db/`,
- retrieving relevant chunks for a user question,
- returning a basic grounded answer with citations.

### Build The Index

```powershell
.venv\Scripts\python src\rag_pipeline.py build
```

### Ask A Question

```powershell
.venv\Scripts\python src\rag_pipeline.py ask "What is the Growth plan price?"
```

### Show Index Stats

```powershell
.venv\Scripts\python src\rag_pipeline.py stats
```

Verified local result:

```text
Collection: bizpilot_company_docs
Chunk count: 16
```

### Example Questions

```powershell
.venv\Scripts\python src\rag_pipeline.py ask "What is the Growth plan price?" --top-k 3
```

Expected behavior:

- retrieves `data/company_docs/bizpilot_pricing.md`
- identifies the Growth plan price as USD 149
- returns citations with source file, source ID, and chunk number

```powershell
.venv\Scripts\python src\rag_pipeline.py ask "How does lead qualification work?" --top-k 3
```

Expected behavior:

- retrieves product sheet and FAQ chunks related to lead qualification
- returns the hybrid rule-based + machine learning explanation context
- returns citations with source file, source ID, and chunk number

### Notes

This is a working RAG retrieval prototype. The current answer layer is extractive and citation-focused. A full LLM generation layer will be added later using one of the professor-approved LLM options.

## Türkçe

Week 2 görevi:

- Tarihler: 13 Temmuz - 19 Temmuz 2026
- Hedef: core RAG pipeline kurmak
- Kapsam: document ingestion, chunking, embeddings, ChromaDB indexing ve citations içeren basic Q&A
- Teslim: CLI veya notebook üzerinden çalışan RAG prototype
- Son teslim tarihi: Pazar, 19 Temmuz 2026

### Mevcut Implementasyon

İlk CLI tabanlı RAG prototipi şu dosyada implement edildi:

```text
src/rag_pipeline.py
```

Şu anda şunları destekler:

- `data/company_docs/` içindeki Markdown şirket dokümanlarını yükleme,
- `Document type` ve `Source ID` gibi metadata alanlarını çıkarma,
- dokümanları overlapping chunks şeklinde bölme,
- `sentence-transformers/all-MiniLM-L6-v2` ile embeddings üretme,
- chunk'ları `chroma_db/` altında persistent ChromaDB içine indexleme,
- kullanıcı sorusu için relevant chunks retrieve etme,
- citations içeren basic grounded answer döndürme.

### Index Oluşturma

```powershell
.venv\Scripts\python src\rag_pipeline.py build
```

### Soru Sorma

```powershell
.venv\Scripts\python src\rag_pipeline.py ask "What is the Growth plan price?"
```

### Index İstatistiklerini Gösterme

```powershell
.venv\Scripts\python src\rag_pipeline.py stats
```

Doğrulanan lokal sonuç:

```text
Collection: bizpilot_company_docs
Chunk count: 16
```

### Örnek Sorular

```powershell
.venv\Scripts\python src\rag_pipeline.py ask "What is the Growth plan price?" --top-k 3
```

Beklenen davranış:

- `data/company_docs/bizpilot_pricing.md` dosyasını retrieve eder
- Growth plan fiyatını USD 149 olarak yakalar
- source file, source ID ve chunk number ile citation döndürür

```powershell
.venv\Scripts\python src\rag_pipeline.py ask "How does lead qualification work?" --top-k 3
```

Beklenen davranış:

- lead qualification ile ilgili product sheet ve FAQ chunk'larını retrieve eder
- hybrid rule-based + machine learning açıklama context'ini döndürür
- source file, source ID ve chunk number ile citation döndürür

### Notlar

Bu çalışan bir RAG retrieval prototipidir. Mevcut answer layer extractive ve citation odaklıdır. Full LLM generation layer daha sonra profesör tarafından onaylanan LLM seçeneklerinden biriyle eklenecektir.
