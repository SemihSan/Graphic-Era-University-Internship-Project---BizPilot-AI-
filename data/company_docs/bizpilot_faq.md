# BizPilot AI FAQ

Document type: FAQ
Source ID: faq_001

## Frequently Asked Questions

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
