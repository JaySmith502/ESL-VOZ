import uuid
from datetime import datetime, timedelta, timezone

from sqlmodel import Session, select

from app.models import Attempt, Lesson, MasteryCell, RecommendationTrace, StudentProfile

BANDS = ["A1.1", "A1.2", "A2.1", "A2.2", "B1.1", "B1.2", "B2"]


def _next_band(band: str) -> str | None:
    idx = BANDS.index(band)
    if idx < len(BANDS) - 1:
        return BANDS[idx + 1]
    return None


def _previous_band(band: str) -> str | None:
    idx = BANDS.index(band)
    if idx > 0:
        return BANDS[idx - 1]
    return None


def _completed_lesson_ids(db: Session, student_id: uuid.UUID) -> set[str]:
    """Return lesson_ids that have at least one attempt (M1 simplification)."""
    attempts = db.exec(
        select(Attempt.lesson_id).where(Attempt.student_id == student_id).where(Attempt.lesson_id != None)  # noqa: E711
    ).all()
    return {a for a in attempts if a}


def _lesson_candidates(db: Session, bands: list[str], exclude_ids: set[str]) -> list[Lesson]:
    return db.exec(
        select(Lesson)
        .where(Lesson.cefr_band.in_(bands))
        .where(Lesson.domain == "Survival")
        .where(Lesson.origin != "generated_uncurated")
        .where(Lesson.lesson_id.notin_(exclude_ids) if exclude_ids else True)
        .order_by(Lesson.cefr_band, Lesson.estimated_minutes)
    ).all()


def _cell_evidence(cells: list[MasteryCell]) -> list[dict]:
    return [
        {
            "mode": c.mode,
            "cefr_band": c.cefr_band,
            "domain": c.domain,
            "mastery_score": c.mastery_score,
            "confidence": c.confidence,
        }
        for c in cells
    ]


def _build_fallback(db: Session, student: StudentProfile, completed: set[str]) -> tuple[Lesson | None, list[dict]]:
    all_lessons = db.exec(
        select(Lesson)
        .where(Lesson.domain == "Survival")
        .where(Lesson.origin != "generated_uncurated")
        .order_by(Lesson.cefr_band)
    ).all()
    candidates = [
        {"lesson_id": l.lesson_id, "title_en": l.title_en, "cefr_band": l.cefr_band}
        for l in all_lessons
    ]
    for lesson in all_lessons:
        if lesson.lesson_id not in completed:
            return lesson, candidates
    return (all_lessons[0] if all_lessons else None), candidates


