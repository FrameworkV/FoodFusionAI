from fastapi import APIRouter, Depends, UploadFile, HTTPException
from sqlmodel import Session
from typing import Dict, List
from foodfusionai.logs.logger_config import logger
from foodfusionai.database import database_setup, crud
from foodfusionai.models.user import User
from foodfusionai.models.groceries import Item
from foodfusionai.routers.users import _get_user

storage_router = APIRouter()

@storage_router.post("/upload_receipt")
async def upload_receipt(receipt: UploadFile, db: Session = Depends(database_setup.get_session), user: User = Depends(_get_user)) -> Dict[str, str]:
    try:
        logger.info(f"User {user.username} started uploading a receipt: {receipt.filename}")

        filename = receipt.filename
        content = await receipt.read()

        file_types = ["image/jpeg", "image/png"]

        if receipt.content_type not in file_types:
            logger.warning(f"User {user.username} tried uploading an invalid file type: {receipt.content_type}. Only {file_types} are allowed")
            raise HTTPException(status_code=400, detail=f"User {user.username} tried uploading an invalid file type: {receipt.content_type}. Only {file_types} are allowed")
        
        groceries = process_receipt(content)    # TODO correct name/class from feature/receipt branch

        crud.update_items(db, groceries, user)

        logger.info(f"Receipt {filename} uploaded successfully")

        return {"filename": filename, "message": f"Receipt {filename} uploaded successfully"}
    except Exception as e:
        logger.warning(f"Error uploading receipt for user {user.username}: {e}")
        raise HTTPException(status_code=500, detail=f"Error uploading receipt for user {user.username}: {e}")
    
@storage_router.get("/get_items")
async def get_items(db: Session = Depends(database_setup.get_session), user: User = Depends(_get_user)) -> List[Item]:
    logger.info(f"Attempt to retrieve items for user {user.username}")

    try:
        groceries = crud.get_items(db, user)

        logger.info(f"Items {groceries} retrieved successfully for user {user.username}")

        return groceries
    except Exception as e:
        logger.warning(f"Error retrieving items for user {user.username}: {e}")
        raise HTTPException(status_code=500, detail=f"Error retrieving items for user {user.username}: {e}")

@storage_router.post("/add_items")
async def add_items(groceries: List[Item], db: Session = Depends(database_setup.get_session), user: User = Depends(_get_user)) -> Dict[str, str]:
    logger.info(f"Attempt to add items for user {user.username}")
    
    try:
        crud.add_items(db, groceries, user)

        logger.info(f"Items added successfully for user {user.username}")

        return {"message": f"Items added successfully for user {user.username}"}
    except Exception as e:
        logger.warning(f"Error adding items for user {user.username}: {e}")
        raise HTTPException(status_code=500, detail=f"Error adding items for user {user.username}: {e}")

@storage_router.put("/update_items")
async def update_items(groceries: List[Item], db: Session = Depends(database_setup.get_session), user: User = Depends(_get_user)) -> Dict[str, str]:
    logger.info(f"Attempt to delete items for user {user.username}")
    
    try:
        crud.update_items(db, groceries, user)

        logger.info(f"Items deleted successfully for user {user.username}")

        return {"message": f"Items deleted successfully for user {user.username}"}
    except Exception as e:
        logger.warning(f"Error deleting items for user {user.username}: {e}")
        raise HTTPException(status_code=500, detail=f"Error deleting items for user {user.username}: {e}")
    
@storage_router.delete("/delete_items")
async def delete_items(groceries: List[Item], db: Session = Depends(database_setup.get_session), user: User = Depends(_get_user)) -> Dict[str, str]:
    logger.info(f"Attempt to delete items for user {user.username}")
    
    try:    
        crud.delete_items(db, groceries, user)

        logger.info(f"Items deleted successfully for user {user.username}")

        return {"message": f"Items deleted successfully for user {user.username}"}
    except Exception as e:
        logger.warning(f"Error deleting items for user {user.username}: {e}")
        raise HTTPException(status_code=500, detail=f"Error deleting items for user {user.username}: {e}")
