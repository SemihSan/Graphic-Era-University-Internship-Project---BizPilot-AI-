from __future__ import annotations

import json
import logging
import os
import re
from pathlib import Path

import pandas as pd
import streamlit as st

from src.lead_scoring_predictor import score_lead
from src.rag_pipeline import (
    COMPANY_DOCS_DATASET,
    DEFAULT_MAX_DISTANCE,
    answer_question,
    build_index,
    generate_extractive_answer,
    generate_llm_rag_answer,
    get_chroma_collection,
    retrieve,
)
from src.outreach_agent import generate_outreach
from src.competitor_intel import run_competitor_intelligence


ROOT_DIR = Path(__file__).resolve().parent
MODEL_PATH = ROOT_DIR / "models" / "lead_scoring_logreg.joblib"

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s: %(message)s")
logger = logging.getLogger("bizpilot")

# Guardrail for chat input length (defends against pathological / abusive input).
MAX_CHAT_CHARS = 2000
BASELINE_REPORT_PATH = ROOT_DIR / "reports" / "lead_scoring_baseline.md"
PROCESSED_DATA_PATH = ROOT_DIR / "data" / "lead_scoring" / "processed" / "lead_scoring_cleaned.csv"
CRM_SCORED_DATA_PATH = ROOT_DIR / "data" / "crm_sample_leads" / "scored_crm_leads.csv"

LABELS = {
    "tr": {
        "Yuksek Potansiyel": "Yüksek Potansiyel",
        "Orta Potansiyel": "Orta Potansiyel",
        "Dusuk Potansiyel": "Düşük Potansiyel",
    },
    "en": {
        "Yuksek Potansiyel": "High Potential",
        "Orta Potansiyel": "Medium Potential",
        "Dusuk Potansiyel": "Low Potential",
    },
}

REASON_TRANSLATIONS = {
    "Email izni var, bu outreach icin olumlu bir sinyal.": "Email permission is available, which is positive for outreach.",
    "Email izni yok, bu satis iletisimini zorlastirabilir.": "Email permission is missing, which may make sales outreach harder.",
    "Lead form doldurarak gelmis, bu daha yuksek niyet gosterebilir.": "The lead came through a form submission, which can indicate stronger intent.",
    "Calisan profesyonel profili donusum icin olumlu gorunuyor.": "The working professional profile is a positive conversion signal.",
    "Meslek bilgisi donusum olasiligini biraz dusuren grupta.": "The occupation category slightly reduces the conversion signal.",
    "Web sitesinde uzun sure gecirmis.": "The lead spent a long time on the website.",
    "Web sitesinde cok az sure gecirmis.": "The lead spent very little time on the website.",
    "Birden fazla ziyaret yapmis.": "The lead visited the website multiple times.",
    "Ziyaret sayisi dusuk.": "The visit count is low.",
    "Sayfa goruntuleme ortalamasi iyi.": "The average page views per visit is strong.",
    "Kural tabanli ek sinyal bulunmadi; skor agirlikli olarak ML modelinden geldi.": "No extra rule-based signal was found; the score mainly comes from the ML model.",
}

LEAD_PROMPT_FIELD_GUIDE = [
    {
        "key": "Lead Source",
        "label_tr": "Lead source",
        "label_en": "Lead source",
        "hint_tr": "Google, organic search, direct traffic, referral veya chat gibi kanal",
        "hint_en": "channel such as Google, organic search, direct traffic, referral, or chat",
    },
    {
        "key": "Lead Origin",
        "label_tr": "Lead origin",
        "label_en": "Lead origin",
        "hint_tr": "form doldurdu, landing page, API veya import gibi geliş kaynağı",
        "hint_en": "form submission, landing page, API, or import",
    },
    {
        "key": "Do Not Email",
        "label_tr": "Email permission",
        "label_en": "Email permission",
        "hint_tr": "email izni var veya email izni yok bilgisi",
        "hint_en": "whether email outreach is allowed or not allowed",
    },
    {
        "key": "What is your current occupation",
        "label_tr": "Current occupation",
        "label_en": "Current occupation",
        "hint_tr": "çalışan profesyonel, öğrenci veya işsiz gibi profil bilgisi",
        "hint_en": "working professional, student, or unemployed",
    },
    {
        "key": "TotalVisits",
        "label_tr": "Total visits",
        "label_en": "Total visits",
        "hint_tr": "siteyi kaç kez ziyaret ettiği",
        "hint_en": "how many times the lead visited the site",
    },
    {
        "key": "Total Time Spent on Website",
        "label_tr": "Time spent on website",
        "label_en": "Time spent on website",
        "hint_tr": "sitede kaç saniye geçirdiği",
        "hint_en": "how many seconds the lead spent on the site",
    },
    {
        "key": "Page Views Per Visit",
        "label_tr": "Page views per visit",
        "label_en": "Page views per visit",
        "hint_tr": "ziyaret başına ortalama sayfa görüntüleme",
        "hint_en": "average page views per visit",
    },
    {
        "key": "Last Activity",
        "label_tr": "Last activity",
        "label_en": "Last activity",
        "hint_tr": "son aktivite: SMS Sent, Email Opened veya Page Visited gibi",
        "hint_en": "last activity such as SMS Sent, Email Opened, or Page Visited",
    },
]
MIN_PROMPT_FIELDS_FOR_SCORING = 2
PROMPT_QUALIFICATION_SIGNAL_FIELDS = {
    "Lead Origin",
    "Do Not Email",
    "What is your current occupation",
    "TotalVisits",
    "Total Time Spent on Website",
    "Page Views Per Visit",
}


st.set_page_config(
    page_title="BizPilot AI",
    page_icon="BP",
    layout="wide",
    initial_sidebar_state="collapsed",
)


