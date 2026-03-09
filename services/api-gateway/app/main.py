"""AegisRisk API Gateway — FastAPI application entrypoint."""

from contextlib import asynccontextmanager

from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.middleware.correlation import CorrelationIdMiddleware
from aegis_shared.utils.logging import setup_logger


from app.routers.auth import router as auth_router
from app.dependencies import get_current_user, require_role, AuthUser

logger = setup_logger("api-gateway", settings.LOG_LEVEL)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan handler."""
    logger.info("api_gateway_starting", port=settings.API_GATEWAY_PORT)
    yield
    logger.info("api_gateway_shutting_down")


app = FastAPI(
    title="AegisRisk API Gateway",
    description="Real-Time Distributed Fraud Detection Platform",
    version="1.0.0",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
)

# Middleware
app.add_middleware(CorrelationIdMiddleware)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router)


# ── Protected route examples ──────────────────────────────

@app.get("/me")
def get_me(user: AuthUser = Depends(get_current_user)):
    """Any authenticated user."""
    return {"sub": user.sub, "email": user.email, "name": user.name}


@app.get("/admin/dashboard")
def admin_only(user: AuthUser = Depends(require_role("admin"))):
    """Only users in the Cognito 'admin' group."""
    return {"message": f"Welcome admin {user.email}"}


@app.get("/health")
def health():
    return {"status": "ok"}

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=settings.API_GATEWAY_PORT,
        reload=True,
    )
