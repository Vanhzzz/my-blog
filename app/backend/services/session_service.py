from datetime import datetime, timedelta, timezone

from sqlalchemy.orm import Session

from ..core.security import generate_session_token, hash_session_token

from ..models.session import UserSession
from ..models.user import User

USER_SESSION_DAYS = 7
ADMIN_SESSION_HOURS = 12

def utc_now():
    return datetime.now(timezone.utc).replace(tzinfo=None)

def create_session(db: Session, user: User, user_agent: str | None = None, ip_address: str | None = None):
    raw_token = generate_session_token()
    token_hash = hash_session_token(raw_token)

    now = utc_now()

    if user.role == "admin":
        expires_at = now + timedelta(hours=ADMIN_SESSION_HOURS)
    else:
        expires_at = now + timedelta(days=USER_SESSION_DAYS)

    session = UserSession(
        user_id=user.id,
        token_hash=token_hash,
        created_at=now,
        expires_at=expires_at,
        last_seen_at=now,
        user_agent=user_agent, 
        ip_address=ip_address
    )

    db.add(session)
    db.commit()
    db.refresh(session)

    return raw_token, session

def get_session(db: Session, raw_token: str):
    token_hash = hash_session_token(raw_token)

    session = db.query(UserSession).filter(UserSession.token_hash == token_hash).first()

    if not session:
        return None

    if session.revoked_at is not None:
        return None

    if session.expires_at <= utc_now():
        return None

    return session

def revoke_session(db: Session, raw_token: str) -> bool:
    token_hash = hash_session_token(raw_token)

    session = db.query(UserSession).filter(UserSession.token_hash == token_hash).first()

    if not session:
        return False

    if session.revoked_at is None:
        session.revoked_at = utc_now()

    db.commit()

    return True



