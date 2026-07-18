from __future__ import annotations

import json
import os
import socket
import time
import urllib.error
import urllib.request
from pathlib import Path
from typing import Any


ROOT_DIR = Path(__file__).resolve().parents[1]
ENV_PATH = ROOT_DIR / ".env"
OPENAI_RESPONSES_URL = "https://api.openai.com/v1/responses"
DEFAULT_OPENAI_MODEL = "gpt-5.4"
DEFAULT_LLM_TIMEOUT_SECONDS = 90
DEFAULT_LLM_MAX_TOKENS = 420
DEFAULT_LLM_RETRY_ATTEMPTS = 2
DEFAULT_LLM_RETRY_DELAY_SECONDS = 5.0
FAST_FALLBACK_TIMEOUT_SECONDS = 12
FAST_FALLBACK_RETRY_ATTEMPTS = 0
RETRYABLE_HTTP_STATUS_CODES = {429, 500, 502, 503, 504}
PROXY_ENV_KEYS = {
    "http": ("HTTP_PROXY", "http_proxy"),
    "https": ("HTTPS_PROXY", "https_proxy"),
}
DEFAULT_CHAT_SYSTEM_PROMPT = (
    "You explain machine-learning lead scores for sales teams. "
    "Return only the final answer. Do not reveal analysis or hidden reasoning."
)

LABEL_TRANSLATIONS = {
    "Yuksek Potansiyel": "High Potential",
    "Orta Potansiyel": "Medium Potential",
    "Dusuk Potansiyel": "Low Potential",
}

REASON_TRANSLATIONS = {
    "Email izni var, bu outreach icin olumlu bir sinyal.": "Email outreach is allowed, which is a positive sales signal.",
    "Email izni yok, bu satis iletisimini zorlastirabilir.": "Email outreach is not allowed, which may make sales follow-up harder.",
    "Lead form doldurarak gelmis, bu daha yuksek niyet gosterebilir.": "The lead came through a form submission, which suggests stronger intent.",
    "Calisan profesyonel profili donusum icin olumlu gorunuyor.": "The working professional profile is a positive conversion signal.",
    "Meslek bilgisi donusum olasiligini biraz dusuren grupta.": "The occupation category slightly weakens the conversion signal.",
    "Web sitesinde uzun sure gecirmis.": "The lead spent a long time on the website.",
    "Web sitesinde cok az sure gecirmis.": "The lead spent very little time on the website.",
    "Birden fazla ziyaret yapmis.": "The lead visited the website multiple times.",
    "Ziyaret sayisi dusuk.": "The visit count is low.",
    "Sayfa goruntuleme ortalamasi iyi.": "The average page views per visit is strong.",
    "Kural tabanli ek sinyal bulunmadi; skor agirlikli olarak ML modelinden geldi.": "No strong rule-based signal was found, so the score mainly follows the ML model.",
}


def generate_lead_score_explanation(lead_data: dict[str, Any], score_result: dict[str, Any]) -> dict[str, Any]:
    load_env_file()
    api_key = os.getenv("OPENAI_API_KEY", "").strip()
    model = os.getenv("OPENAI_MODEL", DEFAULT_OPENAI_MODEL).strip()

    if not api_key:
        return {
            "explanation": build_template_explanation(lead_data, score_result),
            "llm_explanation_used": False,
            "explanation_provider": "template_fallback",
            "explanation_model": "",
            "llm_error": "OPENAI_API_KEY is not configured.",
        }

    try:
        explanation = call_openai_responses(
            api_key=api_key,
            model=model,
            prompt=build_prompt(lead_data, score_result),
            system_prompt=DEFAULT_CHAT_SYSTEM_PROMPT,
            max_tokens=get_llm_max_tokens(),
            clean_response=True,
        )
        return {
            "explanation": explanation,
            "llm_explanation_used": True,
            "explanation_provider": "openai",
            "explanation_model": model,
        }
    except RuntimeError as exc:
        return {
            "explanation": build_template_explanation(lead_data, score_result),
            "llm_explanation_used": False,
            "explanation_provider": "template_fallback",
            "explanation_model": "",
            "llm_error": str(exc),
        }


