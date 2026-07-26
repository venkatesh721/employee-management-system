import json
from urllib import error, request

from app.core.config import settings


def fallback_insights(metrics: dict, focus: str) -> list[str]:
    total = max(metrics["total_employees"], 1)
    inactive_rate = metrics["inactive_employees"] / total
    attendance_rate = metrics["present_records"] / max(metrics["attendance_records"], 1)
    insights = [
        f"Active workforce rate is {(1 - inactive_rate) * 100:.1f}%.",
        f"Recorded attendance rate for the selected period is {attendance_rate * 100:.1f}%.",
    ]
    if inactive_rate > 0.15:
        insights.append(
            "Review inactive employee records and workforce capacity planning."
        )
    if attendance_rate < 0.85:
        insights.append(
            "Investigate attendance barriers and follow up with affected teams."
        )
    else:
        insights.append(
            "Attendance is healthy; continue monitoring late and absent patterns."
        )
    if focus:
        insights.append(f"Requested focus: {focus}")
    return insights


def generate_insights(metrics: dict, focus: str) -> tuple[list[str], str]:
    fallback = fallback_insights(metrics, focus)
    if not settings.ENABLE_EXTERNAL_AI or not settings.OPENAI_API_KEY:
        return fallback, "rules-based fallback"

    prompt = (
        "You are a workforce operations analyst. Return JSON with an 'insights' array "
        "containing 3 concise, actionable observations. Do not include sensitive personal "
        f"data. Metrics: {json.dumps(metrics)}. Business focus: {focus or 'general workforce health'}."
    )
    payload = json.dumps(
        {
            "model": settings.AI_MODEL,
            "messages": [{"role": "user", "content": prompt}],
            "response_format": {"type": "json_object"},
            "temperature": 0.2,
        }
    ).encode()
    api_request = request.Request(
        "https://api.openai.com/v1/chat/completions",
        data=payload,
        headers={
            "Authorization": f"Bearer {settings.OPENAI_API_KEY}",
            "Content-Type": "application/json",
        },
        method="POST",
    )
    try:
        with request.urlopen(api_request, timeout=15) as response:
            result = json.loads(response.read())
        content = json.loads(result["choices"][0]["message"]["content"])
        insights = content.get("insights")
        if not isinstance(insights, list) or not insights:
            raise ValueError("AI response did not contain insights")
        return [str(item)[:500] for item in insights[:5]], "ai"
    except (error.URLError, TimeoutError, KeyError, ValueError, json.JSONDecodeError):
        return fallback, "rules-based fallback"
