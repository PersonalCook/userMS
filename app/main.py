from fastapi import FastAPI, Request
from .database import Base, engine
from . import models
from .routers import auth, profile, users
from fastapi.security import HTTPBearer
from fastapi.middleware.cors import CORSMiddleware
from prometheus_client import generate_latest, CONTENT_TYPE_LATEST
from starlette.responses import Response
import time
from .metrics import (
    num_requests,
    num_errors,
    request_latency,
    requests_in_progress
)

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

@app.middleware("http")
async def metrics_middleware(request: Request, call_next):
    method = request.method
    endpoint = request.url.path

    requests_in_progress.inc()
    start_time = time.time()

    try:
        response = await call_next(request)
        status_code = response.status_code
        duration = time.time() - start_time

        num_requests.labels(method=method, endpoint=endpoint, status_code=status_code).inc()

        if status_code >= 400:
            num_errors.labels(method=method, endpoint=endpoint, status_code=status_code).inc()

        request_latency.labels(method=method, endpoint=endpoint).observe(duration)

        return response
    finally:
        requests_in_progress.dec()

@app.get("/metrics")
def metrics():
    return Response(generate_latest(), media_type=CONTENT_TYPE_LATEST)
 

@app.get("/")
def root():
    return {"msg": "User Service running!"}


@app.get("/health")
def health():
    return {"status": "ok"}