def call_configured_llm(
    prompt: str,
    system_prompt: str,
    *,
    max_tokens: int | None = None,
    temperature: float = 0.2,
    clean_response: bool = False,
) -> dict[str, Any]:
    """Call the configured OpenAI model for BizPilot modules."""
    del temperature  # GPT-5.4 is used with default model sampling settings.
    load_env_file()
    api_key = os.getenv("OPENAI_API_KEY", "").strip()
    model = os.getenv("OPENAI_MODEL", DEFAULT_OPENAI_MODEL).strip()

    if not api_key:
        return {
            "text": "",
            "llm_used": False,
            "provider": "openai",
            "model": model,
            "error": "OPENAI_API_KEY is not configured.",
        }

    try:
        text = call_openai_responses(
            api_key=api_key,
            model=model,
            prompt=prompt,
            system_prompt=system_prompt,
            max_tokens=max_tokens or get_llm_max_tokens(),
            clean_response=clean_response,
        )
        return {"text": text, "llm_used": True, "provider": "openai", "model": model, "error": ""}
    except RuntimeError as exc:
        return {"text": "", "llm_used": False, "provider": "openai", "model": model, "error": str(exc)}


def load_env_file(env_path: Path = ENV_PATH) -> None:
    if not env_path.exists():
        return

    for raw_line in env_path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue

        key, value = line.split("=", 1)
        key = key.strip()
        value = value.strip().strip('"').strip("'")
        if key:
            os.environ[key] = value


def build_prompt(lead_data: dict[str, Any], score_result: dict[str, Any]) -> str:
    payload = {
        "lead_profile": {
            "lead_origin": lead_data.get("Lead Origin"),
            "lead_source": lead_data.get("Lead Source"),
            "do_not_email": lead_data.get("Do Not Email"),
            "occupation": lead_data.get("What is your current occupation"),
            "total_visits": lead_data.get("TotalVisits"),
            "total_time_spent_on_website": lead_data.get("Total Time Spent on Website"),
            "page_views_per_visit": lead_data.get("Page Views Per Visit"),
            "last_activity": lead_data.get("Last Activity"),
            "last_notable_activity": lead_data.get("Last Notable Activity"),
        },
        "score_breakdown": {
            "ml_probability": score_result.get("ml_probability"),
            "ml_score": score_result.get("ml_score"),
            "rule_adjustment": score_result.get("rule_adjustment"),
            "final_score": score_result.get("final_score"),
            "label": score_result.get("label"),
            "rule_reasons": score_result.get("rule_reasons", []),
        },
    }

    return (
        "You are BizPilot AI's lead qualification explainer for a digital business development team.\n"
        "Explain the lead score in natural language using only the provided JSON.\n"
        "Do not invent missing CRM data.\n"
        "Return only the final explanation text. Do not show analysis, hidden reasoning, JSON parsing, headings, or bullet lists.\n"
        "Do not mention the user, prompt, JSON, or that you are analyzing the data.\n"
        "Write one concise sales-focused paragraph with 3 to 4 sentences.\n"
        "Mention the ML base score, rule-based adjustment, final priority, top reasons, and recommended next action.\n"
        "Use plain ASCII punctuation.\n\n"
        f"Lead scoring JSON:\n{json.dumps(payload, indent=2, ensure_ascii=False)}"
    )


def build_template_explanation(lead_data: dict[str, Any], score_result: dict[str, Any]) -> str:
    del lead_data
    final_score = score_result["final_score"]
    label = LABEL_TRANSLATIONS.get(score_result["label"], score_result["label"])
    ml_score = score_result["ml_score"]
    rule_adjustment = score_result["rule_adjustment"]
    reasons = score_result.get("rule_reasons", [])

    direction = "increased" if rule_adjustment >= 0 else "decreased"
    reason_text = " ".join(translate_reason(reason) for reason in reasons[:3])
    if not reason_text:
        reason_text = "No strong rule-based signal was found, so the decision mainly follows the ML model."

    next_action = "prioritize immediate outreach" if final_score >= 75 else "nurture and monitor engagement"
    if final_score < 50:
        next_action = "keep as low-priority until stronger buying intent appears"

    return (
        f"The ML model produced a base score of {ml_score}/100. "
        f"The rule-based layer {direction} the score by {abs(rule_adjustment)} points, "
        f"resulting in a final score of {final_score}/100 ({label}). "
        f"{reason_text} Recommended action: {next_action}."
    )


