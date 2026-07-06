# Week 1 Literature Review / 1. Hafta Literatür Taraması

## English

Project: BizPilot AI: An Agentic RAG-Powered Chatbot for Digital Business Development

Date: 06 July 2026

### Purpose

This literature review supports the Week 1 deliverable by connecting the project objectives to existing work on retrieval-augmented generation, RAG evaluation, and predictive lead scoring. The review is focused on the professor-provided project direction: digital business development, RAG-based document question answering, lead qualification, outreach support, competitor intelligence, and RAG-specific evaluation.

### 1. Retrieval-Augmented Generation

Lewis et al. (2020), "Retrieval-Augmented Generation for Knowledge-Intensive NLP Tasks", introduced RAG as a way to combine a sequence-to-sequence language model with an external dense retrieval index. The central idea is useful for BizPilot AI because the chatbot should not answer only from the LLM's internal knowledge. Instead, it should retrieve relevant company documents such as product sheets, pricing files, FAQs, and past proposals, then generate an answer grounded in those retrieved sources. This directly supports the first project objective: a RAG pipeline that answers business-development questions with citations.

Source: https://arxiv.org/abs/2005.11401

### 2. RAG Evaluation With RAGAS

Es et al. (2023), "RAGAS: Automated Evaluation of Retrieval Augmented Generation", proposed a framework for evaluating RAG systems without always needing human-written reference answers. This is important for BizPilot AI because the professor specifically requires faithfulness, context precision, and answer relevancy. Faithfulness checks whether the generated answer is supported by retrieved context. Context precision checks whether the retrieval component brings useful context instead of noisy chunks. Answer relevancy checks whether the response actually addresses the user's question. These metrics will help evaluate whether the RAG module is reliable enough for company-document Q&A.

Source: https://arxiv.org/abs/2309.15217

### 3. Predictive Modeling for B2B Sales

Rezazadeh (2020), "A Generalized Flow for B2B Sales Predictive Modeling: An Azure Machine Learning Approach", frames B2B sales outcome prediction as a machine learning workflow using historical sales opportunity data. This supports the lead-qualification part of BizPilot AI because the project needs to estimate the likelihood that an inbound lead will convert. The paper is relevant because it treats sales prediction as a probabilistic classification problem, which aligns with the Week 1 baseline model built using Logistic Regression on the Kaggle lead-scoring dataset.

Source: https://arxiv.org/abs/2002.01441

### 4. Dynamic Scoring in B2B Contexts

Sinha et al. (2022), "B2B Advertising: Joint Dynamic Scoring of Account and Users", focuses on scoring both accounts and users in B2B advertising, where buying decisions may happen over a long period and involve multiple individuals. BizPilot AI's initial lead-scoring module is simpler, but this work supports the broader project idea that business-development systems should prioritize leads and accounts based on behavioral signals. It also supports the future outreach module, because a ranked lead can be paired with a personalized message.

Source: https://arxiv.org/abs/2209.14250

### Connection To BizPilot AI

The reviewed works support the planned architecture of BizPilot AI. RAG literature motivates the document-grounded chatbot. RAGAS motivates objective evaluation of faithfulness, context precision, and answer relevancy. B2B predictive modeling literature supports using a structured lead-scoring dataset and a classification model to estimate conversion likelihood. Together, these sources justify the Week 1 MVP direction: a Python and Streamlit application with a lead-scoring baseline, sample company documents for later RAG ingestion, and documentation that prepares the project for LangChain, ChromaDB, LangGraph, Tavily/SerpAPI, and RAGAS integration.

### References

1. Lewis, P., Perez, E., Piktus, A., Petroni, F., Karpukhin, V., Goyal, N., Kuttler, H., Lewis, M., Yih, W., Rocktaschel, T., Riedel, S., & Kiela, D. (2020). Retrieval-Augmented Generation for Knowledge-Intensive NLP Tasks. arXiv. https://arxiv.org/abs/2005.11401
2. Es, S., James, J., Espinosa-Anke, L., & Schockaert, S. (2023). RAGAS: Automated Evaluation of Retrieval Augmented Generation. arXiv. https://arxiv.org/abs/2309.15217
3. Rezazadeh, A. (2020). A Generalized Flow for B2B Sales Predictive Modeling: An Azure Machine Learning Approach. arXiv. https://arxiv.org/abs/2002.01441
4. Sinha, A. R., Choudhary, G., Agarwal, M., Bindal, S., Pande, A., & Girabawe, C. (2022). B2B Advertising: Joint Dynamic Scoring of Account and Users. arXiv. https://arxiv.org/abs/2209.14250

## Türkçe

Proje: BizPilot AI: An Agentic RAG-Powered Chatbot for Digital Business Development

Tarih: 06 Temmuz 2026

### Amaç

Bu literatür taraması, Week 1 teslimini desteklemek için proje hedeflerini retrieval-augmented generation, RAG evaluation ve predictive lead scoring alanındaki çalışmalarla ilişkilendirir. İnceleme, profesör tarafından verilen proje yönüne bağlı kalır: digital business development, RAG tabanlı doküman soru-cevap, lead qualification, outreach desteği, competitor intelligence ve RAG-specific evaluation.

