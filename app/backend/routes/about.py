from fastapi import APIRouter, Depends, Request

from ..core.templates import templates
from ..dependencies.auth import get_current_user
from ..models.user import User

router = APIRouter(
    tags=["About"]
)

@router.get("/about")
async def about(
    request: Request,
    current_user: User | None = Depends(get_current_user)
):
    return templates.TemplateResponse(
        request=request,
        name="about.html",
        context={
            "title": "About",
            "current_user": current_user
        }
    )