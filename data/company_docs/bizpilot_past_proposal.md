# BizPilot AI Sample Past Proposal / BizPilot AI Örnek Geçmiş Proposal

Document type: past proposal
Source ID: proposal_001

## English

### Proposal Summary

Client: Northstar CRM Solutions

Use case: improve inbound lead response and sales team productivity

Proposed solution: deploy BizPilot AI as a Streamlit-based chatbot connected to company sales documents and a lead-scoring workflow.

### Client Problem

Northstar CRM Solutions receives inbound leads from webinars, website forms, and LinkedIn campaigns. The sales team spends significant time checking product details, identifying high-potential leads, and writing initial outreach. Response quality varies across team members.

### Proposed BizPilot AI Workflow

1. Upload company product sheets, FAQs, pricing, and past proposal documents.
2. Build a RAG index using sentence-transformers embeddings and ChromaDB.
3. Answer sales questions with cited sources.
4. Score inbound leads using a trained Logistic Regression model plus rules.
5. Generate personalized cold email and LinkedIn message drafts.
6. Retrieve competitor information with Tavily or SerpAPI when requested.

### Expected Benefits

- Faster answers to product and pricing questions
- More consistent lead prioritization
- Personalized outreach drafts for sales representatives
- Lightweight competitor summaries during deal preparation

### Proposed MVP Timeline

- Week 1: proposal, sample data, Kaggle dataset preparation
- Week 2: RAG ingestion and Q&A chain
- Week 3: lead-scoring baseline
- Week 4: outreach and competitor-intelligence modules
- Week 5: RAGAS evaluation and UI polish
- Week 6: deployment and final documentation

## Türkçe

### Proposal Özeti

Müşteri: Northstar CRM Solutions

Kullanım amacı: inbound lead response ve satış ekibi verimliliğini artırmak

Önerilen çözüm: BizPilot AI'ı şirket satış dokümanlarına ve lead-scoring workflow'una bağlı Streamlit tabanlı bir chatbot olarak kullanmak.

### Müşteri Problemi

Northstar CRM Solutions; webinarlar, website formları ve LinkedIn kampanyalarından inbound lead alır. Satış ekibi ürün detaylarını kontrol etmeye, yüksek potansiyelli lead'leri belirlemeye ve ilk outreach mesajlarını yazmaya önemli zaman harcar. Yanıt kalitesi ekip üyeleri arasında değişkenlik gösterir.

### Önerilen BizPilot AI Workflow'u

1. Şirket ürün dokümanlarını, FAQ dosyalarını, fiyatlandırma ve geçmiş proposal dokümanlarını yükle.
2. sentence-transformers embeddings ve ChromaDB kullanarak RAG index oluştur.
3. Satış sorularını kaynak göstererek cevapla.
4. Eğitilmiş Logistic Regression modeli ve kurallar ile inbound lead'leri puanla.
5. Kişiselleştirilmiş cold email ve LinkedIn mesaj taslakları üret.
6. İstendiğinde Tavily veya SerpAPI ile competitor bilgisi getir.

### Beklenen Faydalar

- Ürün ve fiyatlandırma sorularına daha hızlı cevap
- Daha tutarlı lead önceliklendirme
- Satış temsilcileri için kişiselleştirilmiş outreach taslakları
- Deal preparation sırasında hafif competitor summaries

### Önerilen MVP Zaman Çizelgesi

- Week 1: proposal, sample data, Kaggle dataset hazırlığı
- Week 2: RAG ingestion ve Q&A chain
- Week 3: lead-scoring baseline
- Week 4: outreach ve competitor-intelligence modülleri
- Week 5: RAGAS evaluation ve UI polish
- Week 6: deployment ve final documentation
