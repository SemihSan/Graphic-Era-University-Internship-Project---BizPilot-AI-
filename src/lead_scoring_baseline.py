from __future__ import annotations

from pathlib import Path

import joblib
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (
    accuracy_score,
    classification_report,
    confusion_matrix,
    f1_score,
    precision_score,
    recall_score,
    roc_auc_score,
)
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler


ROOT_DIR = Path(__file__).resolve().parents[1]
RAW_DATA_PATH = ROOT_DIR / "data" / "lead_scoring" / "raw" / "Lead Scoring.csv"
PROCESSED_DIR = ROOT_DIR / "data" / "lead_scoring" / "processed"
MODELS_DIR = ROOT_DIR / "models"
REPORTS_DIR = ROOT_DIR / "reports"

TARGET_COLUMN = "Converted"

DROP_COLUMNS = [
    "Prospect ID",
    "Lead Number",
    # These columns are likely manual/post-lead labels or previous scoring outputs.
    "Tags",
    "Lead Quality",
    "Lead Profile",
    "Asymmetrique Activity Index",
    "Asymmetrique Profile Index",
    "Asymmetrique Activity Score",
    "Asymmetrique Profile Score",
]


def load_dataset() -> pd.DataFrame:
    if not RAW_DATA_PATH.exists():
        raise FileNotFoundError(f"Raw dataset not found: {RAW_DATA_PATH}")
    return pd.read_csv(RAW_DATA_PATH)


