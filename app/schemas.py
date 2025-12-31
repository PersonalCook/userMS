from pydantic import BaseModel, EmailStr, model_validator
from datetime import date

#input 

class UserCreate(BaseModel):
    email: EmailStr
    password: str
    username: str
    public_name: str | None = None
    birthdate: date | None = None


    @model_validator(mode="after")
    def set_public_name(self):
        if self.public_name is None:
            self.public_name = self.username
        return self


class UserLogin(BaseModel):
    email: EmailStr
    password: str


#output

class UserProfile(BaseModel):
    user_id: int
    email: EmailStr
    username: str
    public_name: str
    birthdate: date | None

    class Config:
        orm_mode = True  # Omogoči branje SQLAlchemy objektov


class UserUpdate(BaseModel):
    email: EmailStr | None = None
    username: str | None = None
    public_name: str | None = None
    birthdate: date | None = None


class ErrorResponse(BaseModel):
    detail: str


class RootResponse(BaseModel):
    msg: str


class HealthResponse(BaseModel):
    status: str


class RegisterResponse(BaseModel):
    msg: str


class LoginResponse(BaseModel):
    access_token: str
    user_id: int


class UserSummary(BaseModel):
    user_id: int
    username: str
    public_name: str | None
    email: EmailStr
