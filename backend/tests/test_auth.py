import pytest
from sqlmodel import Session, SQLModel, create_engine
from sqlmodel.pool import StaticPool

from app.models import UserRole
from app.services.auth import (
    create_access_token,
    create_magic_link,
    create_or_get_user,
    decode_access_token,
    verify_magic_link,
)


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


def test_create_or_get_user_creates_learner(db: Session):
    user = create_or_get_user(db, "learner@example.com")
    assert user.email == "learner@example.com"
    assert user.role == UserRole.LEARNER


def test_magic_link_lifecycle(db: Session):
    user = create_or_get_user(db, "magic@example.com")
    raw = create_magic_link(db, user)
    verified = verify_magic_link(db, raw)
    assert verified.id == user.id


def test_verify_magic_link_fails_on_reuse(db: Session):
    user = create_or_get_user(db, "reuse@example.com")
    raw = create_magic_link(db, user)
    verify_magic_link(db, raw)
    with pytest.raises(Exception):
        verify_magic_link(db, raw)


def test_access_token_round_trip(db: Session):
    user = create_or_get_user(db, "token@example.com")
    token = create_access_token(user.id)
    decoded = decode_access_token(token)
    assert decoded == user.id