def clean_dataset(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()

    # In this Kaggle dataset, "Select" means the user did not provide a real value.
    df = df.replace("Select", pd.NA)

    existing_drop_columns = [col for col in DROP_COLUMNS if col in df.columns]
    df = df.drop(columns=existing_drop_columns)

    df = df.drop_duplicates()
    df = df.dropna(subset=[TARGET_COLUMN])

    return df


def build_pipeline(X: pd.DataFrame) -> Pipeline:
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

    preprocessor = ColumnTransformer(
        transformers=[
            ("num", numeric_pipeline, numeric_features),
            ("cat", categorical_pipeline, categorical_features),
        ]
    )

    model = LogisticRegression(
        max_iter=1000,
        class_weight="balanced",
        solver="liblinear",
        random_state=42,
    )

    return Pipeline(
        steps=[
            ("preprocessor", preprocessor),
            ("model", model),
        ]
    )


def get_top_features(pipeline: Pipeline, limit: int = 10) -> tuple[list[tuple[str, float]], list[tuple[str, float]]]:
    preprocessor = pipeline.named_steps["preprocessor"]
    model = pipeline.named_steps["model"]
    feature_names = preprocessor.get_feature_names_out()
    coefficients = model.coef_[0]

    pairs = sorted(zip(feature_names, coefficients), key=lambda item: item[1])
    negative = pairs[:limit]
    positive = pairs[-limit:][::-1]
    return positive, negative


def write_report(
    df_raw: pd.DataFrame,
    df_clean: pd.DataFrame,
    metrics: dict[str, float],
    report_text: str,
    positive_features: list[tuple[str, float]],
    negative_features: list[tuple[str, float]],
) -> None:
    REPORTS_DIR.mkdir(exist_ok=True)
    report_path = REPORTS_DIR / "lead_scoring_baseline.md"

    missing_top = df_clean.isna().sum().sort_values(ascending=False).head(12)

    lines = [
        "# Lead Scoring Baseline Report",
        "",
        "Bu rapor, BizPilot AI projesinin 1. hafta dataset hazırlığı için oluşturulan ilk Logistic Regression baseline sonucudur.",
        "",
        "## Dataset Özeti",
        "",
        f"- Raw dataset satır/sütun sayısı: `{df_raw.shape[0]}` satır, `{df_raw.shape[1]}` sütun",
        f"- Temizlenmiş dataset satır/sütun sayısı: `{df_clean.shape[0]}` satır, `{df_clean.shape[1]}` sütun",
        f"- Hedef kolon: `{TARGET_COLUMN}`",
        f"- Pozitif sınıf anlamı: lead müşteriye dönüştü",
        "",
        "## Temizleme Kararları",
        "",
        "- `Select` değerleri eksik veri olarak işaretlendi.",
        "- ID kolonları modelden çıkarıldı.",
        "- Manuel kalite etiketi veya önceki skor çıktısı olabilecek kolonlar çıkarıldı.",
        "- Eksik hedef değeri olan satırlar çıkarıldı.",
        "",
        "Çıkarılan kolonlar:",
        "",
    ]

    lines.extend([f"- `{col}`" for col in DROP_COLUMNS if col in df_raw.columns])

    lines.extend(
        [
            "",
            "## Eksik Değer Özeti",
            "",
        ]
    )
    lines.extend([f"- `{idx}`: `{int(value)}` eksik değer" for idx, value in missing_top.items() if value > 0])

    lines.extend(
        [
            "",
            "## Model",
            "",
            "- Model: scikit-learn Logistic Regression",
            "- Train/test split: 80/20, stratified",
            "- Numeric kolonlar: median imputation + standard scaling",
            "- Categorical kolonlar: most frequent imputation + one-hot encoding",
            "",
            "## Sonuçlar",
            "",
            f"- Accuracy: `{metrics['accuracy']:.4f}`",
            f"- Precision: `{metrics['precision']:.4f}`",
            f"- Recall: `{metrics['recall']:.4f}`",
            f"- F1: `{metrics['f1']:.4f}`",
            f"- ROC-AUC: `{metrics['roc_auc']:.4f}`",
            "",
            "## Classification Report",
            "",
            "```text",
            report_text,
            "```",
            "",
            "## Pozitif Dönüşümü Artıran İlk Sinyaller",
            "",
        ]
    )
    lines.extend([f"- `{name}`: `{coef:.4f}`" for name, coef in positive_features])

    lines.extend(
        [
            "",
            "## Pozitif Dönüşümü Azaltan İlk Sinyaller",
            "",
        ]
    )
    lines.extend([f"- `{name}`: `{coef:.4f}`" for name, coef in negative_features])

    lines.extend(
        [
            "",
            "## Not",
            "",
            "Bu baseline, 1. hafta teslimi için dataset'in hazırlanabildiğini ve lead scoring modelinin kurulabildiğini göstermek amacıyla hazırlanmıştır.",
        ]
    )

    report_path.write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    PROCESSED_DIR.mkdir(parents=True, exist_ok=True)
    MODELS_DIR.mkdir(exist_ok=True)

    df_raw = load_dataset()
    df_clean = clean_dataset(df_raw)

    X = df_clean.drop(columns=[TARGET_COLUMN])
    y = df_clean[TARGET_COLUMN].astype(int)

    X_train, X_test, y_train, y_test = train_test_split(
        X,
        y,
        test_size=0.2,
        random_state=42,
        stratify=y,
    )

    pipeline = build_pipeline(X_train)
    pipeline.fit(X_train, y_train)

    y_pred = pipeline.predict(X_test)
    y_proba = pipeline.predict_proba(X_test)[:, 1]

    metrics = {
        "accuracy": accuracy_score(y_test, y_pred),
        "precision": precision_score(y_test, y_pred),
        "recall": recall_score(y_test, y_pred),
        "f1": f1_score(y_test, y_pred),
        "roc_auc": roc_auc_score(y_test, y_proba),
    }

    report_text = classification_report(y_test, y_pred)
    positive_features, negative_features = get_top_features(pipeline)

    df_clean.to_csv(PROCESSED_DIR / "lead_scoring_cleaned.csv", index=False)
    joblib.dump(pipeline, MODELS_DIR / "lead_scoring_logreg.joblib")

    write_report(
        df_raw=df_raw,
        df_clean=df_clean,
        metrics=metrics,
        report_text=report_text,
        positive_features=positive_features,
        negative_features=negative_features,
    )

    print("Lead scoring baseline tamamlandı.")
    print(f"Raw shape: {df_raw.shape}")
    print(f"Clean shape: {df_clean.shape}")
    print(f"Confusion matrix:\n{confusion_matrix(y_test, y_pred)}")
    for name, value in metrics.items():
        print(f"{name}: {value:.4f}")
    print(f"Processed dataset: {PROCESSED_DIR / 'lead_scoring_cleaned.csv'}")
    print(f"Model: {MODELS_DIR / 'lead_scoring_logreg.joblib'}")
    print(f"Report: {REPORTS_DIR / 'lead_scoring_baseline.md'}")


if __name__ == "__main__":
    main()
