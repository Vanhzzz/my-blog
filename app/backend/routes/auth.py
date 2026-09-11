import re

from fastapi import APIRouter, Depends, Form, Request

from fastapi.responses import RedirectResponse

from sqlalchemy.orm import Session

from ..core.config import settings
from ..core.templates import templates
from ..database.session import get_db

from ..services.auth_service import authenticate_user, create_user, get_user_by_username, get_user_by_email

from ..services.session_service import create_session, revoke_session, USER_SESSION_DAYS, ADMIN_SESSION_HOURS

from email_validator import validate_email, EmailNotValidError

router = APIRouter(
    tags=["Authentication"]
)

@router.get("/register")
async def register_page(request: Request):
    return templates.TemplateResponse(
        request=request, 
        name="auth/register.html",
        context={
            "title": "Register"
        }
    )

@router.post("/register")
async def register(
    request: Request,
    username: str = Form(...),
    email: str = Form(...),
    password: str = Form(...),
    confirm_password: str = Form(...),
    db: Session = Depends(get_db)
):
    email = email.strip().lower()

    error = None

    if re.search(r"\s", username):
        error = "Username must not contain spaces."

    elif len(username) < 3:
        error = "Username must be at least 3 characters."

    elif len(username) > 30:
        error = "Username must not exceed 30 characters."

    elif not re.fullmatch(
        r"[A-Za-z0-9_]+",
        username
    ):
        error = "Username can only contain letters, numbers and underscores."

    else:
        try:
            email_info = validate_email(
                email,
                check_deliverability=False
            )

            email = email_info.normalized

        except EmailNotValidError:
            error = "Invalid email address."

    if not error and len(password) < 8:
        error = "Password must be at least 8 characters."

    elif not error and len(password) > 128:
        error = "Password must not exceed 128 characters."

    elif not error and password != confirm_password:
        error = "Passwords do not match."

    elif not error and get_user_by_username(
        db,
        username
    ):
        error = "Username already exists."

    elif not error and get_user_by_email(
        db,
        email
    ):
        error = "Email already exists."

    if error:
        return templates.TemplateResponse(
            request=request,
            name="auth/register.html",
            context={
                "title": "Register",
                "error": error
            },
            status_code=400
        )

    user = create_user(
        db,
        username,
        email,
        password
    )

    raw_token, _ = create_session(
        db,
        user,
        user_agent=request.headers.get(
            "user-agent"
        ),
        ip_address=(
            request.client.host
            if request.client
            else None
        )
    )

    response = RedirectResponse(
        url="/",
        status_code=303
    )

    response.set_cookie(
        key=settings.SESSION_COOKIE_NAME,
        value=raw_token,
        httponly=True,
        secure=settings.SESSION_HTTPS_ONLY,
        samesite="lax",
        max_age=USER_SESSION_DAYS * 24 * 60 * 60,
        path="/"
    )

    return response

@router.get("/login")
async def login_page(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="auth/login.html",
        context={
            "title": "Login"
        }
    )

@router.post("/login")
async def login(
    request: Request,
    login_value: str = Form(...),
    password: str = Form(...),
    db: Session = Depends(get_db)
):
    login_value = login_value.strip()

    if "@" in login_value:
        login_value = login_value.lower()

    user = authenticate_user(db, login_value, password)

    if not user:
        return templates.TemplateResponse(
            request=request,
            name="auth/login.html",
            context={
                "title": "Login",
                "error": "Invalid username/email or password.",
            },
            status_code=401
        )

    raw_token, _ = create_session(
        db, 
        user, 
        user_agent=request.headers.get("user-agent"), 
        ip_address=request.client.host if request.client else None
    )

    response = RedirectResponse(
        url="/",
        status_code=303
    )

    if user.role == "admin":
        max_age = ADMIN_SESSION_HOURS * 60 * 60
    else:
        max_age = USER_SESSION_DAYS * 24 * 60 * 60

    response.set_cookie(
        key=settings.SESSION_COOKIE_NAME,
        value=raw_token,
        httponly=True,
        secure=settings.SESSION_HTTPS_ONLY,
        samesite="lax",
        max_age=max_age,
        path="/"
    )

    return response

@router.post("/logout")
async def logout(
    request: Request,
    db: Session = Depends(get_db)
):
    raw_token = request.cookies.get(settings.SESSION_COOKIE_NAME)

    if raw_token:
        revoke_session(db, raw_token)

    response = RedirectResponse(
        url="/",
        status_code=303
    )

    response.delete_cookie(
        key=settings.SESSION_COOKIE_NAME,
        path="/"
    )

    return response