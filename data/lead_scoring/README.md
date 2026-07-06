# Lead Scoring Dataset Plan

The lead-scoring module must use a public Kaggle lead-scoring dataset and train either Logistic Regression or XGBoost, as required by the professor.

## Candidate Datasets

Primary candidate:

- Name: Lead Scoring Dataset
- Source: Kaggle
- URL: https://www.kaggle.com/datasets/amritachatterjee09/lead-scoring-dataset

Fallback candidate:

- Name: Leads Dataset
- Source: Kaggle
- URL: https://www.kaggle.com/datasets/ashydv/leads-dataset

## Selection Criteria

Use the dataset that best satisfies these criteria after download:

- Contains inbound or marketing lead records.
- Contains a binary conversion target, such as `Converted`, `conversion`, or equivalent.
- Includes useful lead features such as source, activity level, visits, company profile, geography, interest level, or engagement.
- Has enough records for train/test split.
- Can be cleaned without needing private business data.

## Preparation Steps

1. Download the selected Kaggle dataset into `data/lead_scoring/raw/`. Done.
2. Inspect columns, target labels, missing values, duplicates, and class balance. Done.
3. Remove columns that leak the target or do not help prediction. Done.
4. Encode categorical features. Done in the scikit-learn pipeline.
5. Scale numeric features if Logistic Regression is used. Done in the scikit-learn pipeline.
6. Split into train/test sets. Done.
7. Train Logistic Regression as the Week 1 baseline. Done.
8. Save cleaned data into `data/lead_scoring/processed/`. Done locally.
9. Record baseline metrics: accuracy, precision, recall, F1, ROC-AUC. Done.
10. Document top positive and negative features for explainability. Done.

## Week 1 Baseline Result

Script:

- `src/lead_scoring_baseline.py`

Generated local outputs:

- `data/lead_scoring/processed/lead_scoring_cleaned.csv`
- `models/lead_scoring_logreg.joblib`
- `reports/lead_scoring_baseline.md`
- `src/lead_scoring_predictor.py`

Metrics:

- Accuracy: 0.7902
- Precision: 0.7261
- Recall: 0.7555
- F1: 0.7405
- ROC-AUC: 0.8703

Interpretation:

The first Logistic Regression baseline is good enough for the Week 1 dataset-ready deliverable. The next technical step is to wrap the trained model in a small prediction function so the future Streamlit app can score a new inbound lead.

## Prediction Wrapper

`src/lead_scoring_predictor.py` loads the trained model and scores a single new lead.

Example command:

```powershell
.venv\Scripts\python src\lead_scoring_predictor.py
```

The output includes:

- ML conversion probability
- ML score out of 100
- Rule-based adjustment
- Final hybrid score out of 100
- Potential label
- Short explanation

## Planned Hybrid Score

Final lead score = ML conversion probability + rule-based adjustment.

Example rule-based signals:

- Positive adjustment for business email domains.
- Positive adjustment for high website engagement.
- Positive adjustment for enterprise company size or strong buying intent.
- Negative adjustment for incomplete contact information.
- Negative adjustment for low engagement or irrelevant industry.

The LLM will explain the score using model probability, rule signals, and retrieved company context.
