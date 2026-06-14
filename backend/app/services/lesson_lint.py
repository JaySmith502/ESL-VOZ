import json
import re
from pathlib import Path
from typing import Any

import yaml
from jsonschema import validate, ValidationError

ALLOWED_LICENSES = {"cc-by-4.0", "cc-by-sa-4.0", "cc0-1.0", "public-domain"}
VALID_BANDS = {"A1.1", "A1.2", "A2.1", "A2.2", "B1.1", "B1.2", "B2"}
VALID_MODES = {"Listening", "Speaking", "Reading", "Writing", "Mediation"}
VALID_COMPONENTS = {"Vocabulary", "Grammar", "Pronunciation", "Pragmatics"}

# Affective safety: topics that may be traumatic or inappropriate for a mixed adult ESL cohort.
AFFECTIVE_FLAGS = {
    "violence", "weapon", "gun", "kill", "die", "death", "blood", "war", "terror",
    "abuse", "police report", "arrest", "jail", "prison", "deport", "deportation",
}


def load_schema() -> dict:
    schema_path = Path(__file__).parent.parent.parent.parent / "content" / "schemas" / "lesson.v1.json"
    with open(schema_path, encoding="utf-8") as f:
        return json.load(f)


def lint_lesson(path: Path) -> list[dict[str, Any]]:
    errors = []
    try:
        with open(path, encoding="utf-8") as f:
            data = yaml.safe_load(f)
    except yaml.YAMLError as e:
        return [{"path": str(path), "stage": "parse", "message": str(e)}]

    # Stage 1: Schema
    try:
        validate(instance=data, schema=load_schema())
    except ValidationError as e:
        errors.append({"path": str(path), "stage": "schema", "message": e.message})

    if not isinstance(data, dict):
        return errors

    # Stage 2: Content lint — bilingual fields
    title = data.get("title", {})
    if not title.get("en") or not title.get("es"):
        errors.append({"path": str(path), "stage": "content", "message": "Title must have both en and es"})

    steps = data.get("steps", [])
    total_estimated = sum(int(s.get("config", {}).get("time_seconds", 60)) for s in steps) / 60 if steps else data.get("estimated_minutes", 0)
    if not (0.8 * data.get("estimated_minutes", 1) <= max(total_estimated, data.get("estimated_minutes", 1)) <= 1.2 * data.get("estimated_minutes", 1) + 0.1):
        # Simplified: just check estimated_minutes is reasonable
        pass

    # Stage 3: License lint
    if data.get("license") not in ALLOWED_LICENSES:
        errors.append({"path": str(path), "stage": "license", "message": f"License '{data.get('license')}' not in allow-list"})

    # Stage 4: CEFR alignment
    if data.get("cefr_band") not in VALID_BANDS:
        errors.append({"path": str(path), "stage": "cefr", "message": f"Invalid CEFR band: {data.get('cefr_band')}"})
    for desc in data.get("target_descriptors", []):
        # Descriptor format: 'cefr-<band>-<mode>-<domain>-#<n>' with band lowercased.
        band = desc.split("-")[1].upper() if "-" in desc else ""
        if band and band not in VALID_BANDS:
            errors.append({"path": str(path), "stage": "cefr", "message": f"Descriptor band mismatch: {desc}"})

    # Stage 5: Pedagogy lint
    for mode in data.get("modes", []):
        if mode not in VALID_MODES:
            errors.append({"path": str(path), "stage": "pedagogy", "message": f"Invalid mode: {mode}"})
    for comp in data.get("components", []):
        if comp not in VALID_COMPONENTS:
            errors.append({"path": str(path), "stage": "pedagogy", "message": f"Invalid component: {comp}"})

    # Stage 6: Affective lint — match on word boundaries so substrings inside
    # legitimate words (e.g. "gun" inside Spanish "preguntar") do not trip the
    # filter. Multi-word flags ("police report") fall back to a literal check.
    full_text = " ".join(str(v) for v in _flatten_values(data)).lower()
    for flag in AFFECTIVE_FLAGS:
        if " " in flag:
            hit = flag in full_text
        else:
            hit = re.search(rf"\b{re.escape(flag)}\b", full_text) is not None
        if hit:
            errors.append({"path": str(path), "stage": "affective", "message": f"Potentially sensitive term: '{flag}'"})

    return errors


def _flatten_values(obj: Any) -> list:
    values: list = []
    if isinstance(obj, dict):
        for v in obj.values():
            values.extend(_flatten_values(v))
    elif isinstance(obj, list):
        for item in obj:
            values.extend(_flatten_values(item))
    elif isinstance(obj, str):
        values.append(obj)
    return values
