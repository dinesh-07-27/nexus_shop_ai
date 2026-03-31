from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from fastapi.security import OAuth2PasswordRequestForm

from app.db import models, database
from app.schemas import user as schemas
from app.core import security

router = APIRouter(prefix="/api/v1/users", tags=["Users (v1)"])

@router.post("/register", response_model=schemas.UserResponse)
def register(user: schemas.UserCreate, db: Session = Depends(database.get_db)):
    db_user = db.query(models.User).filter(models.User.email == user.email).first()
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    hashed_password = security.get_password_hash(user.password)
    # is_admin role explicitly inserted into database
    new_user = models.User(
        email=user.email, 
        hashed_password=hashed_password, 
        full_name=user.full_name, 
        is_admin=user.is_admin
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user

@router.post("/login", response_model=schemas.Token)
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(database.get_db)):
    user = db.query(models.User).filter(models.User.email == form_data.username).first()
    if not user or not security.verify_password(form_data.password, user.hashed_password):
        raise HTTPException(status_code=400, detail="Incorrect email or password")
    
    # Store sub (email), id, and RBAC role in JWT
    access_token = security.create_access_token(data={
        "sub": user.email, 
        "user_id": user.id,
        "is_admin": user.is_admin
    })
    return {"access_token": access_token, "token_type": "bearer"}

@router.get("/me", response_model=schemas.UserResponse)
def read_users_me(current_user: models.User = Depends(security.get_current_user)):
    return current_user

@router.get("/", response_model=list[schemas.UserResponse])
def read_all_users(
    db: Session = Depends(database.get_db),
    admin_user: models.User = Depends(security.require_admin_role)
):
    """Admin Only: Returns the list of all registered users in the system."""
    return db.query(models.User).all()

