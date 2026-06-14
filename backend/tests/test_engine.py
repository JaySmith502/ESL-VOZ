import uuid

import pytest
from sqlmodel import Session, SQLModel, create_engine, select
from sqlmodel.pool import StaticPool

from app.models import Lesson, MasteryCell, StudentProfile, User, UserRole
from app.services.auth import create_or_get_user
from app.services.engine import recommend_next_activity
from app.services.mastery import update_mastery_from_attempt
from app.services.placement import run_placement


@pytest.fixture(name="db")
def db_fixture():
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    SQLModel.metadata.create_all(engine)
    with Session(engine) as session:
        yield session


@pytest.fixture(name="student")
def student_fixture(db: Session):
    user = create_or_get_user(db, "engine@example.com")
    profile = StudentProfile(user_id=user.id, l1="es", cefr_band="A1.1")
    db.add(profile)
    db.commit()
    db.refresh(profile)
    return profile


def _make_lesson(db: Session, lesson_id: str, band: str = "A1.1") -> Lesson:
    lesson = Lesson(
        lesson_id=lesson_id,
        title_en=f"Lesson {lesson_id}",
        title_es=f"Lección {lesson_id}",
        template_pattern="PPP",
        cefr_band=band,
        domain="Survival",
        modes=["Speaking"],
        components=["Vocabulary"],
        estimated_minutes=10,
        yaml_path=f"content/lessons/{lesson_id}.yaml",
        origin="authored",
        license="cc-by-sa-4.0",
    )
    db.add(lesson)
    db.commit()
    return lesson


def test_placement_sets_overall_band_and_cells(db: Session, student: StudentProfile):
    answers = {
        "lis-a1.1-1": "hello",
        "lis-a1.2-1": "water",
        "spk-a1.1-1": "hello",
        "spk-a1.2-1": "I would like water, please.",
        "rdg-a1.1-1": "Ana",
        "rdg-a1.2-1": "next to the kitchen",
        "wrt-a1.1-1": "Maria",
        "wrt-a1.2-1": "I need help.",
    }
    result = run_placement(db, student, answers)
    assert "overall_band" in result
    assert student.cefr_band is not None
    cells = db.exec(select(MasteryCell).where(MasteryCell.student_id == student.id)).all()
    assert len(cells) == 4


def test_engine_recommends_active_learning_path(db: Session, student: StudentProfile):
    _make_lesson(db, "lesson_a")
    result = recommend_next_activity(db, student)
    assert result["bucket_fired"] == "active_learning_path"
    assert result["activity"]["lesson_id"] == "lesson_a"


def test_engine_falls_back_when_all_done(db: Session, student: StudentProfile):
    lesson = _make_lesson(db, "lesson_done")
    from app.models import Attempt
    attempt = Attempt(
        student_id=student.id,
        activity_type="lesson",
        lesson_id=lesson.lesson_id,
        step_id="step-1",
        mode="Speaking",
        cefr_band="A1.1",
        domain="Survival",
        score=0.9,
    )
    db.add(attempt)
    db.commit()
    result = recommend_next_activity(db, student)
    # With only one lesson and it completed, fallback should still return it
    assert result["activity"]["lesson_id"] == lesson.lesson_id


def test_mastery_update_is_monotone(db: Session, student: StudentProfile):
    from app.models import Attempt
    attempt = Attempt(
        student_id=student.id,
        activity_type="lesson",
        lesson_id="l1",
        step_id="s1",
        mode="Speaking",
        cefr_band="A1.1",
        domain="Survival",
        score=0.2,
    )
    cell = update_mastery_from_attempt(db, student, attempt)
    first_score = cell.mastery_score
    attempt2 = Attempt(
        student_id=student.id,
        activity_type="lesson",
        lesson_id="l1",
        step_id="s1",
        mode="Speaking",
        cefr_band="A1.1",
        domain="Survival",
        score=0.9,
    )
    cell2 = update_mastery_from_attempt(db, student, attempt2)
    assert cell2.mastery_score >= first_score
