# Data

This directory contains project data for BizPilot AI.

## Company Documents

`company_docs/` contains synthetic sample company documents for the RAG pipeline. These documents represent product sheets, pricing, FAQs, and past proposals for a digital business development assistant. They are safe to use for prototyping because they do not contain confidential company data.

## Lead Scoring

`lead_scoring/` contains the Kaggle lead-scoring dataset plan. Raw and processed datasets should be stored locally in:

- `data/lead_scoring/raw/`
- `data/lead_scoring/processed/`

These folders are ignored by Git to avoid committing downloaded datasets unless the dataset license clearly allows redistribution.
