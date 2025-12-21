from fastapi import FastAPI
from .database import Base, engine
from . import models
from .routers import auth, profile, users
from fastapi.security import HTTPBearer
from fastapi.middleware.cors import CORSMiddleware

auth_scheme = HTTPBearer()

app = FastAPI(title="User Service")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],     
    allow_credentials=True,
    allow_methods=["*"],      
    allow_headers=["*"],      
)

models.Base.metadata.create_all(bind=engine)
app.include_router(auth.router)
app.include_router(profile.router)
app.include_router(users.router)

@app.get("/")
def root():
    return {"msg": "User Service running!"}


@app.get("/health")
def health():
    return {"status": "ok"}