def translate_reason(reason: str) -> str:
    return REASON_TRANSLATIONS.get(reason, reason)


def call_openai_responses(
    api_key: str,
    model: str,
    prompt: str,
    system_prompt: str,
    max_tokens: int,
    clean_response: bool,
) -> str:
    body = {
        "model": model,
        "input": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": prompt},
        ],
        "max_output_tokens": max_tokens,
    }

    request_data = json.dumps(body).encode("utf-8")
    timeout_seconds = get_llm_timeout_seconds()
    retry_attempts = get_llm_retry_attempts()

    for attempt in range(retry_attempts + 1):
        request = urllib.request.Request(
            OPENAI_RESPONSES_URL,
            data=request_data,
            headers={
                "Authorization": f"Bearer {api_key}",
                "Accept": "application/json",
                "Content-Type": "application/json",
                "User-Agent": "BizPilotAI/1.0",
            },
            method="POST",
        )

        try:
            opener = build_url_opener()
            with opener.open(request, timeout=timeout_seconds) as response:
                response_data = json.loads(response.read().decode("utf-8"))
            text = parse_openai_responses_response(response_data)
            if clean_response:
                return clean_llm_explanation(text, "OpenAI")
            return clean_plain_llm_text(text, "OpenAI")
        except urllib.error.HTTPError as exc:
            detail = exc.read().decode("utf-8", errors="replace")
            message = summarize_http_error("OpenAI", exc.code, detail)
            if exc.code in RETRYABLE_HTTP_STATUS_CODES and attempt < retry_attempts:
                sleep_before_retry(attempt)
                continue
            raise RuntimeError(message) from exc
        except (TimeoutError, socket.timeout) as exc:
            message = f"OpenAI API request timed out after {timeout_seconds} seconds."
            if attempt < retry_attempts:
                sleep_before_retry(attempt)
                continue
            raise RuntimeError(message) from exc
        except urllib.error.URLError as exc:
            message = f"OpenAI API request failed: {exc.reason}"
            if attempt < retry_attempts:
                sleep_before_retry(attempt)
                continue
            raise RuntimeError(message) from exc

    raise RuntimeError("OpenAI API failed after retry attempts.")


def build_url_opener() -> urllib.request.OpenerDirector:
    proxies = get_configured_proxies()
    if proxies:
        return urllib.request.build_opener(urllib.request.ProxyHandler(proxies))
    return urllib.request.build_opener()


def get_configured_proxies() -> dict[str, str]:
    proxies: dict[str, str] = {}
    for scheme, keys in PROXY_ENV_KEYS.items():
        for key in keys:
            value = os.getenv(key, "").strip()
            if value:
                proxies[scheme] = value
                break
    return proxies


def parse_openai_responses_response(response_data: dict[str, Any]) -> str:
    output_text = response_data.get("output_text")
    if isinstance(output_text, str) and output_text.strip():
        return output_text.strip()

    parts: list[str] = []
    output = response_data.get("output", [])
    if isinstance(output, list):
        for item in output:
            if not isinstance(item, dict):
                continue
            content = item.get("content", [])
            if not isinstance(content, list):
                continue
            for content_item in content:
                if not isinstance(content_item, dict):
                    continue
                text = content_item.get("text")
                if isinstance(text, str) and text.strip():
                    parts.append(text.strip())

    if parts:
        return "\n".join(parts)

    raise RuntimeError(f"OpenAI API returned an empty response: {response_data}")


