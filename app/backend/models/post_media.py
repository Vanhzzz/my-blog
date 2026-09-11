from ..core.time import utc_now

from sqlalchemy import Column, DateTime, ForeignKey, Integer, String

from ..database.connection import Base

class PostMedia(Base):
    __tablename__ = "post_media"

    id = Column(
        Integer,
        primary_key=True
    )

    draft_id = Column(
        Integer,
        ForeignKey("post_drafts.id"),
        nullable=True,
        index=True
    )

    post_id = Column(
        Integer,
        ForeignKey("posts.id"),
        nullable=True,
        index=True
    )

    uploaded_by = Column(
        Integer,
        ForeignKey("users.id"),
        nullable=False,
        index=True
    )

    blob_url = Column(
        String(1000),
        nullable=False
    )

    blob_pathname = Column(
        String(500),
        nullable=False,
        unique=True,
        index=True
    )

    media_type = Column(
        String(20),
        nullable=False
    )

    created_at = Column(
        DateTime,
        nullable=False,
        default=utc_now
    )