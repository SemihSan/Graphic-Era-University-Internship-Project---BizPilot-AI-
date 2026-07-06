# BizPilot AI FAQ / BizPilot AI Sık Sorulan Sorular

Document type: FAQ
Source ID: faq_001

## English

### What is BizPilot AI?

BizPilot AI is an agentic RAG-powered chatbot for digital business development. It helps answer company-document questions, qualify leads, draft outreach, and summarize competitor information.

### Which documents can BizPilot AI use?

The RAG pipeline can use product sheets, pricing documents, past proposals, FAQs, and other business-development documents that are safe to upload.

### Does the chatbot cite sources?

Yes. The RAG Q&A module should cite the source documents used to answer each question.

### How does lead qualification work?

The lead-qualification module combines a machine learning model trained on a public Kaggle lead-scoring dataset with simple business rules. The LLM then explains the score in natural language.

### What outreach can it generate?

The outreach module can draft personalized cold emails and LinkedIn messages using retrieved prospect and company context.

### How is competitor intelligence handled?

The competitor-intelligence module uses a public web retrieval API such as Tavily or SerpAPI, then summarizes the retrieved information with source links.

### How will the system be evaluated?

The RAG pipeline will be evaluated using RAGAS metrics: faithfulness, context precision, and answer relevancy.

## Türkçe

### BizPilot AI nedir?

BizPilot AI, dijital iş geliştirme için agentic RAG destekli bir chatbottur. Şirket dokümanı sorularını cevaplamaya, lead'leri puanlamaya, outreach taslakları üretmeye ve rakip bilgilerini özetlemeye yardımcı olur.

### BizPilot AI hangi dokümanları kullanabilir?

RAG pipeline; ürün dokümanları, fiyatlandırma dokümanları, geçmiş proposal dosyaları, FAQ ve güvenli şekilde yüklenebilecek diğer business-development dokümanlarını kullanabilir.

### Chatbot kaynak gösterir mi?

Evet. RAG Q&A modülü, her cevabı üretirken kullanılan kaynak dokümanları göstermelidir.

### Lead qualification nasıl çalışır?

Lead-qualification modülü, public Kaggle lead-scoring dataset üzerinde eğitilmiş bir machine learning modelini basit business rules ile birleştirir. LLM daha sonra skoru doğal dilde açıklar.

### Hangi outreach mesajlarını üretebilir?

Outreach modülü, retrieved prospect ve company context kullanarak kişiselleştirilmiş cold email ve LinkedIn mesajları taslaklayabilir.

### Competitor intelligence nasıl ele alınır?

Competitor-intelligence modülü Tavily veya SerpAPI gibi public web retrieval API kullanır, ardından retrieved bilgileri source linkleriyle özetler.

### Sistem nasıl değerlendirilecek?

RAG pipeline, RAGAS metrikleriyle değerlendirilecektir: faithfulness, context precision ve answer relevancy.
