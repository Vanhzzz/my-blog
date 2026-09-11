from ..core.time import utc_now

from sqlalchemy import Column, DateTime, ForeignKey, Integer, String, Text

from ..database.connection import Base

class Post(Base):
    __tablename__ = "posts"

    id = Column(
        Integer,
        primary_key=True
    )

    author_id = Column(
        Integer,
        ForeignKey("users.id"),
        nullable=False,
        index=True
    )

    title = Column(
        String(255),
        nullable=False
    )

    slug = Column(
        String(255),
        unique=True,
        nullable=False,
        index=True
    )

    summary = Column(
        Text,
        nullable=True
    )

    content = Column(
        Text,
        nullable=False
    )

    category = Column(
        String(100),
        nullable=True
    )

    cover_image_url = Column(
        String(500),
        nullable=True
    )

    status = Column(
        String(20),
        nullable=False,
        default="published"
    )

    created_at = Column(
        DateTime,
        nullable=False,
        default=utc_now
    )

    updated_at = Column(
        DateTime,
        nullable=False,
        default=utc_now,
        onupdate=utc_now
    )