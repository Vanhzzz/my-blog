from fastapi import Depends, HTTPException, status

from ..models.user import User
from .auth import require_login

def require_admin(current_user: User = Depends(require_login)):
    if current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )

    return current_user