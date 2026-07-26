"""Verify the optional OpenAI integration without involving employee records."""

import sys

from app.core.config import settings
from app.services.workforce_insights import generate_insights


def main() -> int:
    if not settings.ENABLE_EXTERNAL_AI:
        print("SKIP ENABLE_EXTERNAL_AI is false")
        return 0
    if not settings.OPENAI_API_KEY:
        print("FAIL OPENAI_API_KEY is not configured", file=sys.stderr)
        return 1

    insights, source = generate_insights(
        {
            "total_employees": 10,
            "inactive_employees": 1,
            "attendance_records": 100,
            "present_records": 92,
        },
        "integration verification",
    )
    if source != "ai":
        print("FAIL OpenAI request fell back to local rules", file=sys.stderr)
        return 1
    print(f"PASS OpenAI integration returned {len(insights)} insights")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
