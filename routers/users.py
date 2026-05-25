from fastapi import APIRouter, Depends, HTTPException
import schemas
from sqlalchemy.orm import Session
import models
from database import get_db
import random
import logging

router = APIRouter(prefix="/auth", tags=["Auth"])
logger = logging.getLogger(__name__)

def random_number():
    r = []
    for i in range(1, 9):
        abc = random.randint(1, 9)
        r.append(abc)
    xyz = ''.join(str(x) for x in r)
    return xyz


@router.post("/register", response_model=schemas.UserResponse, status_code=201)
def register(user: schemas.UserCreate, db: Session = Depends(get_db)):
    '''To register a new user'''
    logger.info(f"Register attempt for username='{user.username}'")
    try:
        user_db = db.query(models.User).filter(models.User.username == user.username).first()
        emailaddress = db.query(models.User).filter(models.User.email == user.email).first()
        if user_db:
            logger.warning(f"Registration failed: username '{user.username}' already taken")
            raise HTTPException(status_code=400, detail="Username already taken!")
        if emailaddress:
            logger.warning(f"Registration failed: email already taken")
            raise HTTPException(status_code=400, detail="Email already taken!")
        data = models.User(
            username=user.username,
            email=user.email,
            password=user.password,
            account_number=random_number()
        )
        db.add(data)
        db.commit()
        db.refresh(data)
        logger.info(f"User registered successfully: username='{data.username}', account='{data.account_number}'")
        return data
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error during registration: {e}")
        db.rollback()
        raise HTTPException(status_code=500, detail="An error occurred during registration")


@router.post("/login", status_code=200)
def login(user: schemas.UserLogin, db: Session = Depends(get_db)):
    '''Login a valid user'''
    logger.info(f"Login attempt for account='{user.account_number}'")
    try:
        user_obj = db.query(models.User).filter(
            models.User.account_number == user.account_number,
            models.User.password == user.password,
        ).first()
        if not user_obj:
            logger.warning(f"Login failed: invalid credentials for account='{user.account_number}'")
            raise HTTPException(status_code=400, detail="Invalid credentials")
        logger.info(f"Login successful for account='{user.account_number}'")
        return {"message": "Login successful!"}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error during login: {e}")
        raise HTTPException(status_code=500, detail="An error occurred during login")


@router.patch("/update/{account_number_value}", status_code=200, response_model=schemas.UserResponse)
def update_user(account_number_value: str, user: schemas.UserUpdate, db: Session = Depends(get_db)):
    '''Update user account details'''
    logger.info(f"Update attempt for account='{account_number_value}'")
    try:
        user_obj = db.query(models.User).filter(models.User.account_number == account_number_value).first()
        if not user_obj:
            logger.warning(f"Update failed: account='{account_number_value}' not found")
            raise HTTPException(status_code=404, detail="User not found")
        if user.username and user.username != user_obj.username:
            if db.query(models.User).filter(models.User.username == user.username).first():
                logger.warning(f"Update failed: username '{user.username}' already taken")
                raise HTTPException(status_code=400, detail="Username already taken!")
            user_obj.username = user.username
        if user.email and user.email != user_obj.email:
            if db.query(models.User).filter(models.User.email == user.email).first():
                logger.warning(f"Update failed: email already taken for account='{account_number_value}'")
                raise HTTPException(status_code=400, detail="Email already taken!")
            user_obj.email = user.email
        if user.password and user.password != user_obj.password:
            user_obj.password = user.password
        db.commit()
        logger.info(f"Account updated successfully: account='{account_number_value}'")
        return user_obj
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating user {account_number_value}: {e}")
        db.rollback()
        raise HTTPException(status_code=500, detail="An error occurred while updating the account")


@router.delete('/delete/{account_number_value}', status_code=204)
def delete_user(account_number_value: str, db: Session = Depends(get_db)):
    '''Delete a user'''
    logger.info(f"Delete attempt for account='{account_number_value}'")
    try:
        user = db.query(models.User).filter(models.User.account_number == account_number_value).first()
        if not user:
            logger.warning(f"Delete failed: account='{account_number_value}' not found")
            raise HTTPException(status_code=404, detail="User not found")
        db.delete(user)
        db.commit()
        logger.info(f"Account deleted successfully: account='{account_number_value}'")
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting user {account_number_value}: {e}")
        db.rollback()
        raise HTTPException(status_code=500, detail="An error occurred while deleting the account")
