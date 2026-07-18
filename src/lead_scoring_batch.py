from __future__ import annotations

import argparse
import os
import time
from pathlib import Path

import pandas as pd

try:
    from src.lead_scoring_predictor import load_model, score_lead
except ImportError:
    from lead_scoring_predictor import load_model, score_lead


ROOT_DIR = Path(__file__).resolve().parents[1]
DEFAULT_INPUT_PATH = ROOT_DIR / "data" / "crm_sample_leads" / "crm_leads_sample.csv"
DEFAULT_OUTPUT_PATH = ROOT_DIR / "data" / "crm_sample_leads" / "scored_crm_leads.csv"
DEFAULT_LLM_BATCH_DELAY_SECONDS = 1.5


def score_crm_dataset(input_path: Path, output_path: Path, use_llm: bool = False) -> pd.DataFrame:
    if not input_path.exists():
        raise FileNotFoundError(f"CRM sample dataset not found: {input_path}")

    model = load_model()
    df = pd.read_csv(input_path)
    scored_rows = []

    batch_delay_seconds = get_llm_batch_delay_seconds() if use_llm else 0.0

    for index, row in df.iterrows():
        lead_data = row.to_dict()
        result = score_lead(lead_data, model=model, use_llm_explanation=use_llm)
        scored_rows.append(
            {
                **lead_data,
                "ml_probability": result["ml_probability"],
                "ml_score": result["ml_score"],
                "rule_adjustment": result["rule_adjustment"],
                "final_score": result["final_score"],
                "label": result["label"],
                "explanation": result["explanation"],
                "explanation_provider": result.get("explanation_provider", "template"),
                "llm_explanation_used": result.get("llm_explanation_used", False),
                "llm_error": result.get("llm_error", ""),
            }
        )
        if batch_delay_seconds > 0 and index < len(df) - 1:
            time.sleep(batch_delay_seconds)

    output_df = pd.DataFrame(scored_rows)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_df.to_csv(output_path, index=False)
    return output_df


def get_llm_batch_delay_seconds() -> float:
    raw_value = os.getenv("LLM_BATCH_DELAY_SECONDS", "").strip()
    if not raw_value:
        return DEFAULT_LLM_BATCH_DELAY_SECONDS

    try:
        delay_seconds = float(raw_value)
    except ValueError:
        return DEFAULT_LLM_BATCH_DELAY_SECONDS

    return max(0.0, min(30.0, delay_seconds))


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Score CRM-style sample leads with BizPilot AI")
    parser.add_argument("--input", type=Path, default=DEFAULT_INPUT_PATH, help="CRM-style input CSV path")
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT_PATH, help="Scored output CSV path")
    parser.add_argument("--llm", action="store_true", help="Use optional LLM explanation provider when configured")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    scored = score_crm_dataset(args.input, args.output, use_llm=args.llm)
    print("Lead scoring batch completed.")
    print(f"Input: {args.input}")
    print(f"Output: {args.output}")
    print(f"Rows scored: {len(scored)}")
    print(f"Average final score: {scored['final_score'].mean():.2f}")
    print(f"High priority leads: {(scored['final_score'] >= 75).sum()}")
    print("Explanation providers:")
    for provider, count in scored["explanation_provider"].value_counts().items():
        print(f"- {provider}: {count}")

    if "llm_error" in scored.columns:
        llm_errors = [
            str(error).strip()
            for error in scored["llm_error"].dropna().unique().tolist()
            if str(error).strip()
        ]
        if llm_errors:
            print("LLM provider errors:")
            for error in llm_errors[:3]:
                print(f"- {error}")


if __name__ == "__main__":
    main()
