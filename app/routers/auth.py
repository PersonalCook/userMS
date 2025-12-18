from fastapi import APIRouter, Depends, HTTPException, Response
from sqlalchemy.orm import Session
from ..database import SessionLocal
from .. import models, schemas
from ..utils.auth import hash_password, verify_password, create_jwt


router = APIRouter(prefix="/auth")

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.post("/register")
def register(user: schemas.UserCreate, db: Session = Depends(get_db)):
    existing_email = db.query(models.User).filter(models.User.email == user.email).first()
    existing_username = db.query(models.User).filter(models.User.username == user.username).first()
    if existing_email:
        raise HTTPException(400, "Email exists")
    if existing_username:
        raise HTTPException(400, "Username exists")

    new_user = models.User(
        email=user.email,
        password_hash=hash_password(user.password),
        username=user.username,
        public_name=user.public_name,
        birthdate=user.birthdate
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return {"msg": "User created"}


@router.post("/login")
def login(user: schemas.UserLogin, db: Session = Depends(get_db)):

    db_user = db.query(models.User).filter(models.User.email == user.email).first()

    if not db_user:
        raise HTTPException(status_code=400, detail="Invalid email or password")

    if not verify_password(user.password, db_user.password_hash):
        raise HTTPException(status_code=400, detail="Invalid email or password")

    token = create_jwt(db_user.user_id)

    return {"access_token": token, "user_id": db_user.user_id}
