from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import joblib
import numpy as np
import pandas as pd
from sklearn.pipeline import Pipeline


ROOT_DIR = Path(__file__).resolve().parents[1]
MODEL_PATH = ROOT_DIR / "models" / "lead_scoring_logreg.joblib"

NUMERIC_COLUMNS = {
    "TotalVisits",
    "Total Time Spent on Website",
    "Page Views Per Visit",
}


def load_model() -> Pipeline:
    if not MODEL_PATH.exists():
        raise FileNotFoundError(
            f"Model bulunamadi: {MODEL_PATH}. Once src/lead_scoring_baseline.py calistirilmali."
        )
    return joblib.load(MODEL_PATH)


def get_expected_columns(model: Pipeline) -> list[str]:
    preprocessor = model.named_steps["preprocessor"]
    return preprocessor.feature_names_in_.tolist()


def build_input_frame(lead_data: dict[str, Any], model: Pipeline) -> pd.DataFrame:
    expected_columns = get_expected_columns(model)
    row = {}

    for column in expected_columns:
        value = lead_data.get(column, np.nan)
        if isinstance(value, str) and value == "Select":
            value = np.nan
        row[column] = value

    frame = pd.DataFrame([row], columns=expected_columns)

    for column in NUMERIC_COLUMNS:
        if column in frame.columns:
            frame[column] = pd.to_numeric(frame[column], errors="coerce")

    return frame


def apply_rule_adjustments(lead_data: dict[str, Any]) -> tuple[int, list[str]]:
    adjustment = 0
    reasons: list[str] = []

    do_not_email = str(lead_data.get("Do Not Email", "")).strip().lower()
    lead_origin = str(lead_data.get("Lead Origin", "")).strip().lower()
    occupation = str(lead_data.get("What is your current occupation", "")).strip().lower()

    total_visits = _to_float(lead_data.get("TotalVisits"))
    total_time = _to_float(lead_data.get("Total Time Spent on Website"))
    page_views = _to_float(lead_data.get("Page Views Per Visit"))

    if do_not_email == "no":
        adjustment += 4
        reasons.append("Email izni var, bu outreach icin olumlu bir sinyal.")
    elif do_not_email == "yes":
        adjustment -= 10
        reasons.append("Email izni yok, bu satis iletisimini zorlastirabilir.")

    if lead_origin == "lead add form":
        adjustment += 8
        reasons.append("Lead form doldurarak gelmis, bu daha yuksek niyet gosterebilir.")

    if occupation == "working professional":
        adjustment += 6
        reasons.append("Calisan profesyonel profili donusum icin olumlu gorunuyor.")
    elif occupation in {"student", "unemployed"}:
        adjustment -= 4
        reasons.append("Meslek bilgisi donusum olasiligini biraz dusuren grupta.")

    if total_time >= 900:
        adjustment += 7
        reasons.append("Web sitesinde uzun sure gecirmis.")
    elif total_time <= 60:
        adjustment -= 6
        reasons.append("Web sitesinde cok az sure gecirmis.")

    if total_visits >= 5:
        adjustment += 4
        reasons.append("Birden fazla ziyaret yapmis.")
    elif total_visits <= 1:
        adjustment -= 3
        reasons.append("Ziyaret sayisi dusuk.")

    if page_views >= 3:
        adjustment += 3
        reasons.append("Sayfa goruntuleme ortalamasi iyi.")

    if not reasons:
        reasons.append("Kural tabanli ek sinyal bulunmadi; skor agirlikli olarak ML modelinden geldi.")

    return adjustment, reasons


def score_lead(lead_data: dict[str, Any], model: Pipeline | None = None) -> dict[str, Any]:
    model = model or load_model()
    input_frame = build_input_frame(lead_data, model)

    ml_probability = float(model.predict_proba(input_frame)[0][1])
    ml_score = round(ml_probability * 100)
    rule_adjustment, reasons = apply_rule_adjustments(lead_data)
    final_score = max(0, min(100, ml_score + rule_adjustment))

    return {
        "ml_probability": round(ml_probability, 4),
        "ml_score": ml_score,
        "rule_adjustment": rule_adjustment,
        "final_score": final_score,
        "label": classify_score(final_score),
        "explanation": build_explanation(final_score, ml_score, rule_adjustment, reasons),
        "rule_reasons": reasons,
    }


def classify_score(score: int) -> str:
    if score >= 75:
        return "Yuksek Potansiyel"
    if score >= 50:
        return "Orta Potansiyel"
    return "Dusuk Potansiyel"


def build_explanation(final_score: int, ml_score: int, rule_adjustment: int, reasons: list[str]) -> str:
    direction = "artirdi" if rule_adjustment >= 0 else "azaltti"
    reason_text = " ".join(reasons[:3])
    return (
        f"Model bu lead icin {ml_score}/100 temel skor uretti. "
        f"Kural tabanli katman skoru {abs(rule_adjustment)} puan {direction}. "
        f"Final skor {final_score}/100 oldu. {reason_text}"
    )


def _to_float(value: Any) -> float:
    try:
        if value is pd.NA or value is None or value == "":
            return 0.0
        return float(value)
    except (TypeError, ValueError):
        return 0.0


def demo() -> None:
    sample_lead = {
        "Lead Origin": "Lead Add Form",
        "Lead Source": "Google",
        "Do Not Email": "No",
        "Do Not Call": "No",
        "TotalVisits": 6,
        "Total Time Spent on Website": 1250,
        "Page Views Per Visit": 3.5,
        "Last Activity": "SMS Sent",
        "Country": "India",
        "What is your current occupation": "Working Professional",
        "Last Notable Activity": "SMS Sent",
    }

    result = score_lead(sample_lead)
    print(json.dumps(result, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    demo()