### 1. Retrieval-Augmented Generation

Lewis et al. (2020), "Retrieval-Augmented Generation for Knowledge-Intensive NLP Tasks" çalışmasında RAG yaklaşımını, sequence-to-sequence language model ile external dense retrieval index birleşimi olarak tanıtmıştır. Bu fikir BizPilot AI için önemlidir çünkü chatbot yalnızca LLM'in iç bilgisinden cevap vermemelidir. Bunun yerine product sheets, pricing files, FAQs ve past proposals gibi ilgili şirket dokümanlarını retrieve etmeli, ardından bu kaynaklara dayalı cevap üretmelidir. Bu doğrudan ilk proje hedefini destekler: business-development sorularını citation ile cevaplayan bir RAG pipeline.

Kaynak: https://arxiv.org/abs/2005.11401

### 2. RAGAS ile RAG Evaluation

Es et al. (2023), "RAGAS: Automated Evaluation of Retrieval Augmented Generation" çalışmasında RAG sistemlerini her zaman human-written reference answer gerektirmeden değerlendirmeye yarayan bir framework önermiştir. Bu BizPilot AI için önemlidir çünkü profesör özellikle faithfulness, context precision ve answer relevancy metriklerini istemektedir. Faithfulness, generated answer'ın retrieved context tarafından desteklenip desteklenmediğini kontrol eder. Context precision, retrieval component'in noisy chunks yerine faydalı context getirip getirmediğini ölçer. Answer relevancy ise cevabın kullanıcı sorusuyla gerçekten ilgili olup olmadığını değerlendirir. Bu metrikler RAG modülünün şirket dokümanı Q&A için güvenilir olup olmadığını ölçmeye yardımcı olur.

Kaynak: https://arxiv.org/abs/2309.15217

### 3. B2B Sales İçin Predictive Modeling

Rezazadeh (2020), "A Generalized Flow for B2B Sales Predictive Modeling: An Azure Machine Learning Approach" çalışmasında B2B sales outcome prediction problemini historical sales opportunity data kullanan bir machine learning workflow olarak ele alır. Bu, BizPilot AI'ın lead-qualification kısmını destekler çünkü proje inbound lead'in conversion ihtimalini tahmin etmelidir. Çalışma sales prediction problemini probabilistic classification olarak ele aldığı için Kaggle lead-scoring dataset üzerinde Logistic Regression ile kurulan Week 1 baseline modeliyle uyumludur.

Kaynak: https://arxiv.org/abs/2002.01441

### 4. B2B Bağlamında Dynamic Scoring

Sinha et al. (2022), "B2B Advertising: Joint Dynamic Scoring of Account and Users" çalışması, B2B advertising içinde hem account hem user scoring konusuna odaklanır. B2B satın alma kararları uzun sürebilir ve birden fazla kişiyi içerebilir. BizPilot AI'ın ilk lead-scoring modülü daha basittir; ancak bu çalışma, business-development sistemlerinin behavioral signals üzerinden lead ve account önceliklendirmesi yapması gerektiği fikrini destekler. Ayrıca ranked lead'in personalized message ile eşleştirileceği future outreach module için de dayanak sağlar.

Kaynak: https://arxiv.org/abs/2209.14250

### BizPilot AI ile Bağlantı

İncelenen çalışmalar BizPilot AI'ın planlanan mimarisini destekler. RAG literatürü document-grounded chatbot fikrini gerekçelendirir. RAGAS, faithfulness, context precision ve answer relevancy için objective evaluation sağlar. B2B predictive modeling literatürü ise structured lead-scoring dataset ve classification model kullanarak conversion likelihood tahmini yapılmasını destekler. Birlikte bu kaynaklar Week 1 MVP yönünü gerekçelendirir: Python ve Streamlit tabanlı bir uygulama, lead-scoring baseline, ileride RAG ingestion için sample company documents ve LangChain, ChromaDB, LangGraph, Tavily/SerpAPI ve RAGAS entegrasyonuna hazırlık.

### References / Kaynaklar

1. Lewis, P., Perez, E., Piktus, A., Petroni, F., Karpukhin, V., Goyal, N., Kuttler, H., Lewis, M., Yih, W., Rocktaschel, T., Riedel, S., & Kiela, D. (2020). Retrieval-Augmented Generation for Knowledge-Intensive NLP Tasks. arXiv. https://arxiv.org/abs/2005.11401
2. Es, S., James, J., Espinosa-Anke, L., & Schockaert, S. (2023). RAGAS: Automated Evaluation of Retrieval Augmented Generation. arXiv. https://arxiv.org/abs/2309.15217
3. Rezazadeh, A. (2020). A Generalized Flow for B2B Sales Predictive Modeling: An Azure Machine Learning Approach. arXiv. https://arxiv.org/abs/2002.01441
4. Sinha, A. R., Choudhary, G., Agarwal, M., Bindal, S., Pande, A., & Girabawe, C. (2022). B2B Advertising: Joint Dynamic Scoring of Account and Users. arXiv. https://arxiv.org/abs/2209.14250
