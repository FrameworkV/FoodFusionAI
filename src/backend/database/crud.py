from sqlmodel import Session, select
from backend.database.auth import create_password_hash, valid_password
from backend.models.user import User, User


def create_user(db: Session, user: User):
    hashed_password = create_password_hash(user.password)
    db_user = User(username=user.username, hashed_password=hashed_password, role=user.role)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


def get_user(db: Session, username: str):
    statement = select(User).where(User.username == username)
    result = db.exec(statement).first()
    return result
