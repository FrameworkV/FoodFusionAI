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


def update_user(db: Session, updated_user: User):
    statement = select(User).where(User.id == updated_user.id)
    db_user = db.exec(statement).first()

    if not db_user:
        raise ValueError("user not found in database")
    
    fields_to_update = {}
    if db_user.username != updated_user.username:
        fields_to_update["username"] = updated_user.username
    if db_user.password != updated_user.password:
        fields_to_update["password"] = updated_user.password
    if db_user.email != updated_user.email:
        fields_to_update["email"] = updated_user.email
    if db_user.reset_code != updated_user.reset_code:
        fields_to_update["reset_code"] = updated_user.reset_code
    if db_user.reset_code_expiration != updated_user.reset_code_expiration:
        fields_to_update["reset_code_expiration"] = updated_user.reset_code_expiration
    if db_user.is_verified != updated_user.is_verified:
        fields_to_update["is_verified"] = updated_user.is_verified
    if set(db_user.groceries) != set(updated_user.groceries):
        fields_to_update["groceries"] = updated_user.groceries

    if fields_to_update:
        for key, value in fields_to_update.items():
            setattr(db_user, key, value)
        db.add(db_user)
        db.commit()
        db.refresh(db_user)

    return db_user


def delete_user(db: session, username: str):
    statement = select(User).where(User.username == username)
    deleted_user = db.exec(statement).first()
    db.delete(deleted_user)