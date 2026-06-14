from datetime import datetime, timezone

from sqlmodel import Session, select

from app.models import Attempt, MasteryCell, StudentProfile

ALPHA = 0.3


def update_mastery_from_attempt(
    db: Session,
    student: StudentProfile,
    attempt: Attempt,
) -> MasteryCell | None:
    if not attempt.mode or not attempt.cefr_band or not attempt.domain:
        return None

    cell = db.exec(
        select(MasteryCell).where(
            MasteryCell.student_id == student.id,
            MasteryCell.mode == attempt.mode,
            MasteryCell.cefr_band == attempt.cefr_band,
            MasteryCell.domain == attempt.domain,
        )
    ).first()

    if not cell:
        cell = MasteryCell(
            student_id=student.id,
            mode=attempt.mode,
            cefr_band=attempt.cefr_band,
            domain=attempt.domain,
            mastery_score=0.0,
            confidence=0.5,
        )
        db.add(cell)

    # EWMA with monotone sticky rule
    new_score = ALPHA * attempt.score + (1 - ALPHA) * cell.mastery_score
    cell.mastery_score = max(cell.mastery_score, new_score)
    cell.confidence = min(1.0, cell.confidence + 0.05)
    cell.updated_at = datetime.now(timezone.utc)
    db.commit()
    db.refresh(cell)
    return cell
