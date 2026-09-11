from sqlalchemy.orm import Session

from ..models.post import Post
from ..models.post_draft import PostDraft
from ..models.post_media import PostMedia

def get_draft(db: Session, draft_id: int):
    return db.query(PostDraft).filter(PostDraft.id == draft_id).first()

def get_dradt_by_post(db: Session, post_id: int):
    return db.query(PostDraft).filter(PostDraft.post_id == post_id).first()

def create_draft(
        db: Session,
        author_id: int,
        title: str | None = None,
        slug: str | None = None,
        summary: str | None = None,
        content: str | None = None,
        category: str | None = None,
        cover_image_url: str | None = None
):
    draft = PostDraft(
        author_id=author_id,
        title=title,
        slug=slug,
        summary=summary,
        content=content,
        category=category,
        cover_image_url=cover_image_url
    )

    db.add(draft)
    db.commit()
    db.refresh(draft)

    return draft

def create_draft_from_post(db: Session, post: Post):
    existing_draft = get_dradt_by_post(db, post.id)

    if existing_draft:
        return existing_draft

    draft = PostDraft(
        post_id=post.id,
        author_id=post.author_id,
        title=post.title,
        slug=post.slug,
        summary=post.summary,
        content=post.content,
        category=post.category,
        cover_image_url=post.cover_image_url
    )

    db.add(draft)
    db.commit()
    db.refresh(draft)

    return draft

def update_draft(
        db: Session,
        draft: PostDraft,
        title: str | None,
        slug: str | None,
        summary: str | None,
        content: str | None,
        category: str | None,
        cover_image_url: str | None
):
    draft.title = title
    draft.slug = slug
    draft.summary = summary
    draft.content = content
    draft.category = category
    draft.cover_image_url = cover_image_url

    db.commit()
    db.refresh(draft)

    return draft

def delete_draft(db: Session, draft: PostDraft):
    media_records = db.query(PostMedia).filter(PostMedia.id == draft.id).all()

    for media in media_records:
        db.delete(media)

    db.delete(draft)

    db.commit()

def publish_draft(db: Session, draft: PostDraft):
    title = (draft.title or "").strip()
    slug = (draft.slug or "").strip()
    content = draft.content or ""

    if not title:
        raise ValueError(
            "Title is required."
        )

    if not slug:
       raise ValueError(
            "Slug is required."
        )

    if not content.strip():
         raise ValueError(
            "Content is required."
        )

    existing_slug = db.query(Post).filter(Post.slug == slug).first()

    if (existing_slug and existing_slug.id != draft.post_id): #TH admin đang sửa nhưng lại xóa post cũ đang sửa
        raise ValueError(
            "Slug already exists."
        )

    if draft.post_id is None:
        post = Post(
            author_id=draft.author_id,
            title=title,
            slug=slug,
            summary=draft.summary,
            content=draft.content,
            category=draft.category,
            cover_image_url=draft.cover_image_url,
            status="published"
        )

        db.add(post)
        db.flush() #Sinh id post mới

    else: 
        post = db.query(Post).filter(Post.id == draft.post_id).first()

        if not post:
            raise ValueError(
                "Post does not exist."
            )

        post.title = title
        post.slug = slug
        post.summary = draft.summary
        post.content = draft.content
        post.category = draft.category
        post.cover_image_url = draft.cover_image_url
        post.status = "published"

    db.delete(draft)

    db.commit()
    db.refresh(post)

    return post

def delete_draft(db: Session, draft: PostDraft):
    db.delete(draft)
    db.commit()