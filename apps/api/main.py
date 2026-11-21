from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from audit import audit
from auth import router as auth_router
from config import settings
from rate_limit import RateLimitMiddleware

app = FastAPI(title=settings.app_name)

app.add_middleware(RateLimitMiddleware)
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router)


@app.get("/health")
def health():
    audit("health_check")
    return {"status": "ok", "environment": settings.environment}
