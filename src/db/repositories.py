from sqlalchemy.orm import Session

from src.core.security import get_password_hash
from src.db.models.user import User


def create_user_repo(db_session: Session, email: str, password: str):
    existing = db_session.query(User).filter(User.email == email).first()
    if existing:
        return None
    hashed_password = get_password_hash(password)
    db_user = User(email=email, hashed_password=hashed_password)
    db_session.add(db_user)
    db_session.commit()
    db_session.refresh(db_user)
    return db_user


def get_user_repo(db_session: Session, user_id: int):
    return db_session.query(User).filter(User.id == user_id).first()


def get_user_by_email(db_session: Session, email: str):
    return db_session.query(User).filter(User.email == email).first()
