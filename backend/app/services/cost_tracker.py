from uuid import UUID

from sqlmodel import Session

from app.models import CostEvent

COST_RATES = {
    "anthropic": {
        "claude-3-haiku": {"input_per_1m": 0.25, "output_per_1m": 1.25},
        "claude-3-sonnet": {"input_per_1m": 3.0, "output_per_1m": 15.0},
    },
    "openai": {
        "tts-1": {"per_1k_chars": 0.015},
        "whisper": {"per_minute": 0.006},
    },
    "deepgram": {
        "nova-2": {"per_hour": 0.43},
    },
}


def record_cost(
    db: Session,
    vendor: str,
    operation: str,
    cost_usd: float,
    student_id: UUID | None = None,
    meta: dict | None = None,
) -> CostEvent:
    event = CostEvent(
        vendor=vendor,
        operation=operation,
        cost_usd=cost_usd,
        student_id=student_id,
        meta=meta or {},
    )
    db.add(event)
    db.commit()
    db.refresh(event)
    return event


def estimate_llm_cost(vendor: str, model: str, input_tokens: int, output_tokens: int) -> float:
    rates = COST_RATES.get(vendor, {}).get(model, {})
    input_cost = input_tokens * rates.get("input_per_1m", 0) / 1_000_000
    output_cost = output_tokens * rates.get("output_per_1m", 0) / 1_000_000
    return round(input_cost + output_cost, 6)
