import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from app.db import create_db_and_tables, engine
from app.services.lesson_ingest import ingest_lessons
from sqlmodel import Session


def main():
    create_db_and_tables()
    with Session(engine) as session:
        result = ingest_lessons(session)
        print("Ingested:", result["ingested"])
        if result["errors"]:
            print("Errors:", result["errors"])


if __name__ == "__main__":
    main()
