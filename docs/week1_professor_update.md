# Week 1 Professor Update / 1. Hafta Profesör Güncellemesi

## English

Dear Professor,

I have started the internship project "BizPilot AI: An Agentic RAG-Powered Chatbot for Digital Business Development" according to the provided objectives, tools, timeline, and deliverables.

During Week 1, I focused on requirement study, tool setup, sample company documents, Kaggle lead-scoring dataset preparation, initial literature review, and a simple Streamlit MVP interface.

Current progress:

- Reviewed the project requirements and kept the scope focused on digital business development.
- Created the initial GitHub-ready project structure.
- Prepared sample company documents for the future RAG pipeline: product sheet, pricing sheet, FAQ, and past proposal.
- Selected and downloaded the Kaggle Lead Scoring Dataset locally.
- Cleaned the dataset and prepared it for machine learning.
- Trained a Logistic Regression baseline model for lead conversion prediction.
- Created a lead-scoring prediction wrapper that returns ML conversion probability, score out of 100, rule-based adjustment, final potential label, and short explanation.
- Built a professional Streamlit MVP interface with Turkish / English language switching.
- Started the literature review with RAG, RAGAS, and B2B predictive scoring references.
- Initialized Git and pushed the project to GitHub.

Dataset and model status:

- Raw dataset size: 9,240 rows and 37 columns
- Cleaned dataset size: 7,484 rows and 28 columns
- Target column: `Converted`
- Model: scikit-learn Logistic Regression
- Accuracy: 0.7902
- Precision: 0.7261
- Recall: 0.7555
- F1: 0.7405
- ROC-AUC: 0.8703

GitHub repository:

```text
https://github.com/SemihSan/Graphic-Era-University-Internship-Project---BizPilot-AI-
```

Next, I will implement the real RAG Q&A pipeline using LangChain, sentence-transformers embeddings, and ChromaDB/FAISS so the chatbot can answer questions from the sample company documents with cited sources.

Regards,

Semih

## Türkçe

Sayın Hocam,

"BizPilot AI: An Agentic RAG-Powered Chatbot for Digital Business Development" internship projesine verilen objectives, tools, timeline ve deliverables doğrultusunda başladım.

Week 1 kapsamında requirement study, tool setup, sample company documents, Kaggle lead-scoring dataset hazırlığı, initial literature review ve basit bir Streamlit MVP interface üzerine çalıştım.

Mevcut ilerleme:

- Proje gereksinimleri incelendi ve kapsam digital business development odağında tutuldu.
- GitHub'a hazır ilk proje klasör yapısı oluşturuldu.
- Gelecekteki RAG pipeline için sample company documents hazırlandı: product sheet, pricing sheet, FAQ ve past proposal.
- Kaggle Lead Scoring Dataset lokal olarak seçildi ve indirildi.
- Dataset temizlendi ve machine learning için hazırlandı.
- Lead conversion prediction için Logistic Regression baseline modeli eğitildi.
- ML conversion probability, 100 üzerinden skor, rule-based adjustment, final potential label ve kısa açıklama döndüren lead-scoring prediction wrapper oluşturuldu.
- Türkçe / English language switching destekleyen profesyonel Streamlit MVP interface oluşturuldu.
- RAG, RAGAS ve B2B predictive scoring referanslarıyla literature review başlatıldı.
- Git başlatıldı ve proje GitHub'a push edildi.

Dataset ve model durumu:

- Raw dataset boyutu: 9,240 satır ve 37 sütun
- Temizlenmiş dataset boyutu: 7,484 satır ve 28 sütun
- Hedef kolon: `Converted`
- Model: scikit-learn Logistic Regression
- Accuracy: 0.7902
- Precision: 0.7261
- Recall: 0.7555
- F1: 0.7405
- ROC-AUC: 0.8703

GitHub repository:

```text
https://github.com/SemihSan/Graphic-Era-University-Internship-Project---BizPilot-AI-
```

Sonraki adımda LangChain, sentence-transformers embeddings ve ChromaDB/FAISS kullanarak gerçek RAG Q&A pipeline'ını kuracağım. Böylece chatbot sample company documents üzerinden kaynak göstererek cevap verebilecek.

Saygılarımla,

Semih
