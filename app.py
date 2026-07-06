from __future__ import annotations

from pathlib import Path
import re

import pandas as pd
import streamlit as st

from src.lead_scoring_predictor import score_lead


ROOT_DIR = Path(__file__).resolve().parent
COMPANY_DOCS_DIR = ROOT_DIR / "data" / "company_docs"
MODEL_PATH = ROOT_DIR / "models" / "lead_scoring_logreg.joblib"
BASELINE_REPORT_PATH = ROOT_DIR / "reports" / "lead_scoring_baseline.md"
PROCESSED_DATA_PATH = ROOT_DIR / "data" / "lead_scoring" / "processed" / "lead_scoring_cleaned.csv"

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
def load_company_documents() -> list[dict[str, str]]:
    docs: list[dict[str, str]] = []
    if not COMPANY_DOCS_DIR.exists():
        return docs

    for path in sorted(COMPANY_DOCS_DIR.glob("*.md")):
        text = path.read_text(encoding="utf-8")
        docs.append(
            {
                "name": path.stem.replace("_", " ").title(),
                "file": path.name,
                "type": extract_value(text, "Document type") or "document",
                "source_id": extract_value(text, "Source ID") or path.stem,
                "text": text,
            }
        )
    return docs


def extract_value(text: str, key: str) -> str | None:
    match = re.search(rf"^{re.escape(key)}:\s*(.+)$", text, flags=re.MULTILINE)
    return match.group(1).strip() if match else None


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
    if lang == "tr":
        return result["explanation"]

    direction = "increased" if result["rule_adjustment"] >= 0 else "decreased"
    translated_reasons = [display_reason(reason, "en") for reason in result["rule_reasons"]]
    return (
        f"The ML model produced a base score of {result['ml_score']}/100. "
        f"The rule-based layer {direction} the score by {abs(result['rule_adjustment'])} points. "
        f"The final score is {result['final_score']}/100. "
        f"{' '.join(translated_reasons[:3])}"
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
    docs = load_company_documents()

    section_title = "Project Status" if is_en else "Proje Durumu"
    st.markdown(f'<div class="bp-section-title">{section_title}</div>', unsafe_allow_html=True)

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Clean Dataset" if is_en else "Temiz Dataset", f"{len(df):,}" if not df.empty else ("Not ready" if is_en else "Hazır değil"))
    col2.metric("Model", "Logistic Regression", "Baseline")
    col3.metric("ROC-AUC", "0.8703")
    col4.metric("RAG Documents" if is_en else "RAG Dokümanı", str(len(docs)))

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

    with st.form("lead_form"):
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
        lead_data = {
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
        st.session_state["last_lead"] = lead_data
        st.session_state["last_score"] = score_lead(lead_data)

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
            st.markdown("#### Rule Signals" if is_en else "#### Kural Sinyalleri")
            for reason in result["rule_reasons"]:
                st.write(f"- {display_reason(reason, lang)}")
    else:
        st.info(
            "Enter lead information and score it to see the result here."
            if is_en
            else "Lead bilgilerini girip skorlama yaptığında sonuç burada görünecek."
        )


def render_document_workspace(lang: str) -> None:
    is_en = lang == "en"
    st.markdown('<div class="bp-section-title">Company Documents Workspace</div>', unsafe_allow_html=True)
    st.caption(
        "This is not the full RAG pipeline yet; it is a Week 1 workspace for reviewing and searching sample company documents."
        if is_en
        else "Bu alan full RAG pipeline değildir; Week 1 için örnek şirket dokümanlarını inceleme ve arama ekranıdır."
    )

    docs = load_company_documents()
    query = st.text_input(
        "Search documents" if is_en else "Dokümanlarda ara",
        placeholder="Example: pricing, outreach, competitor, lead scoring" if is_en else "Örnek: pricing, outreach, competitor, lead scoring",
    )

    if not docs:
        st.warning("Company documents not found." if is_en else "Company document bulunamadı.")
        return

    if query:
        terms = [term.lower() for term in query.split() if term.strip()]
        ranked = []
        for doc in docs:
            text = doc["text"].lower()
            score = sum(text.count(term) for term in terms)
            if score > 0:
                ranked.append((score, doc))
        ranked.sort(key=lambda item: item[0], reverse=True)
        visible_docs = [doc for _, doc in ranked] or docs
    else:
        visible_docs = docs

    for doc in visible_docs:
        with st.expander(f"{doc['name']} | {doc['type']} | {doc['source_id']}"):
            st.markdown(doc["text"])
            st.caption(f"Source file: data/company_docs/{doc['file']}")


def render_outreach_preview(lang: str) -> None:
    is_en = lang == "en"
    st.markdown('<div class="bp-section-title">Outreach Draft Preview</div>', unsafe_allow_html=True)
    st.caption(
        "This is currently a template-based preview. Later, the LLM and retrieved context will generate agentic outreach."
        if is_en
        else "Bu şimdilik template tabanlı preview. İlerleyen adımda LLM ve retrieved context ile agentic outreach üretilecek."
    )

    company = st.text_input("Prospect Company", value="Northstar CRM Solutions")
    contact = st.text_input("Contact Name", value="Aarav")
    pain_point = st.text_input(
        "Observed Need",
        value="inbound lead response and sales team productivity" if is_en else "inbound lead response ve satış ekibi verimliliği",
    )

    score = st.session_state.get("last_score", {}).get("final_score", 78)
    raw_label = st.session_state.get("last_score", {}).get("label", "Yuksek Potansiyel")
    label = display_label(raw_label, lang)

    email = f"""Subject: Helping {company} prioritize inbound leads

Hi {contact},

I noticed that {company} may benefit from improving {pain_point}.
BizPilot AI can help your team answer product questions from company documents, qualify inbound leads, and draft personalized outreach from one workspace.

Based on the current qualification signals, this prospect is scored at {score}/100 ({label}).

Would you be open to a short conversation this week?

Best,
BizPilot AI Team"""

    linkedin = (
        f"Hi {contact}, I am working on BizPilot AI for digital business development. "
        f"It helps teams qualify leads, answer company-document questions, and draft outreach faster. "
        f"Thought it could be relevant for {company}'s {pain_point} workflow."
    )

    c1, c2 = st.columns(2, gap="large")
    with c1:
        st.markdown("#### Cold Email")
        st.code(email, language="text")
    with c2:
        st.markdown("#### LinkedIn Message")
        st.code(linkedin, language="text")


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


def main() -> None:
    inject_styles()
    lang = render_language_selector()
    is_en = lang == "en"
    render_header(lang)

    if not MODEL_PATH.exists():
        st.error(
            "Lead scoring model was not found. Run `.venv\\Scripts\\python src\\lead_scoring_baseline.py` first."
            if is_en
            else "Lead scoring modeli bulunamadı. Önce `.venv\\Scripts\\python src\\lead_scoring_baseline.py` çalıştırılmalı."
        )
        st.stop()

    tabs = (
        ["Dashboard", "Lead Qualification", "Company Docs", "Outreach Preview", "Roadmap"]
        if is_en
        else ["Dashboard", "Lead Qualification", "Company Docs", "Outreach Preview", "Yol Haritası"]
    )
    dashboard_tab, lead_tab, docs_tab, outreach_tab, roadmap_tab = st.tabs(tabs)

    with dashboard_tab:
        render_dashboard(lang)
    with lead_tab:
        render_lead_qualification(lang)
    with docs_tab:
        render_document_workspace(lang)
    with outreach_tab:
        render_outreach_preview(lang)
    with roadmap_tab:
        render_next_modules(lang)


if __name__ == "__main__":
    main()