def clean_llm_explanation(explanation: str, provider_name: str) -> str:
    text = explanation.replace("\r\n", "\n").strip()
    lines = [line.strip() for line in text.splitlines()]
    while lines and (not lines[0] or lines[0].startswith("#")):
        lines.pop(0)
    text = " ".join(line for line in lines if line).strip()

    bad_markers = [
        "the user wants me",
        "let me analyze",
        "let me break down",
        "key points from the json",
        "lead profile info",
        "based on the provided json",
        "i need to",
        "i should",
    ]
    lower_text = text.lower()
    if any(marker in lower_text for marker in bad_markers):
        raise RuntimeError(f"{provider_name} API returned analysis text instead of a final explanation.")

    if len(text.split()) < 25:
        raise RuntimeError(f"{provider_name} API returned a too-short explanation: {text}")

    return text


def clean_plain_llm_text(text: str, provider_name: str) -> str:
    cleaned = text.replace("\r\n", "\n").strip()
    if not cleaned:
        raise RuntimeError(f"{provider_name} API returned an empty response.")
    return cleaned


def summarize_http_error(provider_name: str, status_code: int, detail: str) -> str:
    retry_note = " The request was retried, but the provider still failed." if status_code in RETRYABLE_HTTP_STATUS_CODES else ""

    try:
        payload = json.loads(detail)
        error = payload.get("error")
        title = ""
        message = ""
        if isinstance(error, dict):
            title = str(error.get("type") or error.get("code") or "")
            message = str(error.get("message") or "")
        else:
            title = str(payload.get("title") or payload.get("error") or "")
            message = str(payload.get("detail") or payload.get("message") or "")

        parts = [f"{provider_name} API returned HTTP {status_code}"]
        if title:
            parts.append(title)
        if message:
            parts.append(message)
        return ": ".join(parts) + retry_note
    except json.JSONDecodeError:
        compact_detail = " ".join(detail.split())
        if len(compact_detail) > 300:
            compact_detail = compact_detail[:300] + "..."
        return f"{provider_name} API returned HTTP {status_code}: {compact_detail}{retry_note}"


def sleep_before_retry(attempt: int) -> None:
    delay_seconds = get_llm_retry_delay_seconds() * (attempt + 1)
    time.sleep(delay_seconds)


def get_llm_timeout_seconds() -> int:
    raw_value = os.getenv("LLM_TIMEOUT_SECONDS", "").strip()
    if not raw_value:
        timeout_seconds = DEFAULT_LLM_TIMEOUT_SECONDS
    else:
        try:
            timeout_seconds = int(raw_value)
        except ValueError:
            timeout_seconds = DEFAULT_LLM_TIMEOUT_SECONDS

    if os.getenv("BIZPILOT_FAST_LLM_FALLBACK", "").strip() == "1":
        return max(5, min(timeout_seconds, FAST_FALLBACK_TIMEOUT_SECONDS))

    return max(10, timeout_seconds)


def get_llm_max_tokens() -> int:
    raw_value = os.getenv("LLM_MAX_TOKENS", "").strip()
    if not raw_value:
        return DEFAULT_LLM_MAX_TOKENS
    try:
        max_tokens = int(raw_value)
    except ValueError:
        return DEFAULT_LLM_MAX_TOKENS
    return max(80, max_tokens)


def get_llm_retry_attempts() -> int:
    raw_value = os.getenv("LLM_RETRY_ATTEMPTS", "").strip()
    if not raw_value:
        retry_attempts = DEFAULT_LLM_RETRY_ATTEMPTS
    else:
        try:
            retry_attempts = int(raw_value)
        except ValueError:
            retry_attempts = DEFAULT_LLM_RETRY_ATTEMPTS

    if os.getenv("BIZPILOT_FAST_LLM_FALLBACK", "").strip() == "1":
        return min(max(0, retry_attempts), FAST_FALLBACK_RETRY_ATTEMPTS)

    return max(0, min(5, retry_attempts))


def get_llm_retry_delay_seconds() -> float:
    raw_value = os.getenv("LLM_RETRY_DELAY_SECONDS", "").strip()
    if not raw_value:
        return DEFAULT_LLM_RETRY_DELAY_SECONDS
    try:
        retry_delay = float(raw_value)
    except ValueError:
        return DEFAULT_LLM_RETRY_DELAY_SECONDS
    return max(0.5, min(60.0, retry_delay))
