from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import or_

from ..database import SessionLocal
from .. import models, schemas

router = APIRouter(prefix="/users", tags=["Users"])

EXAMPLE_USER = {
    "user_id": 1,
    "username": "ana",
    "public_name": "Ana",
    "email": "ana@example.com",
}

ERROR_404 = {
    "model": schemas.ErrorResponse,
    "description": "Not found",
    "content": {"application/json": {"example": {"detail": "User not found"}}},
}
ERROR_500 = {
    "model": schemas.ErrorResponse,
    "description": "Internal error",
    "content": {"application/json": {"example": {"detail": "Internal server error"}}},
}


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.get(
    "/by-username/{username}",
    response_model=schemas.UserSummary,
    summary="Get user by username",
    responses={
        200: {"description": "OK", "content": {"application/json": {"example": EXAMPLE_USER}}},
        404: ERROR_404,
        422: {"description": "Validation error"},
        500: ERROR_500,
    },
)
def get_user_by_username(username: str, db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.username == username).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return {"user_id": user.user_id, "username": user.username, "public_name": user.public_name, "email": user.email}

@router.get(
    "/search",
    response_model=list[schemas.UserSummary],
    summary="Search users",
    responses={
        200: {"description": "OK", "content": {"application/json": {"example": [EXAMPLE_USER]}}},
        422: {"description": "Validation error"},
        500: ERROR_500,
    },
)
def search_users(
    q: str = Query(..., description="Search in username or public name", examples={"example": {"value": "an"}}),
    skip: int = Query(0, ge=0, description="Number of items to skip", examples={"example": {"value": 0}}),
    limit: int = Query(20, ge=1, le=100, description="Max items to return", examples={"example": {"value": 20}}),
    db: Session = Depends(get_db),
):
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

@router.get(
    "/{user_id}",
    response_model=schemas.UserSummary,
    summary="Get user by id",
    responses={
        200: {"description": "OK", "content": {"application/json": {"example": EXAMPLE_USER}}},
        404: ERROR_404,
        422: {"description": "Validation error"},
        500: ERROR_500,
    },
)
def get_user_by_id(user_id: int, db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.user_id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return {"user_id": user.user_id, "username": user.username, "public_name": user.public_name, "email": user.email}
