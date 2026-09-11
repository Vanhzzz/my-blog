from ..core.time import utc_now

from sqlalchemy import Column, DateTime, ForeignKey, Integer, String

from ..database.connection import Base

class UserSession(Base):
    __tablename__ = "sessions"
    
    id = Column(
        Integer,
        primary_key=True
    )

    user_id = Column(
        Integer,
        ForeignKey("users.id"),
        nullable=False,
        index=True
    )

    token_hash = Column(
        String(64),
        unique=True,
        nullable=False,
        index=True
    )

    created_at = Column(
        DateTime,
        nullable=False,
        default=utc_now
    )

    expires_at = Column(
        DateTime,
        nullable=False,
        index=True
    )

    last_seen_at = Column(
        DateTime,
        nullable=True
    )

    revoked_at = Column(
        DateTime,
        nullable=True
    )

    user_agent = Column(
        String(255),
        nullable=True
    )

    ip_address = Column(
        String(45),
        nullable=True
    )