import json
import uuid
from pathlib import Path
from typing import Any

from sqlmodel import Session, select

from app.models import MasteryCell, StudentProfile

BANK_PATH = Path(__file__).parent.parent / "data" / "placement_bank.json"
BANDS = ["A1.1", "A1.2", "A2.1", "A2.2"]


def load_bank() -> dict[str, Any]:
    with open(BANK_PATH, encoding="utf-8") as f:
        return json.load(f)


def get_items_for_mode(bank: dict, mode: str) -> list[dict]:
    return [item for item in bank["items"] if item["mode"] == mode]


def next_band_index(current: str, correct: bool) -> int:
    idx = BANDS.index(current)
    if correct and idx < len(BANDS) - 1:
        return idx + 1
    if not correct and idx > 0:
        return idx - 1
    return idx


def get_placement_items() -> list[dict]:
    """Return sanitized placement items for the frontend (no answers)."""
    bank = load_bank()
    sanitized = []
    for item in bank["items"]:
        clean = {
            "id": item["id"],
            "mode": item["mode"],
            "band": item["band"],
            "prompt_en": item.get("prompt_en", ""),
            "prompt_es": item.get("prompt_es", ""),
        }
        if "options" in item:
            clean["options"] = item["options"]
        if "example" in item:
            clean["example"] = item["example"]
        sanitized.append(clean)
    return sanitized


def _score_response(item: dict, response: Any) -> tuple[bool, bool]:
    """Return (is_idk, is_correct)."""
    text = str(response).strip()
    if text == "__idk__" or text == "":
        return True, False
    if "answer" in item:
        return False, text.lower() == item["answer"].lower()
    # Speaking/writing: accept any non-empty response in this simplified slice
    return False, bool(text)


def run_placement(
    db: Session,
    student: StudentProfile,
    answers: dict[str, Any],
) -> dict[str, Any]:
    bank = load_bank()
    results = []
    final_bands = {}

    for mode in ["Listening", "Speaking", "Reading", "Writing"]:
        items = get_items_for_mode(bank, mode)
        # Sort by band order
        items.sort(key=lambda x: BANDS.index(x["band"]))
        current_band_idx = 0
        consecutive_failures = 0
        consecutive_idks = 0
        attempted = 0
        correct_count = 0

        for item in items:
            if attempted >= 6 or consecutive_failures >= 2 or consecutive_idks >= 2:
                break
            # Only use items near current band to keep adaptive
            item_idx = BANDS.index(item["band"])
            if abs(item_idx - current_band_idx) > 1:
                continue
            attempted += 1
            response = answers.get(item["id"], "")
            is_idk, is_correct = _score_response(item, response)

            if is_idk:
                consecutive_idks += 1
                consecutive_failures += 1
                current_band_idx = next_band_index(BANDS[current_band_idx], False)
            elif is_correct:
                correct_count += 1
                consecutive_failures = 0
                consecutive_idks = 0
                current_band_idx = next_band_index(BANDS[current_band_idx], True)
            else:
                consecutive_failures += 1
                consecutive_idks = 0
                current_band_idx = next_band_index(BANDS[current_band_idx], False)

            results.append({
                "item_id": item["id"],
                "is_idk": is_idk,
                "correct": is_correct,
                "response": response,
            })

        final_band = BANDS[max(0, current_band_idx)]
        final_bands[mode] = final_band

        # Write or update mastery cell
        cell = db.exec(
            select(MasteryCell).where(
                MasteryCell.student_id == student.id,
                MasteryCell.mode == mode,
                MasteryCell.cefr_band == final_band,
                MasteryCell.domain == "Survival",
            )
        ).first()
        if not cell:
            cell = MasteryCell(
                student_id=student.id,
                mode=mode,
                cefr_band=final_band,
                domain="Survival",
                mastery_score=0.7,
                confidence=0.6,
            )
            db.add(cell)
        else:
            cell.mastery_score = max(cell.mastery_score, 0.7)
            cell.confidence = max(cell.confidence, 0.6)

    # Set the student's overall starting band conservatively (lowest mode band)
    overall_band_index = min(BANDS.index(b) for b in final_bands.values())
    student.cefr_band = BANDS[overall_band_index]

    db.add(student)
    db.commit()
    return {
        "estimated_bands": final_bands,
        "overall_band": student.cefr_band,
        "results": results,
    }
