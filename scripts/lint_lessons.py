import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT / "backend"))

from app.services.lesson_lint import lint_lesson

LESSONS_DIR = REPO_ROOT / "content" / "lessons"


def main():
    all_errors = []
    for path in LESSONS_DIR.glob("*.yaml"):
        errors = lint_lesson(path)
        all_errors.extend(errors)
        if not errors:
            print(f"[ok] {path.name}")

    if all_errors:
        for err in all_errors:
            print(f"[FAIL] {err['path']} [{err['stage']}]: {err['message']}")
        sys.exit(1)
    else:
        print("All lessons passed lint.")


if __name__ == "__main__":
    main()
