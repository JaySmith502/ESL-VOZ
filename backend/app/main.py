from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api import auth, engine, instructor, lessons, onboarding, tutor
from app.db import create_db_and_tables


@asynccontextmanager
async def lifespan(app: FastAPI):
    create_db_and_tables()
    yield


app = FastAPI(title="ESL-voice API", version="0.1.0", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router, prefix="/auth", tags=["auth"])
app.include_router(onboarding.router, prefix="/onboarding", tags=["onboarding"])
app.include_router(engine.router, prefix="/engine", tags=["engine"])
app.include_router(lessons.router, prefix="/lessons", tags=["lessons"])
app.include_router(instructor.router, prefix="/instructor", tags=["instructor"])
app.include_router(tutor.router, prefix="/tutor", tags=["tutor"])


@app.get("/health")
def health():
    return {"status": "ok"}
