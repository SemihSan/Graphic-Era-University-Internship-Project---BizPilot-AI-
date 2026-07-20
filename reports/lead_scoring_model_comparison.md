# Lead Scoring Model Comparison / Lead Scoring Model Karşılaştırması

Same cleaned Kaggle Lead Scoring dataset, same train/test split (80/20, stratified, random_state=42), same preprocessing. Only the classifier changes.

## Results

| Model | Accuracy | Precision | Recall | F1 | ROC-AUC |
| --- | --- | --- | --- | --- | --- |
| Logistic Regression | 0.7902 | 0.7261 | 0.7555 | 0.7405 | 0.8703 |
| Random Forest | 0.8003 | 0.7434 | 0.7572 | 0.7502 | 0.8670 |
| XGBoost | 0.8116 | 0.7772 | 0.7352 | 0.7556 | 0.8857 |

**Best model by ROC-AUC:** XGBoost (0.8857).

## Notes

- The production app currently ships Logistic Regression for interpretability (clear coefficient-based reasons in the lead explanation).
- Tree ensembles (Random Forest / XGBoost) are reported here to satisfy the project scope ("Logistic Regression or XGBoost") and to show the accuracy trade-off against interpretability.
- Numbers are on a single hold-out split; cross-validation would tighten the estimates.