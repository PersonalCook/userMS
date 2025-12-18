from fastapi import APIRouter, Depends, HTTPException, Header, status
from sqlalchemy.orm import Session

from ..database import SessionLocal
from ..utils.auth import decode_jwt
from .. import models, schemas

from fastapi import Security
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

security = HTTPBearer()

router = APIRouter(prefix="/profile", tags=["Profile"])


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

@router.get("/", response_model=schemas.UserProfile)
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


@router.delete("/", status_code=status.HTTP_204_NO_CONTENT)
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
