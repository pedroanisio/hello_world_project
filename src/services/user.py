from sqlalchemy.orm import Session

from src.db.repositories import create_user_repo, get_user_repo
from src.core.security import validate_password_strength
from src.core.exceptions import PasswordTooWeakException

def user_create_service(db: Session, email: str, password: str):
    if not validate_password_strength(password):
        raise PasswordTooWeakException("Password must be at least 8 characters, contain letters and numbers.")
    return create_user_repo(db, email, password)

def user_read_service(db: Session, user_id: int):
    return get_user_repo(db, user_id)
