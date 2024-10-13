from sqlmodel import Session, select
from backend.database.auth import create_password_hash
from backend.models.user import User


def create_user(db: Session, user: User):
    hashed_password = create_password_hash(user.password)
    db_user = User(username=user.username, password=hashed_password, email=user.email)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


def get_user(db: Session, username: str):
    statement = select(User).where(User.username == username)
    result = db.exec(statement).first()
    return result
