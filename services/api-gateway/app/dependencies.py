"""Dependency injection for API Gateway — JWT auth."""

from fastapi import HTTPException, status, Depends, Request
from typing import Annotated
import httpx
from app.middleware.auth.enums import UserRole
from aegis_shared.schemas.auth import AuthUser
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from app.grpc.clients.transaction_client import TransactionGRPCClient
from app.middleware.auth.cognito import verify_token

oauth2_scheme = HTTPBearer(auto_error=False)

async def get_current_user(
    token: HTTPAuthorizationCredentials = Depends(oauth2_scheme)
) -> AuthUser:
    """Extract and verify JWT token, returning an AuthUser."""
    
    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated"
        )

    
    claims = verify_token(token.credentials)

    groups = claims.get("cognito:groups", [])
    # Support both standard Cognito prefix and the cleaner Lambda-enriched format
    tenant_id = claims.get("tenant_id") or claims.get("custom:tenant_id")

    # Strictly rely on token claims for multi-tenancy
    if not tenant_id:
        from aegis_shared.utils.logging import get_logger
        logger = get_logger("dependencies")
        logger.warning(f"tenant_id missing from token for user {claims['sub']}. Was the 'profile' scope requested during login?")
        tenant_id = claims["sub"]

    if "admin" in groups:
        tenant_id = "admin"

    return AuthUser(
        sub=claims["sub"],
        email=claims.get("email") or "",
        name=claims.get("name") or claims.get("email", ""),
        roles=groups,
        tenant_id=tenant_id,
    )


def require_role(role: UserRole): # Change to Enum best approach
    """Factory for role-based route guards."""
    
    def _check_role(user: Annotated[AuthUser, Depends(get_current_user)]) -> AuthUser:
        if role not in user.roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access Denied"
            )
        return user
    return _check_role


def require_admin_role(user: Annotated[AuthUser, Depends(get_current_user)]) -> AuthUser:
    """Extract and verify JWT token, returning an AuthUser."""

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authenticated"
        )

    if UserRole.ADMIN not in user.roles:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Access Denied - Admin role required"
        )

    return user


def require_analyst_role(user: Annotated[AuthUser, Depends(get_current_user)]) -> AuthUser:
    """Extract and verify JWT token, returning an AuthUser."""

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authenticated"
        )

    if UserRole.ANALYST not in user.roles:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Access Denied - Analyst role required"
        )

    return user


def get_transaction_client(request: Request) -> TransactionGRPCClient:
    """
    Retrieve the gRPC client from the application state.
    """
    client = getattr(request.app.state, "transaction_client", None)
    if client is None:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Transaction service client not initialized"
        )
    return client

def get_http_client(request: Request) -> httpx.AsyncClient:
    """
    Retrieve the HTTP client from the application state.
    """
    client = getattr(request.app.state, "http_client", None)
    if client is None:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="HTTP client not initialized"
        )
    return client


def get_sqs_session(request: Request):
    """Retrieve the shared aioboto3 session from application state."""
    session = getattr(request.app.state, "boto_session", None)
    if session is None:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="SQS session not initialized",
        )
    return session