def recommend_next_activity(db: Session, student: StudentProfile) -> dict:
    completed = _completed_lesson_ids(db, student.id)
    current_band = student.cefr_band or "A1.1"
    cells = db.exec(select(MasteryCell).where(MasteryCell.student_id == student.id)).all()

    # Bucket 1: overdue SRS reviews (placeholder for M1 — returns empty until SRS is wired)
    # Bucket 2: active learning path — next uncompleted lesson at current band
    active_candidates = _lesson_candidates(db, [current_band], completed)
    if active_candidates:
        selected = active_candidates[0]
        rationale = (
            f"Active learning path: learner's current band is {current_band} in Survival. "
            f"Selected '{selected.title_en}' as the next uncompleted lesson."
        )
        trace = RecommendationTrace(
            student_id=student.id,
            bucket_fired="active_learning_path",
            rationale=rationale,
            candidates_considered=[
                {"lesson_id": l.lesson_id, "title_en": l.title_en, "cefr_band": l.cefr_band}
                for l in active_candidates
            ],
            selected_activity={
                "type": "lesson",
                "lesson_id": selected.lesson_id,
                "title_en": selected.title_en,
                "title_es": selected.title_es,
            },
            graph_evidence=_cell_evidence(cells),
        )
        db.add(trace)
        db.commit()
        return {
            "bucket_fired": trace.bucket_fired,
            "rationale": trace.rationale,
            "graph_evidence": trace.graph_evidence,
            "activity": trace.selected_activity,
        }

    # Bucket 3: mastery consolidation — cells in [0.5, 0.85) needing one more push
    consolidation_cells = [c for c in cells if 0.5 <= c.mastery_score < 0.85]
    if consolidation_cells:
        target_modes = list({c.mode for c in consolidation_cells})
        target_bands = list({c.cefr_band for c in consolidation_cells})
        consolidation_lessons = _lesson_candidates(db, target_bands, completed)
        consolidation_lessons = [l for l in consolidation_lessons if any(m in l.modes for m in target_modes)]
        if consolidation_lessons:
            selected = consolidation_lessons[0]
            rationale = (
                f"Mastery consolidation: {len(consolidation_cells)} cell(s) are between 0.5–0.85. "
                f"Selected '{selected.title_en}' to strengthen {selected.modes}."
            )
            trace = RecommendationTrace(
                student_id=student.id,
                bucket_fired="mastery_consolidation",
                rationale=rationale,
                candidates_considered=[
                    {"lesson_id": l.lesson_id, "title_en": l.title_en, "cefr_band": l.cefr_band}
                    for l in consolidation_lessons
                ],
                selected_activity={
                    "type": "lesson",
                    "lesson_id": selected.lesson_id,
                    "title_en": selected.title_en,
                    "title_es": selected.title_es,
                },
                graph_evidence=_cell_evidence(consolidation_cells),
            )
            db.add(trace)
            db.commit()
            return {
                "bucket_fired": trace.bucket_fired,
                "rationale": trace.rationale,
                "graph_evidence": trace.graph_evidence,
                "activity": trace.selected_activity,
            }

    # Bucket 4: stretch challenge — one band up if confidence is high
    next_band = _next_band(current_band)
    high_confidence_cells = [c for c in cells if c.confidence >= 0.7]
    if next_band and high_confidence_cells:
        stretch_candidates = _lesson_candidates(db, [next_band], completed)
        if stretch_candidates:
            selected = stretch_candidates[0]
            rationale = (
                f"Stretch challenge: learner shows high confidence in {len(high_confidence_cells)} cell(s); "
                f"offering a {next_band} lesson."
            )
            trace = RecommendationTrace(
                student_id=student.id,
                bucket_fired="stretch_challenge",
                rationale=rationale,
                candidates_considered=[
                    {"lesson_id": l.lesson_id, "title_en": l.title_en, "cefr_band": l.cefr_band}
                    for l in stretch_candidates
                ],
                selected_activity={
                    "type": "lesson",
                    "lesson_id": selected.lesson_id,
                    "title_en": selected.title_en,
                    "title_es": selected.title_es,
                },
                graph_evidence=_cell_evidence(high_confidence_cells),
            )
            db.add(trace)
            db.commit()
            return {
                "bucket_fired": trace.bucket_fired,
                "rationale": trace.rationale,
                "graph_evidence": trace.graph_evidence,
                "activity": trace.selected_activity,
            }

    # Fallback: any available lesson at current or lower band
    selected, candidates = _build_fallback(db, student, completed)
    rationale = "No active/consolidation/stretch candidate found; defaulting to the next available Survival lesson."
    trace = RecommendationTrace(
        student_id=student.id,
        bucket_fired="exploration",
        rationale=rationale,
        candidates_considered=candidates,
        selected_activity={
            "type": "lesson",
            "lesson_id": selected.lesson_id if selected else None,
            "title_en": selected.title_en if selected else None,
            "title_es": selected.title_es if selected else None,
        },
        graph_evidence=_cell_evidence(cells),
    )
    db.add(trace)
    db.commit()
    return {
        "bucket_fired": trace.bucket_fired,
        "rationale": trace.rationale,
        "graph_evidence": trace.graph_evidence,
        "activity": trace.selected_activity,
    }
