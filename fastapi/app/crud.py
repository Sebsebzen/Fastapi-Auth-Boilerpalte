from sqlalchemy.orm import Session
from . import auth, models, schemas
import uuid
from typing import Optional

def get_user(db: Session, id: str):
    return db.query(models.UserModel).filter(models.UserModel.id == id).first()

def get_user_by_username(db: Session, username: str):
    user = db.query(models.UserModel).filter(models.UserModel.username == username).first()
    return user

def get_user_by_email(db: Session, email: str):
    user = db.query(models.UserModel).filter(models.UserModel.email == email).first()
    return user

def create_user(db: Session, user: schemas.UserRegister, token: Optional[str] = None):
    hashed_password = auth.get_password_hash(user.password)
    id = uuid.uuid4()
    while get_user(db=db,id=str(id)):
        id = uuid.uuid4()
    
    db_user = models.UserModel(
        id=str(id),
        email=user.email,
        username=user.username,
        hashed_password=hashed_password,
        verification_token=token
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

def get_users(db: Session, skip: int = 0, limit: int = 100):
    users = db.query(models.UserModel).offset(skip).limit(limit).all()
    return users