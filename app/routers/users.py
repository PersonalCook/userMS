from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import or_

from ..database import SessionLocal
from .. import models

router = APIRouter(prefix="/users", tags=["Users"])


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.get("/by-username/{username}")
def get_user_by_username(username: str, db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.username == username).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return {"user_id": user.user_id, "username": user.username, "public_name": user.public_name, "email": user.email}

@router.get("/search")
def search_users(q: str, skip: int = 0, limit: int = 20, db: Session = Depends(get_db)):
    pattern = f"%{q}%"
    users = (
        db.query(models.User)
        .filter(or_(models.User.username.ilike(pattern), models.User.public_name.ilike(pattern)))
        .offset(skip)
        .limit(limit)
        .all()
    )
    return [
        {
            "user_id": u.user_id,
            "username": u.username,
            "public_name": u.public_name,
            "email": u.email,
        }
        for u in users
    ]

@router.get("/{user_id}")
def get_user_by_id(user_id: int, db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.user_id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return {"user_id": user.user_id, "username": user.username, "public_name": user.public_name, "email": user.email}
