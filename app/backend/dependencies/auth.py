from fastapi import Depends, HTTPException, Request, status

from sqlalchemy.orm import Session

from ..core.config import settings
from ..database.session import get_db
from ..models.user import User
from ..services.session_service import get_session

def get_current_user(request: Request, db: Session = Depends(get_db)):
    raw_token = request.cookies.get(settings.SESSION_COOKIE_NAME)

    if not raw_token:
        return None

    session = get_session(db, raw_token)

    if not session: 
        return None

    user = db.query(User).filter(User.id == session.user_id).first()

    if not user:
        return None

    if not user.is_active:
        return None

    return user

def require_login(current_user: User | None = Depends(get_current_user)):
    if not current_user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required"
        )

    return current_user

    