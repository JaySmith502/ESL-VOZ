from pathlib import Path
from typing import Any

import yaml
from sqlmodel import Session, select

from app.models import Lesson, LessonStep

LESSONS_DIR = Path(__file__).parent.parent.parent.parent / "content" / "lessons"


def ingest_lessons(db: Session) -> dict[str, Any]:
    ingested = []
    skipped = []
    errors = []

    for path in LESSONS_DIR.glob("*.yaml"):
        try:
            with open(path, encoding="utf-8") as f:
                data = yaml.safe_load(f)
        except Exception as e:
            errors.append({"path": str(path), "error": str(e)})
            continue

        if not isinstance(data, dict):
            skipped.append(str(path))
            continue

        lesson_id = data["lesson_id"]
        existing = db.exec(select(Lesson).where(Lesson.lesson_id == lesson_id)).first()
        if existing:
            # Remove old steps
            for step in existing.steps:
                db.delete(step)
            lesson = existing
        else:
            lesson = Lesson(lesson_id=lesson_id)
            db.add(lesson)

        lesson.title_en = data["title"]["en"]
        lesson.title_es = data["title"]["es"]
        lesson.template_pattern = data["template_pattern"]
        lesson.cefr_band = data["cefr_band"]
        lesson.domain = data["domain"]
        lesson.modes = data["modes"]
        lesson.components = data["components"]
        lesson.estimated_minutes = data["estimated_minutes"]
        lesson.yaml_path = str(path)
        lesson.license = data["license"]
        lesson.origin = data["origin"]
        lesson.target_descriptors = data.get("target_descriptors", [])
        lesson.prerequisites = data.get("prerequisites", {})

        db.flush()  # get lesson.id if new

        for idx, step_data in enumerate(data.get("steps", [])):
            step = LessonStep(
                lesson_id=lesson.lesson_id,
                step_idx=idx,
                step_type=step_data["step_type"],
                config=step_data.get("config", {}),
            )
            db.add(step)

        db.commit()
        ingested.append(lesson_id)

    return {"ingested": ingested, "skipped": skipped, "errors": errors}
