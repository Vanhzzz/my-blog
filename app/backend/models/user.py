from ..core.time import utc_now

from sqlalchemy import Boolean, Column, DateTime, Integer, String

from ..database.connection import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True)

    username = Column(
        String(30),
        unique=True,
        nullable=False,
        index=True
    )

    email = Column(
        String(255),
        unique=True,
        nullable=False,
        index=True
    )

    password_hash = Column(
        String(255),
        nullable=False
    )

    role = Column(
        String(20),
        nullable=False,
        default="user"
    )

    is_active = Column(
        Boolean,
        nullable=False,
        default=True
    )

    timezone = Column(
        String(64),
        nullable=False,
        default="UTC"
    )
    
    created_at = Column(
        DateTime,
        nullable=False,
        default=utc_now
    )

