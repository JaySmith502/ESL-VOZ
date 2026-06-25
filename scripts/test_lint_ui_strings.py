"""Smoke check for the affective-filter linter.

Run: python scripts/test_lint_ui_strings.py
"""

from __future__ import annotations

import json
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from lint_ui_strings import lint_file


def _write(tmp: Path, name: str, payload: dict) -> Path:
    p = tmp / name
    p.write_text(json.dumps(payload), encoding="utf-8")
    return p


def main() -> int:
    with tempfile.TemporaryDirectory() as d:
        tmp = Path(d)

        clean = _write(tmp, "clean.json", {
            "lesson": {"continue": "Continue", "correct": "Good work", "tryAgain": "Try again"},
        })
        assert lint_file(clean) == [], "clean file should pass"

        dirty = _write(tmp, "dirty.json", {
            "lesson": {"feedback": "That was wrong, try again."},
            "alerts": ["You failed the test."],
        })
        errs = lint_file(dirty)
        assert any("wrong" in e.lower() for e in errs), f"missed 'wrong': {errs}"
        assert any("failed" in e.lower() for e in errs), f"missed 'failed': {errs}"

        # Word boundary: "wrongful" must NOT trip "wrong" (over-match guard).
        edge = _write(tmp, "edge.json", {"x": "wrongful arrest"})
        assert lint_file(edge) == [], f"over-matched 'wrongful': {lint_file(edge)}"

        # Spanish
        es = _write(tmp, "es.json", {"a": "Respuesta incorrecta."})
        # 'incorrecta' is the feminine of 'incorrecto'; banlist matches the masculine
        # form. We are NOT trying to lemmatize — banlist additions are deliberate.
        # This test pins current behavior.
        assert lint_file(es) == [], "es lemma not in banlist; expected pass"

        print("ok lint_ui_strings self-check")
        return 0


if __name__ == "__main__":
    sys.exit(main())