def inject_styles() -> None:
    st.markdown(
        """
        <style>
        #MainMenu, footer, header {visibility: hidden;}
        .block-container {
            padding-top: 1.6rem;
            padding-bottom: 2.5rem;
            max-width: 1180px;
        }
        .bp-hero {
            border: 1px solid #E5E7EB;
            background: linear-gradient(135deg, #FFFFFF 0%, #F0FDFA 55%, #FFFBEB 100%);
            padding: 24px 26px;
            border-radius: 8px;
            margin-bottom: 18px;
        }
        .bp-kicker {
            color: #0F766E;
            font-size: 0.82rem;
            font-weight: 700;
            letter-spacing: 0.02em;
            text-transform: uppercase;
            margin-bottom: 6px;
        }
        .bp-title {
            color: #18181B;
            font-size: 2.1rem;
            line-height: 1.15;
            font-weight: 800;
            margin: 0 0 8px;
        }
        .bp-subtitle {
            color: #52525B;
            max-width: 820px;
            font-size: 1rem;
            margin: 0;
        }
        .bp-chip-row {
            display: flex;
            flex-wrap: wrap;
            gap: 8px;
            margin-top: 16px;
        }
        .bp-chip {
            border: 1px solid #CCFBF1;
            background: #F0FDFA;
            color: #115E59;
            border-radius: 999px;
            padding: 6px 10px;
            font-size: 0.82rem;
            font-weight: 600;
        }
        .bp-card {
            border: 1px solid #E5E7EB;
            background: #FFFFFF;
            border-radius: 8px;
            padding: 18px;
            height: 100%;
        }
        .bp-card h3 {
            margin-top: 0;
            margin-bottom: 6px;
            font-size: 1.02rem;
            color: #18181B;
        }
        .bp-muted {
            color: #71717A;
            font-size: 0.92rem;
        }
        .bp-score {
            font-size: 3.2rem;
            line-height: 1;
            font-weight: 850;
            color: #0F766E;
            margin-bottom: 4px;
        }
        .bp-label {
            color: #18181B;
            font-size: 1rem;
            font-weight: 700;
        }
        .bp-section-title {
            color: #18181B;
            font-size: 1.25rem;
            font-weight: 800;
            margin: 8px 0 12px;
        }
        div[data-testid="stMetric"] {
            background: #FFFFFF;
            border: 1px solid #E5E7EB;
            border-radius: 8px;
            padding: 14px 16px;
        }
        div[data-testid="stTabs"] button {
            font-weight: 650;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


@st.cache_data
def load_dataset_preview() -> pd.DataFrame:
    if not PROCESSED_DATA_PATH.exists():
        return pd.DataFrame()
    return pd.read_csv(PROCESSED_DATA_PATH)


@st.cache_data
def load_public_corpus_preview() -> pd.DataFrame:
    rows: list[dict[str, str]] = []
    if not COMPANY_DOCS_DATASET.exists():
        return pd.DataFrame()

    for line in COMPANY_DOCS_DATASET.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        record = json.loads(line)
        rows.append(
            {
                "company": record.get("company", ""),
                "document_type": record.get("document_type", ""),
                "title": record.get("title", ""),
                "source_url": record.get("source_url", ""),
                "retrieved_date": record.get("retrieved_date", ""),
            }
        )
    return pd.DataFrame(rows)


@st.cache_data
def load_scored_crm_leads() -> pd.DataFrame:
    if not CRM_SCORED_DATA_PATH.exists():
        return pd.DataFrame()
    return pd.read_csv(CRM_SCORED_DATA_PATH)


def option_values(df: pd.DataFrame, column: str, fallback: list[str]) -> list[str]:
    if df.empty or column not in df.columns:
        return fallback
    values = [str(value) for value in df[column].dropna().unique().tolist()]
    values = sorted(value for value in values if value and value != "nan")
    return values or fallback


def render_language_selector() -> str:
    cols = st.columns([1, 0.3])
    with cols[1]:
        language = st.radio(
            "Language",
            ["Türkçe", "English"],
            horizontal=True,
            label_visibility="collapsed",
        )
    return "en" if language == "English" else "tr"


def display_label(label: str, lang: str) -> str:
    return LABELS[lang].get(label, label)


def display_reason(reason: str, lang: str) -> str:
    if lang == "tr":
        return reason
    return REASON_TRANSLATIONS.get(reason, reason)


def display_explanation(result: dict, lang: str) -> str:
    if result.get("llm_explanation_used"):
        return result["explanation"]

    if lang == "tr":
        return build_turkish_display_explanation(result)

    if result.get("explanation_provider") in {"template", "template_fallback"}:
        return result["explanation"]

    direction = "increased" if result["rule_adjustment"] >= 0 else "decreased"
    translated_reasons = [display_reason(reason, "en") for reason in result["rule_reasons"]]
    return (
        f"The ML model produced a base score of {result['ml_score']}/100. "
        f"The rule-based layer {direction} the score by {abs(result['rule_adjustment'])} points. "
        f"The final score is {result['final_score']}/100. "
        f"{' '.join(translated_reasons[:3])}"
    )


def score_lead_for_ui(lead_data: dict) -> dict:
    return score_lead(lead_data, use_llm_explanation=True)


def build_turkish_display_explanation(result: dict) -> str:
    rule_adjustment = int(result.get("rule_adjustment", 0))
    if rule_adjustment > 0:
        adjustment_sentence = f"Kural tabanli katman skoru {rule_adjustment} puan artirdi."
    elif rule_adjustment < 0:
        adjustment_sentence = f"Kural tabanli katman skoru {abs(rule_adjustment)} puan azaltti."
    else:
        adjustment_sentence = "Kural tabanli katman skoru degistirmedi."

    reasons = result.get("rule_reasons", [])
    reason_text = " ".join(reasons[:3])
    label = display_label(result.get("label", ""), "tr")
    final_score = int(result.get("final_score", 0))

    if final_score >= 75:
        action = "Satis ekibinin oncelikli olarak takip etmesi mantikli."
    elif final_score >= 50:
        action = "Lead takip edilebilir, fakat once ek niyet sinyali toplamak iyi olur."
    else:
        action = "Daha guclu satin alma sinyali gelene kadar dusuk oncelikte tutulabilir."

    return (
        f"ML modeli bu lead icin {result.get('ml_score', 0)}/100 temel skor uretti. "
        f"{adjustment_sentence} Final skor {final_score}/100 oldu ({label}). "
        f"{reason_text} Onerilen aksiyon: {action}"
    )


def parse_lead_prompt(prompt: str, fallback_lead_data: dict | None, df: pd.DataFrame) -> dict:
    """Extract CRM-style lead fields from a short natural-language prompt."""
    lead_data = dict(fallback_lead_data or {})
    text = normalize_prompt_text(prompt)

    do_not_email = parse_do_not_email(text)
    if do_not_email:
        lead_data["Do Not Email"] = do_not_email

    lead_origin = match_known_value(
        text,
        option_values(df, "Lead Origin", ["Lead Add Form", "API", "Landing Page Submission", "Lead Import"]),
        {
            "Lead Add Form": [
                "lead add form",
                "add form",
                "form submission",
                "filled form",
                "submitted form",
                "form doldurdu",
                "formu doldurdu",
                "form doldurmus",
                "formu doldurmus",
                "form gonderdi",
                "formu gonderdi",
                "formdan geldi",
                "form ile geldi",
                "lead form",
                "web formu",
            ],
            "Landing Page Submission": [
                "landing page submission",
                "landing page",
                "landing pageden",
                "landing page'den",
            ],
            "Lead Import": ["lead import", "imported lead", "import edildi", "ice aktarildi"],
            "API": [" api ", "from api", "via api", "api ile"],
        },
    )
    if lead_origin:
        lead_data["Lead Origin"] = lead_origin

    lead_source = match_known_value(
        text,
        option_values(df, "Lead Source", ["Google", "Direct Traffic", "Organic Search", "Olark Chat", "Referral Sites"]),
        {
            "Google": ["google"],
            "Direct Traffic": ["direct traffic", "direct"],
            "Organic Search": ["organic search", "organic"],
            "Olark Chat": ["olark chat", "chat"],
            "Referral Sites": ["referral sites", "referral"],
        },
    )
    if lead_source:
        lead_data["Lead Source"] = lead_source

    occupation = match_known_value(
        text,
        option_values(df, "What is your current occupation", ["Working Professional", "Student", "Unemployed"]),
        {
            "Working Professional": ["working professional", "professional", "employee", "employed", "calisan", "profesyonel", "is sahibi"],
            "Student": ["student", "ogrenci"],
            "Unemployed": ["unemployed", "issiz"],
        },
    )
    if occupation:
        lead_data["What is your current occupation"] = occupation

    last_activity = match_known_value(
        text,
        option_values(df, "Last Activity", ["SMS Sent", "Email Opened", "Page Visited on Website"]),
        {
            "SMS Sent": ["sms sent", "sent sms", "sms", "sms gonderildi"],
            "Email Opened": ["email opened", "opened email", "email acti", "mail acti"],
            "Page Visited on Website": [
                "page visited on website",
                "visited page",
                "page visited",
                "sayfa ziyaret",
                "siteyi ziyaret",
                "siteye girmis",
                "siteye girdi",
            ],
        },
    )
    if last_activity:
        lead_data["Last Activity"] = last_activity

    last_notable_activity = match_known_value(
        text,
        option_values(df, "Last Notable Activity", ["SMS Sent", "Email Opened", "Modified"]),
        {
            "SMS Sent": ["last notable activity sms", "notable sms"],
            "Email Opened": ["last notable activity email", "notable email"],
            "Modified": ["modified"],
        },
    )
    if last_notable_activity:
        lead_data["Last Notable Activity"] = last_notable_activity

    total_visits = extract_number(
        text,
        [
            r"(?:total\s*)?visits?\s*(?:is|are|=|:)?\s*(\d+(?:\.\d+)?)",
            r"(\d+(?:\.\d+)?)\s*(?:total\s*)?visits?",
            r"(?:ziyaret|ziyaret sayisi|site ziyaret)\s*(?:=|:)?\s*(\d+(?:\.\d+)?)",
            r"(\d+(?:\.\d+)?)\s*ziyaret",
            r"(?:siteye|siteye girmis|siteye girdi|siteye girmisti)\s*(?:\w+\s*)?(\d+(?:\.\d+)?)\s*kere",
            r"(\d+(?:\.\d+)?)\s*kere\s*(?:siteye|siteye girmis|siteye girdi)",
        ],
    )
    if total_visits is not None:
        lead_data["TotalVisits"] = int(total_visits)

    total_time = extract_number(
        text,
        [
            r"(?:total\s*)?(?:time spent on website|website time|time spent)\s*(?:is|=|:)?\s*(\d+(?:\.\d+)?)",
            r"spent\s*(\d+(?:\.\d+)?)\s*(?:seconds|sec|s|minutes|min)?",
            r"(?:sitede|web sitesinde|website)\s*(\d+(?:\.\d+)?)\s*(?:saniye|sn|sec|seconds)",
            r"(\d+(?:\.\d+)?)\s*(?:saniye|sn|sec|seconds)",
        ],
    )
    if total_time is not None:
        lead_data["Total Time Spent on Website"] = int(total_time)

    page_views = extract_number(
        text,
        [
            r"page views per visit\s*(?:is|=|:)?\s*(\d+(?:\.\d+)?)",
            r"(\d+(?:\.\d+)?)\s*page views",
            r"(?:sayfa goruntuleme|sayfa goruntulemesi)\s*(?:=|:)?\s*(\d+(?:\.\d+)?)",
            r"(\d+(?:\.\d+)?)\s*sayfa goruntuleme",
        ],
    )
    if page_views is not None:
        lead_data["Page Views Per Visit"] = float(page_views)

    return lead_data


def normalize_prompt_text(prompt: str) -> str:
    text = prompt.lower()
    replacements = {
        "ç": "c",
        "ğ": "g",
        "ı": "i",
        "ö": "o",
        "ş": "s",
        "ü": "u",
    }
    for source, target in replacements.items():
        text = text.replace(source, target)
    return f" {text} "


def parse_do_not_email(text: str) -> str | None:
    if re.search(r"do not email\s*(?:is|=|:)?\s*yes", text):
        return "Yes"
    if re.search(r"do not email\s*(?:is|=|:)?\s*no", text):
        return "No"
    if any(
        phrase in text
        for phrase in [
            "does not allow email",
            "email not allowed",
            "email opt out",
            "opted out",
            "email izni yok",
            "mail izni yok",
            "eposta izni yok",
            "e-posta izni yok",
            "iletisim izni yok",
            "email atilmasin",
            "mail atilmasin",
            "email gonderilmesin",
        ]
    ):
        return "Yes"
    if any(
        phrase in text
        for phrase in [
            "email allowed",
            "can email",
            "email opt in",
            "opted in",
            "email izni var",
            "mail izni var",
            "eposta izni var",
            "e-posta izni var",
            "iletisim izni var",
            "email atilabilir",
            "mail atilabilir",
            "email gonderilebilir",
            "mail atmamiza izin veriyor",
            "email atmamiza izin veriyor",
            "mail gondermemize izin veriyor",
            "email gondermemize izin veriyor",
            "mail atabiliriz",
            "email atabiliriz",
            "mail gonderebiliriz",
            "email gonderebiliriz",
        ]
    ):
        return "No"
    return None


def match_known_value(text: str, options: list[str], aliases: dict[str, list[str]]) -> str | None:
    padded_text = f" {text} "
    for value in options:
        lowered = value.lower()
        if lowered in text:
            return value
        for alias in aliases.get(value, []):
            if alias.strip() in padded_text:
                return value
    return None


def extract_number(text: str, patterns: list[str]) -> float | None:
    for pattern in patterns:
        match = re.search(pattern, text)
        if match:
            try:
                return float(match.group(1))
            except ValueError:
                return None
    return None


def get_missing_lead_prompt_fields(lead_data: dict) -> list[dict[str, str]]:
    missing_fields: list[dict[str, str]] = []
    for field in LEAD_PROMPT_FIELD_GUIDE:
        value = lead_data.get(field["key"])
        if is_missing_lead_value(value):
            missing_fields.append(field)
    return missing_fields


def get_present_lead_prompt_fields(lead_data: dict) -> list[dict[str, str]]:
    present_fields: list[dict[str, str]] = []
    for field in LEAD_PROMPT_FIELD_GUIDE:
        value = lead_data.get(field["key"])
        if not is_missing_lead_value(value):
            present_fields.append(field)
    return present_fields


def validate_prompt_lead_for_scoring(lead_data: dict, lang: str) -> tuple[bool, str]:
    present_fields = get_present_lead_prompt_fields(lead_data)
    present_keys = {field["key"] for field in present_fields}
    has_qualification_signal = bool(present_keys.intersection(PROMPT_QUALIFICATION_SIGNAL_FIELDS))

    if len(present_fields) < MIN_PROMPT_FIELDS_FOR_SCORING:
        message = (
            "This prompt is too thin for lead scoring. I found only one CRM-style field, so the score would be misleading. "
            "Add at least one more lead signal such as form submission, email permission, occupation, visits, website time, or page views."
            if lang == "en"
            else "Bu prompt lead scoring icin fazla zayif. Sadece bir CRM-style alan bulundu, bu durumda skor yanıltıcı olur. "
            "Form doldurdu, email izni, meslek, ziyaret sayisi, sitede gecirilen sure veya sayfa goruntuleme gibi en az bir sinyal daha ekle."
        )
        return False, message

    if not has_qualification_signal:
        message = (
            "This prompt contains basic source/activity information, but no strong qualification signal. "
            "Add email permission, lead origin, occupation, visits, website time, or page views before scoring."
            if lang == "en"
            else "Bu prompt temel kaynak/aktivite bilgisi iceriyor ama guclu qualification sinyali yok. "
            "Skorlamadan once email izni, lead origin, meslek, ziyaret sayisi, sitede gecirilen sure veya sayfa goruntuleme ekle."
        )
        return False, message

    return True, ""


def is_missing_lead_value(value) -> bool:
    if value is None or value == "":
        return True
    try:
        return bool(pd.isna(value))
    except (TypeError, ValueError):
        return False


def render_prompt_quality_suggestions(lead_data: dict, lang: str) -> None:
    missing_fields = get_missing_lead_prompt_fields(lead_data)
    if not missing_fields:
        st.success(
            "Prompt contains the main lead fields needed for a reliable score."
            if lang == "en"
            else "Prompt, güvenilir skor için gereken ana lead alanlarını içeriyor."
        )
        return

    if lang == "en":
        st.info(
            "Some useful lead fields were not found in the prompt. They are treated as unknown, not as zero. "
            "Adding them can make the score more reliable and easier to explain."
        )
        st.markdown("**Missing information suggestions:**")
        for field in missing_fields:
            st.write(f"- {field['label_en']}: {field['hint_en']}")
        st.caption(
            "Example: Lead came from a Google form, email is allowed, working professional, "
            "6 visits, 1250 seconds on site, 3.5 page views per visit, last activity SMS Sent."
        )
        return

    st.info(
        "Prompt icinde bazi faydali lead alanlari bulunamadi. Bunlar 0 degil, bilinmiyor kabul edilir. "
        "Bu bilgileri eklersen skor daha guvenilir ve aciklanabilir olur."
    )
    st.markdown("**Eksik bilgi önerileri:**")
    for field in missing_fields:
        st.write(f"- {field['label_tr']}: {field['hint_tr']}")
    st.caption(
        "Ornek: Google uzerinden form doldurdu, email izni var, calisan profesyonel, "
        "6 ziyaret, sitede 1250 saniye, 3.5 sayfa goruntuleme, son aktivite SMS Sent."
    )


def render_baseline_report(lang: str) -> None:
    if lang == "tr":
        st.markdown(BASELINE_REPORT_PATH.read_text(encoding="utf-8"))
        return

    st.markdown(
        """
        # Lead Scoring Baseline Report

        This report summarizes the first Logistic Regression baseline created for the Week 1 dataset preparation of BizPilot AI.

        ## Dataset Summary

        - Raw dataset size: `9240` rows, `37` columns
        - Cleaned dataset size: `7484` rows, `28` columns
        - Target column: `Converted`
        - Positive class meaning: the lead converted into a customer

        ## Cleaning Decisions

        - `Select` values were treated as missing values.
        - ID columns were removed from model training.
        - Manual quality labels or previous scoring outputs were removed to reduce leakage risk.
        - Rows with missing target values were removed.

        Removed columns:

        - `Prospect ID`
        - `Lead Number`
        - `Tags`
        - `Lead Quality`
        - `Lead Profile`
        - `Asymmetrique Activity Index`
        - `Asymmetrique Profile Index`
        - `Asymmetrique Activity Score`
        - `Asymmetrique Profile Score`

        ## Model

        - Model: scikit-learn Logistic Regression
        - Train/test split: 80/20, stratified
        - Numeric columns: median imputation + standard scaling
        - Categorical columns: most frequent imputation + one-hot encoding

        ## Results

        - Accuracy: `0.7902`
        - Precision: `0.7261`
        - Recall: `0.7555`
        - F1: `0.7405`
        - ROC-AUC: `0.8703`

        ## Classification Report

        ```text
                      precision    recall  f1-score   support

                   0       0.84      0.81      0.82       904
                   1       0.73      0.76      0.74       593

            accuracy                           0.79      1497
           macro avg       0.78      0.78      0.78      1497
        weighted avg       0.79      0.79      0.79      1497
        ```

        ## Top Signals Increasing Conversion

        - `cat__Lead Origin_Lead Add Form`: `2.2730`
        - `cat__What is your current occupation_Working Professional`: `1.4245`
        - `num__Total Time Spent on Website`: `1.1186`
        - `cat__Lead Source_Olark Chat`: `0.9949`
        - `cat__Last Notable Activity_SMS Sent`: `0.8296`
        - `cat__Do Not Email_No`: `0.8269`

        ## Top Signals Decreasing Conversion

        - `cat__What is your current occupation_Unemployed`: `-1.1530`
        - `cat__Lead Origin_Landing Page Submission`: `-1.0636`
        - `cat__Do Not Email_Yes`: `-0.7543`
        - `cat__What is your current occupation_Student`: `-0.6879`
        - `cat__Lead Origin_API`: `-0.6518`

        ## Note

        This baseline proves that the Kaggle lead-scoring dataset can be cleaned, modeled, and used as the starting point for the lead qualification module. It is not the final model; later steps can add feature review, XGBoost comparison, stronger validation, and LLM-based explanation.
        """
    )


def render_header(lang: str) -> None:
    is_en = lang == "en"
    subtitle = (
        "An MVP dashboard combining RAG-based company knowledge, lead qualification, "
        "outreach drafts, and competitor intelligence for digital business development."
        if is_en
        else "Dijital iş geliştirme için RAG destekli chatbot, lead qualification, "
        "outreach taslakları ve competitor intelligence modüllerini bir araya getiren MVP paneli."
    )
    chips = (
        ["Week 1 MVP", "Lead Scoring active", "RAG documents ready", "Streamlit UI"]
        if is_en
        else ["Week 1 MVP", "Lead Scoring aktif", "RAG dokümanları hazır", "Streamlit UI"]
    )
    chip_html = "".join(f'<span class="bp-chip">{chip}</span>' for chip in chips)

    st.markdown(
        f"""
        <div class="bp-hero">
            <div class="bp-kicker">Graphic Era University Internship Project</div>
            <h1 class="bp-title">BizPilot AI</h1>
            <p class="bp-subtitle">{subtitle}</p>
            <div class="bp-chip-row">{chip_html}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_dashboard(lang: str) -> None:
    is_en = lang == "en"
    df = load_dataset_preview()
    corpus_df = load_public_corpus_preview()

    section_title = "Project Status" if is_en else "Proje Durumu"
    st.markdown(f'<div class="bp-section-title">{section_title}</div>', unsafe_allow_html=True)

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Clean Dataset" if is_en else "Temiz Dataset", f"{len(df):,}" if not df.empty else ("Not ready" if is_en else "Hazır değil"))
    col2.metric("Model", "Logistic Regression", "Baseline")
    col3.metric("ROC-AUC", "0.8703")
    col4.metric("RAG Corpus" if is_en else "RAG Corpus", str(len(corpus_df)))

    st.divider()

    left, right = st.columns([1.1, 0.9], gap="large")
    with left:
        title = "Working Module Today" if is_en else "Bugünkü Çalışan Parça"
        text = (
            "The Lead Qualification module is active. When the user enters lead data, "
            "the system produces a 0-100 final score using the ML model and rule-based adjustment."
            if is_en
            else "Lead Qualification modülü aktif. Kullanıcı lead bilgilerini girince sistem ML modeli "
            "ve kural tabanlı düzeltme ile 0-100 arasında final skor üretiyor."
        )
        st.markdown(
            f"""
            <div class="bp-card">
                <h3>{title}</h3>
                <p class="bp-muted">{text}</p>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with right:
        title = "Week 1 Delivery Focus" if is_en else "Week 1 Teslim Odağı"
        text = (
            "The proposal, sample company documents, Kaggle lead-scoring dataset preparation, "
            "and first baseline report are ready for Week 1 refinement."
            if is_en
            else "Proje önerisi, sample company documents, Kaggle lead-scoring dataset hazırlığı "
            "ve ilk baseline raporu Week 1 teslimi için hazır hale getiriliyor."
        )
        st.markdown(
            f"""
            <div class="bp-card">
                <h3>{title}</h3>
                <p class="bp-muted">{text}</p>
            </div>
            """,
            unsafe_allow_html=True,
        )

    if BASELINE_REPORT_PATH.exists():
        with st.expander("Show lead scoring baseline report" if is_en else "Lead scoring baseline raporunu göster"):
            render_baseline_report(lang)


def render_lead_qualification(lang: str) -> None:
    is_en = lang == "en"
    st.markdown('<div class="bp-section-title">Lead Qualification</div>', unsafe_allow_html=True)
    st.caption(
        "This screen uses the trained Logistic Regression model together with a simple business-rule layer."
        if is_en
        else "Bu ekran eğitilmiş Logistic Regression modelini ve basit business rule katmanını birlikte kullanır."
    )

    df = load_dataset_preview()

    with st.form("lead_prompt_only_form"):
        st.markdown("#### Prompt-only lead scoring" if is_en else "#### Sadece prompt ile lead skorlama")
        st.caption(
            "This mode does not require the structured form. BizPilot extracts CRM-style fields directly from the prompt."
            if is_en
            else "Bu mod structured form gerektirmez. BizPilot CRM-style alanlari dogrudan prompt'tan cikarir."
        )
        st.caption(
            "Missing fields are treated as unknown, not as zero."
            if is_en
            else "Yazilmayan alanlar 0 degil, bilinmiyor kabul edilir."
        )
        prompt_only_text = st.text_area(
            "Lead prompt" if is_en else "Lead prompt'u",
            value="",
            placeholder=(
                "Example: Lead came from Lead Add Form via Google. Email allowed. "
                "Working professional, 6 visits, spent 1250 seconds, 3.5 page views per visit, last activity SMS Sent."
                if is_en
                else "Ornek: Google uzerinden form doldurdu, email izni var, calisan profesyonel, "
                "6 ziyaret, sitede 1250 saniye, 3.5 sayfa goruntuleme, son aktivite SMS Sent."
            ),
            height=120,
        )
        prompt_submitted = st.form_submit_button(
            "Score Prompt Lead" if is_en else "Prompt Lead'i Skorla",
            use_container_width=True,
        )

    if prompt_submitted:
        parsed_lead = parse_lead_prompt(prompt_only_text, None, df)
        is_scoreable_prompt, prompt_validation_message = validate_prompt_lead_for_scoring(parsed_lead, lang)
        st.session_state["last_lead_prompt"] = prompt_only_text.strip()
        st.session_state["last_lead_input_mode"] = "prompt_only"

        if not prompt_only_text.strip():
            st.warning("Please enter a lead prompt." if is_en else "Lutfen lead prompt'u yaz.")
            st.session_state.pop("last_score", None)
            st.session_state.pop("last_prompt_missing_fields", None)
        elif not parsed_lead:
            st.warning(
                "No CRM-style lead fields were found in the prompt. Try mentioning lead origin, source, email permission, occupation, visits, website time, or page views."
                if is_en
                else "Prompt icinde CRM-style lead alani bulunamadi. Lead origin, source, email izni, occupation, visits, website time veya page views yazmayi dene."
            )
            st.session_state.pop("last_score", None)
            st.session_state.pop("last_prompt_missing_fields", None)
        elif not is_scoreable_prompt:
            st.warning(prompt_validation_message)
            st.info(
                "Example: Lead came from a Google form, email is allowed, working professional, 6 visits, 1250 seconds on site."
                if is_en
                else "Ornek: Google uzerinden form doldurdu, email izni var, calisan profesyonel, 6 ziyaret, sitede 1250 saniye kaldi."
            )
            with st.expander("Fields found in the prompt" if is_en else "Prompt icinde bulunan alanlar"):
                st.json(parsed_lead)
            st.session_state.pop("last_score", None)
            st.session_state["last_lead"] = parsed_lead
            st.session_state["last_prompt_missing_fields"] = get_missing_lead_prompt_fields(parsed_lead)
        else:
            st.session_state["last_lead"] = parsed_lead
            st.session_state["last_prompt_missing_fields"] = get_missing_lead_prompt_fields(parsed_lead)
            st.session_state["last_score"] = score_lead_for_ui(parsed_lead)

    with st.form("lead_form"):
        st.markdown("#### Structured form scoring" if is_en else "#### Structured form ile skorlama")
        c1, c2, c3 = st.columns(3)
        lead_origin = c1.selectbox(
            "Lead Origin",
            option_values(df, "Lead Origin", ["Lead Add Form", "API", "Landing Page Submission", "Lead Import"]),
        )
        lead_source = c2.selectbox(
            "Lead Source",
            option_values(df, "Lead Source", ["Google", "Direct Traffic", "Organic Search", "Olark Chat", "Referral Sites"]),
        )
        do_not_email = c3.selectbox("Do Not Email", ["No", "Yes"])

        c4, c5, c6 = st.columns(3)
        total_visits = c4.number_input("Total Visits", min_value=0, max_value=100, value=5, step=1)
        total_time = c5.number_input("Total Time Spent on Website", min_value=0, max_value=10000, value=900, step=50)
        page_views = c6.number_input("Page Views Per Visit", min_value=0.0, max_value=30.0, value=3.0, step=0.5)

        c7, c8, c9 = st.columns(3)
        occupation = c7.selectbox(
            "Current Occupation",
            option_values(df, "What is your current occupation", ["Working Professional", "Student", "Unemployed"]),
        )
        last_activity = c8.selectbox(
            "Last Activity",
            option_values(df, "Last Activity", ["SMS Sent", "Email Opened", "Page Visited on Website"]),
        )
        last_notable_activity = c9.selectbox(
            "Last Notable Activity",
            option_values(df, "Last Notable Activity", ["SMS Sent", "Email Opened", "Modified"]),
        )

        submitted = st.form_submit_button("Score Lead" if is_en else "Lead'i Skorla", use_container_width=True)

    if submitted:
        fallback_lead_data = {
            "Lead Origin": lead_origin,
            "Lead Source": lead_source,
            "Do Not Email": do_not_email,
            "Do Not Call": "No",
            "TotalVisits": total_visits,
            "Total Time Spent on Website": total_time,
            "Page Views Per Visit": page_views,
            "What is your current occupation": occupation,
            "Last Activity": last_activity,
            "Last Notable Activity": last_notable_activity,
        }
        lead_data = fallback_lead_data
        st.session_state["last_lead"] = lead_data
        st.session_state["last_lead_prompt"] = ""
        st.session_state.pop("last_prompt_missing_fields", None)
        st.session_state["last_score"] = score_lead_for_ui(lead_data)

    result = st.session_state.get("last_score")
    if result:
        score = int(result["final_score"])
        left, right = st.columns([0.8, 1.2], gap="large")

        with left:
            st.markdown(
                f"""
                <div class="bp-card">
                    <div class="bp-score">{score}/100</div>
                    <div class="bp-label">{display_label(result["label"], lang)}</div>
                    <p class="bp-muted">{"ML base score" if is_en else "ML temel skor"}: {result["ml_score"]}/100</p>
                    <p class="bp-muted">{"Rule adjustment" if is_en else "Kural düzeltmesi"}: {result["rule_adjustment"]:+d}</p>
                </div>
                """,
                unsafe_allow_html=True,
            )
            st.progress(score / 100)

        with right:
            st.markdown("#### Explanation" if is_en else "#### Açıklama")
            st.write(display_explanation(result, lang))
            st.caption(
                f"Score engine: ML + rules | Explanation provider: {result.get('explanation_provider', 'rule_template')}"
                if is_en
                else f"Skor motoru: ML + kurallar | Açıklama sağlayıcı: {result.get('explanation_provider', 'rule_template')}"
            )
            if result.get("llm_error") and not result.get("llm_explanation_used"):
                with st.expander("LLM fallback note" if is_en else "LLM fallback notu"):
                    st.write(result["llm_error"])
            st.markdown("#### Rule Signals" if is_en else "#### Kural Sinyalleri")
            for reason in result["rule_reasons"]:
                st.write(f"- {display_reason(reason, lang)}")
            if st.session_state.get("last_lead_prompt"):
                st.markdown("#### Prompt Quality" if is_en else "#### Prompt Kalitesi")
                render_prompt_quality_suggestions(st.session_state.get("last_lead", {}), lang)
            with st.expander("Parsed lead input" if is_en else "Parse edilen lead girdisi"):
                if st.session_state.get("last_lead_prompt"):
                    st.caption(
                        "Original prompt:"
                        if is_en
                        else "Orijinal prompt:"
                    )
                    st.write(st.session_state["last_lead_prompt"])
                st.json(st.session_state.get("last_lead", {}))
    else:
        st.info(
            "Enter lead information and score it to see the result here."
            if is_en
            else "Lead bilgilerini girip skorlama yaptığında sonuç burada görünecek."
        )


def render_crm_batch_results(lang: str) -> None:
    is_en = lang == "en"
    with st.expander("Show CRM-style batch scoring output" if is_en else "CRM-style batch skor sonucunu göster"):
        scored_df = load_scored_crm_leads()
        if scored_df.empty:
            st.info(
                "Batch output was not found. Run `.venv\\Scripts\\python.exe src\\lead_scoring_batch.py --llm` first."
                if is_en
                else "Batch output bulunamadı. Önce `.venv\\Scripts\\python.exe src\\lead_scoring_batch.py --llm` çalıştır."
            )
            return

        visible_columns = [
            "crm_lead_id",
            "company_name",
            "contact_name",
            "industry",
            "final_score",
            "label",
            "explanation_provider",
            "llm_explanation_used",
            "explanation",
            "llm_error",
        ]
        visible_columns = [column for column in visible_columns if column in scored_df.columns]
        st.dataframe(scored_df[visible_columns], use_container_width=True, hide_index=True)

        if "explanation_provider" in scored_df.columns:
            providers = scored_df["explanation_provider"].value_counts().to_dict()
            provider_summary = ", ".join(f"{name}: {count}" for name, count in providers.items())
            st.caption(
                f"Explanation providers: {provider_summary}"
                if is_en
                else f"Açıklama sağlayıcıları: {provider_summary}"
            )


def render_rag_workspace(lang: str) -> None:
    is_en = lang == "en"
    st.markdown('<div class="bp-section-title">RAG Q&A Workspace</div>', unsafe_allow_html=True)
    st.caption(
        "Test the Week 2 RAG prototype from the browser: read the synthetic BizPilot company corpus, build the ChromaDB index, ask questions, and view citations."
        if is_en
        else "Week 2 RAG prototipini tarayıcıdan test et: synthetic BizPilot company corpus'u oku, ChromaDB index'i oluştur, soru sor ve citation'ları gör."
    )

    corpus_df = load_public_corpus_preview()
    try:
        indexed_chunks = get_chroma_collection(reset=False).count()
        index_error = ""
    except Exception as exc:
        indexed_chunks = 0
        index_error = str(exc)

    metric_1, metric_2, metric_3 = st.columns(3)
    metric_1.metric("Corpus records" if is_en else "Corpus kaydı", len(corpus_df))
    metric_2.metric("Indexed chunks" if is_en else "Indexlenen chunk", indexed_chunks)
    metric_3.metric("Embedding", "all-MiniLM-L6-v2")

    if index_error:
        st.warning(
            f"ChromaDB index could not be read: {index_error}"
            if is_en
            else f"ChromaDB index okunamadı: {index_error}"
        )

    left, right = st.columns([0.9, 1.1], gap="large")
    with left:
        st.markdown("#### RAG Index")
        st.write(f"Dataset: `{COMPANY_DOCS_DATASET.relative_to(ROOT_DIR)}`")
        if st.button(
            "Build / Refresh ChromaDB Index" if is_en else "ChromaDB Index'i Oluştur / Yenile",
            use_container_width=True,
        ):
            try:
                with st.spinner("Building RAG index..." if is_en else "RAG index oluşturuluyor..."):
                    indexed_chunks = build_index(reset=True)
                st.success(
                    f"RAG index is ready. Indexed chunks: {indexed_chunks}"
                    if is_en
                    else f"RAG index hazır. Indexlenen chunk sayısı: {indexed_chunks}"
                )
            except Exception as exc:
                st.error(
                    f"Index build failed: {exc}"
                    if is_en
                    else f"Index oluşturma başarısız oldu: {exc}"
                )

        st.markdown("#### Corpus Preview" if is_en else "#### Corpus Önizleme")
        if corpus_df.empty:
            st.warning("Synthetic BizPilot corpus was not found." if is_en else "Synthetic BizPilot corpus bulunamadı.")
        else:
            st.dataframe(corpus_df, use_container_width=True, hide_index=True)

    with right:
        st.markdown("#### Ask RAG" if is_en else "#### RAG'e Soru Sor")
        question = st.text_input(
            "Question" if is_en else "Soru",
            value="Which plan is best for a growing sales team and why?",
            placeholder="Example: How does prompt-only lead qualification work?",
        )
        rag_prompt = st.text_area(
            "RAG answer prompt" if is_en else "RAG cevap prompt'u",
            value=(
                "Answer as a concise business-development assistant. "
                "Use short paragraphs and cite the relevant sources."
            ),
            help=(
                "This controls the answer style and business focus. It cannot override the retrieved context or citation rules."
                if is_en
                else "Bu alan cevabın stilini ve business odağını belirler. Retrieved context ve citation kurallarını override edemez."
            ),
            height=95,
        )
        top_k = st.slider(
            "Retrieved chunks" if is_en else "Getirilecek chunk sayısı",
            min_value=1,
            max_value=8,
            value=5,
        )
        use_llm_answer = st.checkbox(
            "Generate final answer with LLM" if is_en else "Final cevabı LLM ile üret",
            value=True,
            help=(
                "Retrieves ChromaDB context first, then sends only that context to the configured LLM provider."
                if is_en
                else "Önce ChromaDB context getirir, sonra sadece bu context'i yapılandırılmış LLM provider'a gönderir."
            ),
        )

        if st.button("Ask Question" if is_en else "Soruyu Çalıştır", use_container_width=True):
            if not question.strip():
                st.warning("Please enter a question." if is_en else "Lütfen bir soru yaz.")
            else:
                try:
                    with st.spinner(
                        "Retrieving context and generating answer..."
                        if is_en
                        else "Context getiriliyor ve cevap üretiliyor..."
                    ):
                        response = answer_question(
                            question.strip(),
                            top_k=top_k,
                            use_llm=use_llm_answer,
                            user_prompt=rag_prompt,
                        )
                    st.code(response, language="text")
                except Exception as exc:
                    st.error(
                        f"RAG question failed: {exc}"
                        if is_en
                        else f"RAG sorusu calismadi: {exc}"
                    )
                    st.info(
                        "If the index is empty, click Build / Refresh ChromaDB Index first."
                        if is_en
                        else "Index boşsa önce ChromaDB Index'i Oluştur / Yenile butonuna bas."
                    )


def render_outreach_preview(lang: str) -> None:
    is_en = lang == "en"
    st.markdown('<div class="bp-section-title">Agentic Outreach Generator</div>', unsafe_allow_html=True)
    st.caption(
        "An agentic pipeline (qualify → research → draft → critique) grounds the message in the lead score and company documents, then an LLM refines it."
        if is_en
        else "Agentic bir hat (qualify → research → draft → critique) mesajı lead skoru ve şirket dokümanlarına dayandırır, sonra bir LLM taslağı iyileştirir."
    )

    company = st.text_input("Prospect Company", value="Northstar CRM Solutions")
    contact = st.text_input("Contact Name", value="Aarav")
    pain_point = st.text_input(
        "Observed Need",
        value="inbound lead response and sales team productivity" if is_en else "inbound lead response ve satış ekibi verimliliği",
    )

    col_opts1, col_opts2 = st.columns(2)
    use_llm = col_opts1.checkbox(
        "Use LLM (uncheck for offline template)" if is_en else "LLM kullan (kapatınca offline template)",
        value=True,
    )
    use_rag = col_opts2.checkbox(
        "Use RAG research" if is_en else "RAG araştırması kullan",
        value=True,
    )

    generate = st.button(
        "Generate Outreach" if is_en else "Outreach Üret",
        type="primary",
        key="generate_outreach_btn",
    )

    if generate:
        last_score = st.session_state.get("last_score", {})
        lead_data = st.session_state.get("last_lead") or last_score.get("input_features") or {}
        spinner_text = "Running agentic outreach pipeline..." if is_en else "Agentic outreach hattı çalışıyor..."
        with st.spinner(spinner_text):
            try:
                result = generate_outreach(
                    company=company,
                    contact=contact,
                    pain_point=pain_point,
                    lead_data=lead_data,
                    use_rag=use_rag,
                    use_llm=use_llm,
                )
                st.session_state["last_outreach"] = result
            except Exception as exc:
                st.error(
                    f"Outreach generation failed: {exc}" if is_en else f"Outreach üretimi başarısız: {exc}"
                )

    result = st.session_state.get("last_outreach")
    if not result:
        st.info(
            "Fill in the prospect details and click Generate Outreach."
            if is_en
            else "Prospect bilgilerini doldur ve Outreach Üret butonuna bas."
        )
        return

    steps = " → ".join(result.get("steps", []))
    score = result.get("score")
    label = display_label(result.get("label", ""), lang)
    st.markdown(
        f"**{'Pipeline' if is_en else 'Hat'}:** `{steps}` &nbsp;|&nbsp; "
        f"**{'Orchestrator' if is_en else 'Orkestratör'}:** `{result.get('orchestrator', '')}` &nbsp;|&nbsp; "
        f"**{'Lead score' if is_en else 'Lead skoru'}:** {score}/100 ({label})"
    )
    st.caption(
        f"Draft: {result.get('draft_provider', '')} | Critique: {result.get('critique_provider', '')}"
    )
    if result.get("research_note"):
        st.caption(result["research_note"])
    for note in result.get("notes", []):
        st.caption(f"ℹ️ {note}")

    c1, c2 = st.columns(2, gap="large")
    with c1:
        st.markdown("#### Cold Email")
        st.code(result.get("email", ""), language="text")
    with c2:
        st.markdown("#### LinkedIn Message")
        st.code(result.get("linkedin", ""), language="text")

    research = result.get("research", [])
    if research:
        with st.expander("Retrieved company context" if is_en else "Getirilen şirket bağlamı"):
            for item in research:
                st.markdown(f"**{item.get('title', 'context')}**")
                st.caption(item.get("snippet", ""))


def render_competitor_intelligence(lang: str) -> None:
    is_en = lang == "en"
    st.markdown('<div class="bp-section-title">Competitor Intelligence</div>', unsafe_allow_html=True)
    st.caption(
        "Retrieves public web information via Tavily or SerpAPI (with a local corpus fallback) and summarizes it with an LLM."
        if is_en
        else "Tavily veya SerpAPI ile public web bilgisini getirir (yoksa yerel korpusa düşer) ve bir LLM ile özetler."
    )

    query = st.text_input(
        "Research Query" if is_en else "Araştırma Sorgusu",
        value="AI lead scoring SaaS competitors",
        key="competitor_query",
    )
    col1, col2 = st.columns(2)
    max_results = col1.slider(
        "Max results" if is_en else "Maksimum sonuç",
        min_value=3,
        max_value=10,
        value=5,
    )
    use_llm = col2.checkbox(
        "Summarize with LLM" if is_en else "LLM ile özetle",
        value=True,
        key="competitor_use_llm",
    )

    if st.button("Run Competitor Research" if is_en else "Rakip Araştırması Çalıştır", key="competitor_btn"):
        spinner_text = "Retrieving and summarizing..." if is_en else "Getiriliyor ve özetleniyor..."
        with st.spinner(spinner_text):
            try:
                st.session_state["last_competitor"] = run_competitor_intelligence(
                    query, max_results=max_results, use_llm=use_llm
                )
            except Exception as exc:
                st.error(
                    f"Competitor research failed: {exc}" if is_en else f"Rakip araştırması başarısız: {exc}"
                )

    result = st.session_state.get("last_competitor")
    if not result:
        st.info(
            "Enter a query and click Run Competitor Research."
            if is_en
            else "Bir sorgu gir ve Rakip Araştırması Çalıştır butonuna bas."
        )
        return

    st.caption(
        f"Provider: {result.get('retrieval_provider', '')} | {result.get('retrieval_note', '')}"
    )
    if result.get("summary"):
        st.markdown("#### Summary" if is_en else "#### Özet")
        st.write(result["summary"])
        st.caption(f"Summary provider: {result.get('summary_provider', '')}")

    results = result.get("results", [])
    if results:
        st.markdown("#### Sources" if is_en else "#### Kaynaklar")
        for index, item in enumerate(results, start=1):
            title = item.get("title", "result")
            url = item.get("source_url") or item.get("url") or ""
            st.markdown(f"**[{index}] {title}**")
            snippet = item.get("snippet") or item.get("content") or ""
            if snippet:
                st.caption(snippet)
            if url:
                st.caption(url)


CHAT_INTENT_KEYWORDS = {
    "competitor": [
        "competitor", "competitors", "rakip", "rakipler", "vs ", "versus", "compare",
        "comparison", "market", "hubspot", "salesforce", "pipedrive", "alternative",
    ],
    "outreach": [
        "outreach", "cold email", "email to", "linkedin", "mesaj yaz", "draft", "write an email",
        "reach out", "e-posta", "eposta", "outreach yaz", "teklif", "proposal", "pitch",
        "teklif ver", "teklif yaz", "teklif sun", "satış maili", "satis maili", "mail at",
        "mail yaz", "iletişime geç", "iletisime gec",
        "give an order", "give a order", "place an order", "order to", "make a deal",
        "close a deal", "sell to", "want to sell", "pitch to", "do business with",
        "get in touch", "sunum yap", "anlaşma", "anlasma", "iş yap", "is yap", "sat ",
    ],
    "lead": [
        "lead score", "score this lead", "qualify", "skorla", "puanla", "lead skor",
        "how good is this lead", "lead quality",
    ],
}


def classify_chat_intent(text: str) -> str:
    """Route a chat message to a module using scored keyword matching.

    Counts keyword hits per intent and returns the highest-scoring one. Ties are
    broken by priority (competitor > outreach > lead); if nothing matches, the
    message falls back to document RAG Q&A.
    """
    lowered = f" {text.lower()} "
    scores = {
        intent: sum(1 for keyword in keywords if keyword in lowered)
        for intent, keywords in CHAT_INTENT_KEYWORDS.items()
    }
    best_intent = max(
        ("competitor", "outreach", "lead"),
        key=lambda intent: scores[intent],
    )
    if scores[best_intent] > 0:
        logger.debug("chat intent=%s scores=%s", best_intent, scores)
        return best_intent
    logger.debug("chat intent=rag scores=%s", scores)
    return "rag"



def _extract_outreach_company(text: str) -> str:
    # 1) "for/to/için Acme" — hedef eylemden ÖNCE gelen büyük harfli ad.
    match = re.search(r"(?:for|to|için|icin)\s+([A-ZÇĞİÖŞÜ][\w&.\- ]{2,40})", text)
    if match:
        return match.group(1).strip(" .")

    # 2) "Acme için ..." — şirket adı "için/icin" edatından önce.
    before = re.search(r"([A-ZÇĞİÖŞÜ][\w&.\-]{2,40})\s+(?:için|icin)\b", text)
    if before:
        return before.group(1).strip(" .")

    stopwords = {
        "için", "icin", "bir", "for", "to", "the", "and", "bu", "ve", "bize", "size",
        "me", "us", "them", "you", "him", "her", "it", "someone", "them.",
        "make", "give", "get", "do", "have", "take", "place", "close", "sell",
        "want", "reach", "send", "write", "draft", "an", "a", "some", "any",
    }

    # 3) İngilizce "to/with <company>" (küçük harf de olabilir): "order to microsoft",
    #    "make a deal with Salesforce". İlk stopword/fiil olmayan adayı seç.
    for candidate in re.finditer(r"\b(?:to|with)\s+([A-Za-z][\w&.\-]{2,40})", text):
        raw = candidate.group(1).strip(" .")
        if raw.lower() not in stopwords:
            return raw[:1].upper() + raw[1:]

    # 4) Türkçe yönelme hâli: "Microsoft'a / microsofta bir teklif / mail / mesaj ...".
    target_words = r"(?:teklif|mail|e-?posta|eposta|mesaj|ulaş|ulas|outreach)"
    dative = re.search(
        rf"([A-Za-zÇĞİÖŞÜçğıöşü][\w&.\-]{{1,40}}?)(['’`])?([ae])?\s+(?:bir\s+)?{target_words}",
        text,
    )
    if dative:
        raw = dative.group(1).strip(" .")
        had_apostrophe = dative.group(2) is not None
        if raw.lower() in stopwords:
            return ""
        # Kesme işareti YOKSA ("microsofta") sondaki yönelme ekini (a/e) temizle.
        if not had_apostrophe and len(raw) > 4 and raw[-1].lower() in "ae" and raw[-2].lower() not in "aeıioöuü":
            raw = raw[:-1]
        return raw[:1].upper() + raw[1:]
    return ""


def answer_chat_rag(text: str) -> dict:
    retrieved = retrieve(text, top_k=5, max_distance=DEFAULT_MAX_DISTANCE)
    if not retrieved:
        return {
            "answer": (
                "I could not find this in BizPilot AI's company documents, so I will not guess. "
                "Try asking about pricing, plans, RAG architecture, lead scoring, outreach, "
                "onboarding, support, security, or competitor intelligence."
            ),
            "citations": [],
            "mode": "no_context",
        }
    llm = generate_llm_rag_answer(text, retrieved)
    if llm["llm_used"]:
        answer = str(llm["answer"])
        mode = f"llm:{llm['provider']}"
    else:
        answer = generate_extractive_answer(text, retrieved)
        mode = "extractive_fallback"
    best_distance = min(row["distance"] for row in retrieved)
    if best_distance > 1.2:
        answer = (
            "Note: this topic is only weakly covered by BizPilot AI's documents, so treat the "
            "answer with caution.\n\n" + answer
        )
    citations = []
    for index, row in enumerate(retrieved, start=1):
        meta = row["metadata"]
        citations.append(f"[{index}] {meta.get('title', meta.get('document_type', 'context'))} — {meta.get('source_url', '')}")
    return {"answer": answer, "citations": citations, "mode": mode}


def route_chat_message(text: str, lang: str) -> dict:
    """Dispatch a chat message to the right module. Returns a render spec."""
    is_en = lang == "en"
    intent = classify_chat_intent(text)

    if intent == "competitor":
        result = run_competitor_intelligence(text, max_results=5, use_llm=True)
        body = result.get("summary", "")
        sources = [
            f"[{i}] {r.get('title', 'result')} — {r.get('source_url') or r.get('url', '')}"
            for i, r in enumerate(result.get("results", []), start=1)
        ]
        meta = f"Competitor Intelligence · {result.get('retrieval_provider', '')} · {result.get('summary_provider', '')}"
        return {"intent": intent, "answer": body, "sources": sources, "meta": meta}

    if intent == "outreach":
        company = _extract_outreach_company(text) or "the prospect company"
        last_lead = st.session_state.get("last_lead") or {}
        result = generate_outreach(
            company=company,
            contact="there",
            pain_point="",
            lead_data=last_lead,
            use_rag=True,
            use_llm=True,
        )
        body = (
            f"**Cold Email**\n\n{result.get('email', '')}\n\n---\n\n"
            f"**LinkedIn**\n\n{result.get('linkedin', '')}"
        )
        meta = (
            f"Outreach · {' → '.join(result.get('steps', []))} · "
            f"score {result.get('score')}/100 · {result.get('draft_provider', '')}"
        )
        return {"intent": intent, "answer": body, "sources": [], "meta": meta}

    if intent == "lead":
        msg = (
            "To score a lead I need its CRM fields. Open the **Lead Qualification** tab and "
            "either paste a short lead description or fill the structured form. Once scored, "
            "you can ask me here to draft outreach for it."
            if is_en
            else "Bir lead'i skorlamak için CRM alanları gerekli. **Lead Qualification** sekmesine geçip "
            "kısa bir lead açıklaması yaz ya da formu doldur. Skorladıktan sonra buradan onun için "
            "outreach üretmemi isteyebilirsin."
        )
        return {"intent": intent, "answer": msg, "sources": [], "meta": "Lead Qualification"}

    rag = answer_chat_rag(text)
    return {"intent": "rag", "answer": rag["answer"], "sources": rag["citations"], "meta": f"RAG Q&A · {rag['mode']}"}


def render_chatbot(lang: str) -> None:
    is_en = lang == "en"
    st.markdown('<div class="bp-section-title">BizPilot AI Chatbot</div>', unsafe_allow_html=True)
    st.caption(
        "One chat that routes your message to the right module: company-document Q&A, "
        "competitor intelligence, or outreach drafting. Lead scoring stays in its own tab."
        if is_en
        else "Mesajını doğru modüle yönlendiren tek sohbet: şirket-doküman Q&A, rakip analizi "
        "veya outreach yazımı. Lead skorlama kendi sekmesinde kalır."
    )

    if "chat_history" not in st.session_state:
        st.session_state["chat_history"] = []

    if st.button("Clear chat" if is_en else "Sohbeti temizle", key="clear_chat"):
        st.session_state["chat_history"] = []

    for message in st.session_state["chat_history"]:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
            if message.get("meta"):
                st.caption(message["meta"])
            for source in message.get("sources", []):
                st.caption(source)

    placeholder = (
        "Ask about pricing, a competitor, or say 'write an outreach email for Acme'"
        if is_en
        else "Fiyatı sor, bir rakibi sor ya da 'Acme için outreach emaili yaz' de"
    )
    prompt = st.chat_input(placeholder)
    if not prompt:
        return

    prompt = prompt.strip()
    if not prompt:
        st.warning("Please type a question." if is_en else "Lütfen bir soru yaz.")
        return
    if len(prompt) > MAX_CHAT_CHARS:
        st.warning(
            f"Message is too long (max {MAX_CHAT_CHARS} characters). Please shorten it."
            if is_en
            else f"Mesaj çok uzun (en fazla {MAX_CHAT_CHARS} karakter). Lütfen kısalt."
        )
        return

    st.session_state["chat_history"].append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        spinner_text = "Thinking..." if is_en else "Düşünüyor..."
        with st.spinner(spinner_text):
            try:
                spec = route_chat_message(prompt, lang)
            except Exception as exc:
                logger.exception("chat routing failed")
                spec = {"answer": f"Something went wrong: {exc}", "sources": [], "meta": "error"}
        st.markdown(spec["answer"])
        if spec.get("meta"):
            st.caption(spec["meta"])
        for source in spec.get("sources", []):
            st.caption(source)

    st.session_state["chat_history"].append(
        {
            "role": "assistant",
            "content": spec["answer"],
            "sources": spec.get("sources", []),
            "meta": spec.get("meta", ""),
        }
    )


def render_next_modules(lang: str) -> None:
    is_en = lang == "en"
    section_title = "Next Modules" if is_en else "Sonraki Modüller"
    rag_text = (
        "Grounded answers from documents with LangChain + ChromaDB."
        if is_en
        else "LangChain + ChromaDB ile dokümanlardan kaynaklı cevap üretme."
    )
    competitor_text = (
        "Summarizing public web information with Tavily or SerpAPI."
        if is_en
        else "Tavily veya SerpAPI ile public web bilgisini özetleme."
    )
    ragas_text = (
        "Measuring faithfulness, context precision, and answer relevancy."
        if is_en
        else "Faithfulness, context precision ve answer relevancy ölçümü."
    )

    st.markdown(f'<div class="bp-section-title">{section_title}</div>', unsafe_allow_html=True)
    c1, c2, c3 = st.columns(3)
    c1.markdown(
        f"""
        <div class="bp-card">
            <h3>RAG Q&A</h3>
            <p class="bp-muted">{rag_text}</p>
        </div>
        """,
        unsafe_allow_html=True,
    )
    c2.markdown(
        f"""
        <div class="bp-card">
            <h3>Competitor Intelligence</h3>
            <p class="bp-muted">{competitor_text}</p>
        </div>
        """,
        unsafe_allow_html=True,
    )
    c3.markdown(
        f"""
        <div class="bp-card">
            <h3>RAGAS Evaluation</h3>
            <p class="bp-muted">{ragas_text}</p>
        </div>
        """,
        unsafe_allow_html=True,
    )


@st.cache_resource(show_spinner=False)
def ensure_rag_index() -> int:
    """Build the ChromaDB index on first run if it is empty.

    On fresh deployments (Hugging Face Spaces / Render) the ``chroma_db/``
    folder is not committed, so the index is rebuilt once from the committed
    company corpus. Cached so it runs only once per container.
    """
    try:
        count = get_chroma_collection(reset=False).count()
        if count == 0:
            count = build_index(reset=True)
        return count
    except Exception:
        return 0


def main() -> None:
    inject_styles()
    lang = render_language_selector()
    is_en = lang == "en"
    render_header(lang)

    ensure_rag_index()

    if not MODEL_PATH.exists():
        st.error(
            "Lead scoring model was not found. Run `.venv\\Scripts\\python src\\lead_scoring_baseline.py` first."
            if is_en
            else "Lead scoring modeli bulunamadı. Önce `.venv\\Scripts\\python src\\lead_scoring_baseline.py` çalıştırılmalı."
        )
        st.stop()

    tabs = (
        ["Chatbot", "Dashboard", "Lead Qualification", "RAG Q&A", "Outreach Preview", "Competitor Intelligence", "Roadmap"]
        if is_en
        else ["Chatbot", "Dashboard", "Lead Qualification", "RAG Q&A", "Outreach Preview", "Rakip Analizi", "Yol Haritası"]
    )
    chatbot_tab, dashboard_tab, lead_tab, docs_tab, outreach_tab, competitor_tab, roadmap_tab = st.tabs(tabs)

    with chatbot_tab:
        render_chatbot(lang)
    with dashboard_tab:
        render_dashboard(lang)
    with lead_tab:
        render_lead_qualification(lang)
        render_crm_batch_results(lang)
    with docs_tab:
        render_rag_workspace(lang)
    with outreach_tab:
        render_outreach_preview(lang)
    with competitor_tab:
        render_competitor_intelligence(lang)
    with roadmap_tab:
        render_next_modules(lang)


if __name__ == "__main__":
    main()
