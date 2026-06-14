import hashlib
import secrets
import uuid
from datetime import datetime, timedelta, timezone

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import JWTError, jwt
from passlib.context import CryptContext
from sqlmodel import Session, select

from app.core.config import settings
from app.db import get_db
from app.models import ConsentGrant, ConsentLayer, MagicLinkToken, User, UserRole

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
security = HTTPBearer(auto_error=False)


def hash_token(token: str) -> str:
    return hashlib.sha256(token.encode()).hexdigest()


def create_access_token(user_id: uuid.UUID) -> str:
    expire = datetime.now(timezone.utc) + timedelta(minutes=settings.access_token_expire_minutes)
    payload = {"sub": str(user_id), "exp": expire}
    return jwt.encode(payload, settings.secret_key, algorithm=settings.algorithm)


def decode_access_token(token: str) -> uuid.UUID:
    try:
        payload = jwt.decode(token, settings.secret_key, algorithms=[settings.algorithm])
        return uuid.UUID(payload["sub"])
    except (JWTError, KeyError, ValueError):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")


def require_user(credentials: HTTPAuthorizationCredentials = Depends(security), db: Session = Depends(get_db)) -> User:
    if not credentials:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Missing token")
    user_id = decode_access_token(credentials.credentials)
    user = db.exec(select(User).where(User.id == user_id)).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found")
    return user


def require_role(*roles: UserRole):
    def checker(user: User = Depends(require_user)) -> User:
        if user.role not in roles:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Insufficient permissions")
        return user
    return checker


def create_or_get_user(db: Session, email: str, role: UserRole = UserRole.LEARNER) -> User:
    user = db.exec(select(User).where(User.email == email)).first()
    if not user:
        user = User(email=email, role=role)
        db.add(user)
        db.commit()
        db.refresh(user)
    return user


def create_magic_link(db: Session, user: User) -> str:
    raw = secrets.token_urlsafe(32)
    token = MagicLinkToken(
        token_hash=hash_token(raw),
        user_id=user.id,
        expires_at=datetime.now(timezone.utc) + timedelta(hours=settings.magic_link_expire_hours),
    )
    db.add(token)
    db.commit()
    return raw


def _as_utc(value: datetime) -> datetime:
    if value.tzinfo is None:
        return value.replace(tzinfo=timezone.utc)
    return value.astimezone(timezone.utc)


def verify_magic_link(db: Session, raw_token: str) -> User:
    token_hash = hash_token(raw_token)
    token = db.exec(select(MagicLinkToken).where(MagicLinkToken.token_hash == token_hash)).first()
    if not token or token.used_at or _as_utc(token.expires_at) < datetime.now(timezone.utc):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid or expired magic link")
    token.used_at = datetime.now(timezone.utc)
    db.add(token)
    db.commit()
    user = db.exec(select(User).where(User.id == token.user_id)).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="User not found")
    return user


def record_consent(db: Session, user_id: uuid.UUID, layer: ConsentLayer, version: str = "1.0") -> ConsentGrant:
    grant = ConsentGrant(user_id=user_id, layer=layer, version=version)
    db.add(grant)
    db.commit()
    db.refresh(grant)
    return grant


def has_consent(db: Session, user_id: uuid.UUID, layer: ConsentLayer) -> bool:
    grant = db.exec(
        select(ConsentGrant)
        .where(ConsentGrant.user_id == user_id)
        .where(ConsentGrant.layer == layer)
        .order_by(ConsentGrant.granted_at.desc())
    ).first()
    return grant is not None and grant.withdrawn_at is None
