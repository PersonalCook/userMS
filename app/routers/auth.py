from fastapi import APIRouter, Depends, HTTPException, Response, Body
from sqlalchemy.orm import Session
from ..database import SessionLocal
from .. import models, schemas
from ..utils.auth import hash_password, verify_password, create_jwt
from ..metrics import (
    user_registrations,
    user_logins
)

router = APIRouter(prefix="/auth")

ERROR_400 = {
    "model": schemas.ErrorResponse,
    "description": "Bad request",
    "content": {"application/json": {"example": {"detail": "Email exists"}}},
}
ERROR_502 = {
    "model": schemas.ErrorResponse,
    "description": "Upstream error",
    "content": {"application/json": {"example": {"detail": "Database unavailable"}}},
}

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.post(
    "/register",
    response_model=schemas.RegisterResponse,
    summary="Register user",
    responses={
        200: {"description": "OK", "content": {"application/json": {"example": {"msg": "User created"}}}},
        400: ERROR_400,
        422: {"description": "Validation error"},
        502: ERROR_502,
    },
)
def register(
    user: schemas.UserCreate = Body(
        ...,
        examples={
            "example": {
                "value": {
                    "email": "ana@example.com",
                    "password": "secret123",
                    "username": "ana",
                    "public_name": "Ana",
                }
            }
        },
    ),
    db: Session = Depends(get_db),
):
    status_ = "success"
    try:
        existing_email = db.query(models.User).filter(models.User.email == user.email).first()
        existing_username = db.query(models.User).filter(models.User.username == user.username).first()
        if existing_email:
            status_ = "error"
            raise HTTPException(400, "Email exists")
        if existing_username:
            status_ = "error"
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
    except HTTPException:
        status_ = "error"
        raise
    except Exception as e:
        status_ = "error"
        raise HTTPException(status_code=502, detail=str(e))
    finally:
        user_registrations.labels(source="api", status=status_).inc()

@router.post(
    "/login",
    response_model=schemas.LoginResponse,
    summary="Login",
    responses={
        200: {
            "description": "OK",
            "content": {"application/json": {"example": {"access_token": "jwt", "user_id": 1}}},
        },
        400: ERROR_400,
        422: {"description": "Validation error"},
        502: ERROR_502,
    },
)
def login(
    user: schemas.UserLogin = Body(
        ...,
        examples={"example": {"value": {"email": "ana@example.com", "password": "secret123"}}},
    ),
    db: Session = Depends(get_db),
):

    status_ = "success"
    try:
        db_user = db.query(models.User).filter(models.User.email == user.email).first()

        if not db_user:
            status_ = "error"
            raise HTTPException(status_code=400, detail="Invalid email or password")

        if not verify_password(user.password, db_user.password_hash):
            status_ = "error"
            raise HTTPException(status_code=400, detail="Invalid email or password")

        token = create_jwt(db_user.user_id)

        return {"access_token": token, "user_id": db_user.user_id}
    except HTTPException:
        status_ = "error"
        raise
    except Exception as e:
        status_ = "error"
        raise HTTPException(status_code=502, detail=str(e))
    finally:
        user_logins.labels(source="api", status=status_).inc()
