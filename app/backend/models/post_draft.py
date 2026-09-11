from ..core.time import utc_now

from sqlalchemy import Column, DateTime, ForeignKey, Integer, String, Text

from ..database.connection import Base

class PostDraft(Base):
    __tablename__ = "post_drafts"

    id = Column(
        Integer,
        primary_key=True
    )

    post_id = Column(
        Integer,
        ForeignKey("posts.id"),
        nullable=True,
        unique=True,
        index=True
    )

    author_id = Column(
        Integer,
        ForeignKey("users.id"),
        nullable=False,
        index=True
    )

    title = Column(
        String(255),
        nullable=True
    )

    slug = Column(
        String(255),
        nullable=True,
        index=True
    )

    summary = Column(
        Text,
        nullable=True
    )

    content = Column(
        Text,
        nullable=True
    )

    category = Column(
        String(100),
        nullable=True
    )

    cover_image_url = Column(
        String(500),
        nullable=True
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