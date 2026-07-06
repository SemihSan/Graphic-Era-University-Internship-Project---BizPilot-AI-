# Week 1 Literature Review Notes

This file records the first reading list for the Week 1 deliverable. The summaries are intentionally short so they can be expanded after reading the papers.

## RAG

1. Lewis et al. (2020), "Retrieval-Augmented Generation for Knowledge-Intensive NLP Tasks"
   - Source: https://arxiv.org/abs/2005.11401
   - Why it matters: introduces RAG as a way to combine parametric model knowledge with retrieved non-parametric memory.
   - Use in BizPilot AI: supports the company-document Q&A module, where answers must be grounded in product sheets, pricing, FAQs, and proposals.

2. Es et al. (2023/2025 revision), "Ragas: Automated Evaluation of Retrieval Augmented Generation"
   - Source: https://arxiv.org/abs/2309.15217
   - Why it matters: proposes reference-free RAG evaluation dimensions including faithful use of retrieved context and answer quality.
   - Use in BizPilot AI: directly matches the required metrics: faithfulness, context precision, and answer relevancy.

## Lead Scoring and Sales Prediction

3. Rezazadeh (2020), "A Generalized Flow for B2B Sales Predictive Modeling: An Azure Machine Learning Approach"
   - Source: https://arxiv.org/abs/2002.01441
   - Why it matters: frames B2B sales outcome prediction as an ML workflow using historical sales opportunities.
   - Use in BizPilot AI: supports the lead-qualification module and the idea of outputting conversion probability.

4. Sinha et al. (2022), "B2B Advertising: Joint Dynamic Scoring of Account and Users"
   - Source: https://arxiv.org/abs/2209.14250
   - Why it matters: discusses B2B account/user scoring over long buying cycles.
   - Use in BizPilot AI: supports ranking leads and explaining why some accounts are higher priority.

## Notes To Expand

- Compare simple rule-based lead scoring with predictive lead scoring.
- Explain why Logistic Regression is a good Week 1 baseline: interpretable, fast, and suitable for binary conversion prediction.
- Explain why XGBoost can be tested later if the baseline needs better performance.
- Connect RAG evaluation metrics to professor-required deliverables.
