from sqlalchemy.orm import Session

from ..core.security import hash_password, verify_password

from ..models.user import User

def get_user_by_username(db: Session, username: str):
    return db.query(User).filter(User.username == username).first()

def get_user_by_email(db: Session, email: str):
    return db.query(User).filter(User.email == email).first()

def create_user(db: Session, username: str, email: str, password: str):
    password_hash = hash_password(password)

    user = User(username=username, email=email, password_hash=password_hash, role="user")

    db.add(user)
    db.commit()
    db.refresh(user)

    return user

def authenticate_user(db: Session, login_value: str, password: str):
    user = db.query(User).filter((User.username == login_value) | (User.email == login_value)).first()

    if not user:
        return None

    if not user.is_active:
        return None

    if not verify_password(password, user.password_hash):
        return None

    return user