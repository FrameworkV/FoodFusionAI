from sqlmodel import Session, select
from foodfusionai.models.user import User
from foodfusionai.models.groceries import ShoppingList, Recipe, Item


def create_user(db: Session, user: User):
    db.add(user)
    db.commit()
    db.refresh(user)


def get_user(db: Session, username: str):
    statement = select(User).where(User.username == username)
    result = db.exec(statement).first()
    return result


def update_user(db: Session, user_id: int, updated_user: User):
    statement = select(User).where(User.id == user_id)
    db_user = db.exec(statement).first()

    if not db_user:
        raise ValueError("user not found in database")
    
    for key, value in updated_user.model_dump(exclude_unset=True).items():  #sql model objects are not natively iterable
        setattr(db_user, key, value)

        db.add(db_user)
        db.commit()
        db.refresh(db_user)

    return db_user


def delete_user(db: Session, user_id: int):
    statement = select(User).where(User.id == user_id)
def delete_user(db: Session, user_id: int):
    statement = select(User).where(User.id == user_id)
    deleted_user = db.exec(statement).first()
    if not deleted_user:
        raise ValueError("user not found in database")
    if not deleted_user:
        raise ValueError("user not found in database")
    db.delete(deleted_user)
    db.commit()

def get_recipe(db: Session, recipe_id: int):
    statement = select(Recipe.content).where(Recipe.id == recipe_id)
    result = db.exec(statement).first()

    return result

def get_user_stock(db: Session, user_id: int):
    statement = select(Item).where(Item.user_id == user_id)
    result = db.exec(statement).all()

    return result

def create_shopping_list(db: Session, shopping_list: ShoppingList):
    db.add(shopping_list)
    db.commit()
    db.refresh(shopping_list)

def delete_shopping_list(db: Session, id: int):
    statement = select(ShoppingList).where(ShoppingList.id == id)
    deleted_shopping_list = db.exec(statement).first()
    db.delete(deleted_shopping_list)
    db.commit()
