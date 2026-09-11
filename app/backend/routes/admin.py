from fastapi import APIRouter, Depends, HTTPException, Request, status

from fastapi.responses import JSONResponse
from sqlalchemy import func
from sqlalchemy.orm import Session

from ..core.config import settings
from ..core.templates import templates
from ..database.session import get_db
from ..dependencies.admin import require_admin

from ..models.post import Post
from ..models.post_draft import PostDraft
from ..models.user import User

from ..services.post_draft_service import (
    create_draft,
    create_draft_from_post,
    delete_draft,
    get_draft,
    publish_draft,
    update_draft
)

router = APIRouter(
    prefix="/admin",
    tags=["Admin"]
)

@router.get("")
async def admin_dashboard(
    request: Request,
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    total_posts = (
        db.query(func.count(Post.id)).scalar() or 0
    )

    published_posts = (
        db.query(func.count(Post.id)).filter(Post.status == "published").scalar() or 0
    )

    draft_posts = (
        db.query(func.count(PostDraft.id)).scalar() or 0
    )

    total_users = (
        db.query(func.count(User.id)).scalar() or 0
    )

    recent_posts = (
        db.query(Post, User.username.label("author_username")).
        join(User, Post.author_id == User.id).
        order_by(Post.created_at.desc()).
        limit(5).all()
    )

    return templates.TemplateResponse(
        request=request,
        name="admin/dashboard.html",
        context={
            "title": "Admin Dashboard",
            "current_user": current_user,

            "total_posts": total_posts,
            "published_posts": published_posts,
            "draft_posts": draft_posts,
            "total_users": total_users,

            "recent_posts": recent_posts,

            "app_name": settings.APP_NAME,
            "app_env": settings.APP_ENV,
            "database_name": "TiDB Cloud"
        }
    )

@router.get("/posts/create")
async def create_post_page(
    request: Request,
    current_user: User = Depends(require_admin)
):
    return templates.TemplateResponse(
        request=request,
        name="admin/create_post.html",
        context={
            "title": "Create Post",
            "current_user": current_user,
            "draft": None
        }
    )

@router.delete("/posts/drafts/{draft_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_post_draft(
    draft_id: int,
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    draft = get_draft(db, draft_id)

    if not draft:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Draft not found."
        )

    if draft.author_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have access to this draft."
        ) 

    delete_draft(db, draft)
    
@router.post("/posts/autosave")
async def create_post_autosave(
    request: Request,
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    data = await request.json()

    draft = create_draft(
        db=db,
        author_id=current_user.id,
        title=data.get("title"),
        slug=data.get("slug"),
        summary=data.get("summary"),
        content=data.get("content"),
        category=data.get("category"),
        cover_image_url=data.get(
            "cover_image_url"
        )
    )

    return JSONResponse(
        status_code=201,
        content={
            "success": True,
            "draft_id": draft.id,
            "message": "Draft created."
        }
    )

@router.get("/posts/drafts")
async def draft_page(
    request: Request,
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    drafts = (db.query(PostDraft, User.username.label("author_username")).
            join(User, PostDraft.author_id == User.id).
            order_by(PostDraft.updated_at.desc())
            .all())

    return templates.TemplateResponse(
        request=request,
        name="admin/drafts.html",
        context={
            "title": "Drafts",
            "current_user": current_user,
            "drafts": drafts
        }
    )

@router.put("/posts/drafts/{draft_id}/autosave")
async def update_post_autosave(
    draft_id: int,
    request: Request,
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    draft = get_draft(db, draft_id)

    if not draft:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Draft not found."
        )

    data = await request.json()

    draft = update_draft(
        db=db,
        draft=draft,
        title=data.get("title"),
        slug=data.get("slug"),
        summary=data.get("summary"),
        content=data.get("content"),
        category=data.get("category"),
        cover_image_url=data.get(
            "cover_image_url"
        )
    )

    return {
        "success": True,
        "draft_id": draft.id,
        "message": "Draft saved."
    }

@router.get("/posts/drafts/{draft_id}/edit")
async def edit_draft_page(
    draft_id: int,
    request: Request,
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    draft = get_draft(db, draft_id)

    if not draft:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Draft not found."
        )

    return templates.TemplateResponse(
        request=request,
        name="admin/create_post.html",
        context={
            "title": "Edit Draft",
            "current_user": current_user,
            "draft": draft
        }
    )

@router.get("/posts/drafts/{draft_id}/preview")
async def preview_draft_page(
    draft_id: int, 
    request: Request,
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    draft = get_draft(db, draft_id)

    if not draft:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Draft not found."
        )

    return templates.TemplateResponse(
        request=request,
        name="admin/preview_post.html",
        context={
            "title": (
                draft.title or "Post Preview"
            ),
            "current_user": current_user,
            "draft": draft
        }
    ) 

@router.post("/posts/drafts/{draft_id}/publish")
async def publish_post_draft(
    draft_id: int,
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    draft = get_draft(db, draft_id)

    if not draft:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Draft not found."
        )

    try:
        post = publish_draft(db, draft)
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc)
        )

    return {
        "success": True,
        "post_id": post.id,
        "slug": post.slug,
        "redirect_url": f"/blog/{post.slug}"
    }

@router.post("/posts/{post_id}/edit")
async def create_edit_draft(
    post_id: int,
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    post = db.query(Post).filter(Post.id == post_id).first()

    if not post:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Post not found."
        )

    draft = create_draft_from_post(db, post)

    return {
        "success": True,
        "draft_id": draft.id,
        "edit_url": (
            f"/admin/posts/drafts/{draft.id}/edit"
        )
    }