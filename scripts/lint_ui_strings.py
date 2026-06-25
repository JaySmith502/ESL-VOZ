"""Affective-filter linter for UI strings (M1 acceptance #8).

Fails CI when any string in frontend/messages/*.json contains language that
raises Krashen's affective filter — judgmental, anxiety-inducing, or
shame-coded phrasing. Keep the banlist small and high-signal; a long banlist
becomes its own problem.

Run: python scripts/lint_ui_strings.py
"""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
MESSAGES_DIR = REPO_ROOT / "frontend" / "messages"

# Word-boundary patterns. Lowercased; the scan is case-insensitive.
BANNED = [
    # English
    r"\bwrong\b",
    r"\bincorrect\b",
    r"\bfailed\b",
    r"\bfailure\b",
    r"\bstupid\b",
    r"\bdumb\b",
    r"\bbad job\b",
    r"\btry harder\b",
    r"\byou lost\b",
    # Spanish
    r"\bincorrecto\b",
    r"\bfallaste\b",
    r"\bestúpido\b",
    r"\btonto\b",
    r"\bmal hecho\b",
]
_RX = re.compile("|".join(BANNED), re.IGNORECASE)


def _walk(obj, path: str = ""):
    """Yield (json-path, string) for every string leaf."""
    if isinstance(obj, dict):
        for k, v in obj.items():
            yield from _walk(v, f"{path}.{k}" if path else k)
    elif isinstance(obj, list):
        for i, v in enumerate(obj):
            yield from _walk(v, f"{path}[{i}]")
    elif isinstance(obj, str):
        yield path, obj


def lint_file(path: Path) -> list[str]:
    data = json.loads(path.read_text(encoding="utf-8"))
    errs = []
    for json_path, value in _walk(data):
        m = _RX.search(value)
        if m:
            errs.append(f"{path.name}:{json_path}: banned phrase {m.group(0)!r} in {value!r}")
    return errs


def main() -> int:
    files = sorted(MESSAGES_DIR.glob("*.json"))
    if not files:
        print(f"[warn] no message files under {MESSAGES_DIR}")
        return 0
    all_errs = []
    for p in files:
        errs = lint_file(p)
        if errs:
            all_errs.extend(errs)
        else:
            print(f"[ok] {p.name}")
    if all_errs:
        print("\nAffective-filter violations:")
        for e in all_errs:
            print(f"  [FAIL] {e}")
        return 1
    print("All UI strings passed the affective-filter lint.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
