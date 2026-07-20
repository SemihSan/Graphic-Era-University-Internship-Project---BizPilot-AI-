# Week 5 RAG Evaluation Report / 5. Hafta RAG Değerlendirme Raporu

- Generated at (UTC): 2026-07-19T19:27:52.828955+00:00
- Retrieval top_k: 5
- LLM generation used: True
- Evaluation items: 8

## Aggregate Metrics

| Metric | Score |
| --- | --- |
| Faithfulness | 0.798 |
| Context Precision | 0.558 |
| Answer Relevancy | 0.735 |

Scores range from 0 to 1 (higher is better). Metrics use an LLM judge when a provider is reachable, otherwise an embedding-similarity fallback.

## Per-Question Results

| # | Question | Mode | Ctx | Faithfulness | Context Precision | Answer Relevancy |
| --- | --- | --- | --- | --- | --- | --- |
| 1 | How much does the BizPilot AI Starter plan cost and what does it include? | llm:openai | 5 | 0.893 | 0.520 | 0.853 |
| 2 | Which plan first includes CRM-style batch lead scoring? | llm:openai | 5 | 0.688 | 1.000 | 0.856 |
| 3 | What vector database and embedding model does the RAG pipeline use? | llm:openai | 5 | 0.592 | 0.800 | 0.821 |
| 4 | How does BizPilot AI qualify inbound leads? | llm:openai | 5 | 0.744 | 0.280 | 0.767 |
| 5 | What does the competitor-intelligence module do? | llm:openai | 5 | 0.909 | 0.400 | 0.610 |
| 6 | Who are the main users of BizPilot AI? | llm:openai | 5 | 0.805 | 0.130 | 0.816 |
| 7 | What can the outreach generator produce? | llm:openai | 5 | 0.863 | 0.333 | 0.533 |
| 8 | What is BizPilot AI? | llm:openai | 5 | 0.890 | 1.000 | 0.623 |

## Hallucination Guardrail Checks

Out-of-scope questions correctly refused: 2 / 2

| Question | Refused (no hallucination) | Contexts |
| --- | --- | --- |
| What is the capital of France? | yes | 0 |
| Give me BizPilot AI's exact 2027 revenue in US dollars. | yes | 5 |

## Notes

- Faithfulness measures whether the answer is grounded in the retrieved context.
- Context precision measures whether the retrieved chunks are relevant to the question.
- Answer relevancy measures whether the answer addresses the question.
- Guardrail checks confirm the system refuses out-of-scope questions instead of inventing facts.
