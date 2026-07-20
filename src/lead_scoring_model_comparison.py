"""Lead scoring model comparison: Logistic Regression vs Random Forest vs XGBoost.

Reuses the Week 3 baseline data cleaning and preprocessing so the comparison is
apples-to-apples, then trains three models on the same train/test split and
reports accuracy, precision, recall, F1, and ROC-AUC side by side.

Run:
    python src/lead_scoring_model_comparison.py

Output:
    reports/lead_scoring_model_comparison.md
"""
from __future__ import annotations

from pathlib import Path

import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.ensemble import RandomForestClassifier
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (
    accuracy_score,
    f1_score,
    precision_score,
    recall_score,
    roc_auc_score,
)
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler

try:
    from src.lead_scoring_baseline import TARGET_COLUMN, clean_dataset, load_dataset
except ImportError:  # pragma: no cover - supports direct script execution
    from lead_scoring_baseline import TARGET_COLUMN, clean_dataset, load_dataset

try:
    from xgboost import XGBClassifier

    _HAS_XGBOOST = True
except ImportError:  # pragma: no cover - graceful degradation
    _HAS_XGBOOST = False


ROOT_DIR = Path(__file__).resolve().parents[1]
REPORTS_DIR = ROOT_DIR / "reports"
REPORT_PATH = REPORTS_DIR / "lead_scoring_model_comparison.md"


def build_preprocessor(X: pd.DataFrame) -> ColumnTransformer:
    numeric_features = X.select_dtypes(include=["number"]).columns.tolist()
    categorical_features = X.select_dtypes(exclude=["number"]).columns.tolist()

    numeric_pipeline = Pipeline(
        steps=[
            ("imputer", SimpleImputer(strategy="median")),
            ("scaler", StandardScaler()),
        ]
    )
    categorical_pipeline = Pipeline(
        steps=[
            ("imputer", SimpleImputer(strategy="most_frequent")),
            ("onehot", OneHotEncoder(handle_unknown="ignore", min_frequency=0.01)),
        ]
    )
    return ColumnTransformer(
        transformers=[
            ("num", numeric_pipeline, numeric_features),
            ("cat", categorical_pipeline, categorical_features),
        ]
    )


def build_models() -> dict[str, object]:
    models: dict[str, object] = {
        "Logistic Regression": LogisticRegression(
            max_iter=1000,
            class_weight="balanced",
            solver="liblinear",
            random_state=42,
        ),
        "Random Forest": RandomForestClassifier(
            n_estimators=300,
            class_weight="balanced",
            random_state=42,
            n_jobs=-1,
        ),
    }
    if _HAS_XGBOOST:
        models["XGBoost"] = XGBClassifier(
            n_estimators=400,
            max_depth=5,
            learning_rate=0.05,
            subsample=0.9,
            colsample_bytree=0.9,
            eval_metric="logloss",
            random_state=42,
            n_jobs=-1,
        )
    return models


def evaluate_models() -> dict[str, dict[str, float]]:
    df_clean = clean_dataset(load_dataset())
    X = df_clean.drop(columns=[TARGET_COLUMN])
    y = df_clean[TARGET_COLUMN].astype(int)

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )

    results: dict[str, dict[str, float]] = {}
    for name, estimator in build_models().items():
        pipeline = Pipeline(
            steps=[("preprocessor", build_preprocessor(X_train)), ("model", estimator)]
        )
        pipeline.fit(X_train, y_train)
        y_pred = pipeline.predict(X_test)
        y_proba = pipeline.predict_proba(X_test)[:, 1]
        results[name] = {
            "accuracy": accuracy_score(y_test, y_pred),
            "precision": precision_score(y_test, y_pred),
            "recall": recall_score(y_test, y_pred),
            "f1": f1_score(y_test, y_pred),
            "roc_auc": roc_auc_score(y_test, y_proba),
        }
    return results


def build_report(results: dict[str, dict[str, float]]) -> str:
    best_model = max(results, key=lambda name: results[name]["roc_auc"])
    metrics_order = ["accuracy", "precision", "recall", "f1", "roc_auc"]

    lines = [
        "# Lead Scoring Model Comparison / Lead Scoring Model Karşılaştırması",
        "",
        "Same cleaned Kaggle Lead Scoring dataset, same train/test split (80/20, "
        "stratified, random_state=42), same preprocessing. Only the classifier changes.",
        "",
        "## Results",
        "",
        "| Model | Accuracy | Precision | Recall | F1 | ROC-AUC |",
        "| --- | --- | --- | --- | --- | --- |",
    ]
    for name, metrics in results.items():
        row = " | ".join(f"{metrics[m]:.4f}" for m in metrics_order)
        lines.append(f"| {name} | {row} |")

    if not _HAS_XGBOOST:
        lines.append("")
        lines.append("> Note: XGBoost was not installed, so it was skipped.")

    lines.extend(
        [
            "",
            f"**Best model by ROC-AUC:** {best_model} "
            f"({results[best_model]['roc_auc']:.4f}).",
            "",
            "## Notes",
            "",
            "- The production app currently ships Logistic Regression for interpretability "
            "(clear coefficient-based reasons in the lead explanation).",
            "- Tree ensembles (Random Forest / XGBoost) are reported here to satisfy the "
            "project scope (\"Logistic Regression or XGBoost\") and to show the accuracy "
            "trade-off against interpretability.",
            "- Numbers are on a single hold-out split; cross-validation would tighten the estimates.",
        ]
    )
    return "\n".join(lines)


def main() -> None:
    REPORTS_DIR.mkdir(exist_ok=True)
    results = evaluate_models()
    report = build_report(results)
    REPORT_PATH.write_text(report, encoding="utf-8")

    print("Lead scoring model comparison complete.")
    for name, metrics in results.items():
        print(f"  {name}: ROC-AUC={metrics['roc_auc']:.4f} F1={metrics['f1']:.4f}")
    print(f"Report: {REPORT_PATH}")


if __name__ == "__main__":
    main()
