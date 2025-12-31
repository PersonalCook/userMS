from fastapi import APIRouter, Depends, HTTPException, Header, status
from sqlalchemy.orm import Session

from ..database import SessionLocal
from ..utils.auth import decode_jwt
from .. import models, schemas

from fastapi import Security
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

security = HTTPBearer()

router = APIRouter(prefix="/profile", tags=["Profile"])

EXAMPLE_PROFILE = {
    "user_id": 1,
    "email": "ana@example.com",
    "username": "ana",
    "public_name": "Ana",
    "birthdate": "1999-01-01",
}

ERROR_401 = {
    "model": schemas.ErrorResponse,
    "description": "Unauthorized",
    "content": {"application/json": {"example": {"detail": "Invalid or expired token"}}},
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


def get_current_user(credentials: HTTPAuthorizationCredentials = Security(security)):
    token = credentials.credentials  

    try:
        payload = decode_jwt(token)
        return payload["user_id"]
    except:
        raise HTTPException(status_code=401, detail="Invalid or expired token")

@router.get(
    "/",
    response_model=schemas.UserProfile,
    summary="Get my profile",
    responses={
        200: {"description": "OK", "content": {"application/json": {"example": EXAMPLE_PROFILE}}},
        401: ERROR_401,
        404: ERROR_404,
        422: {"description": "Validation error"},
        500: ERROR_500,
    },
)
def get_profile(
    user_id: int = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    user = (
        db.query(models.User)
        .filter(models.User.user_id == user_id)
        .first()
    )
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )

    return user


@router.delete(
    "/",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete my profile",
    responses={
        204: {"description": "Deleted"},
        401: ERROR_401,
        404: ERROR_404,
        422: {"description": "Validation error"},
        500: ERROR_500,
    },
)
def delete_profile(
    user_id: int = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    user = (
        db.query(models.User)
        .filter(models.User.user_id == user_id)
        .first()
    )
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )

    db.delete(user)
    db.commit()
    # 204 NO CONTENT – ne vračamo nič v body-ju
    return
