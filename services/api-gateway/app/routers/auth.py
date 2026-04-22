""" Auth api routes """


import httpx
from app.config import settings
from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException, Query, status
from aegis_shared.schemas.auth import TokenResponse
from app.dependencies import get_current_user, get_http_client, AuthUser
from fastapi.responses import RedirectResponse


router = APIRouter(prefix="/auth", tags=["Auth"])

@router.get("/login")
def login():
    """Redirect user to Cognito Hosted UI"""
    
    return RedirectResponse(settings.LOGIN_URL)

@router.get("/callback", response_model=TokenResponse)
async def callback(code: Annotated[str, Query()], client: Annotated[httpx.AsyncClient, Depends(get_http_client)]):

    
    response = await client.post(
        f"{settings.COGNITO_DOMAIN}/oauth2/token",
        data={
            "grant_type": "authorization_code",
            "client_id": settings.COGNITO_APP_CLIENT_ID,
            "client_secret": settings.COGNITO_APP_CLIENT_SECRET,
            "code": code,
            "redirect_uri": settings.COGNITO_REDIRECT_URI
        },
        headers={"Content-Type": "application/x-www-form-urlencoded"},
    )

    if response.status_code != 200:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Bad Request"
        )
        
    tokens = response.json()

    return TokenResponse(
        access_token=tokens["access_token"],
        id_token=tokens["id_token"],
        refresh_token=tokens.get("refresh_token"),
        token_type="Bearer",
    )
    
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

oauth2_scheme = HTTPBearer(auto_error=False)

@router.get("/logout")
async def logout(
    client: Annotated[httpx.AsyncClient, Depends(get_http_client)],
    token: Annotated[HTTPAuthorizationCredentials | None, Depends(oauth2_scheme)] = None
):
    """
    1. Revoke the token with Cognito (if provided)
    2. Redirect to Cognito Hosted UI logout to clear cookies
    """

    if token:
        # Attempt to revoke the token on AWS side
        try:
            await client.post(
                f"{settings.COGNITO_DOMAIN}/oauth2/revoke",
                data={
                    "token": token.credentials,
                    "client_id": settings.COGNITO_APP_CLIENT_ID,
                    "client_secret": settings.COGNITO_APP_CLIENT_SECRET,
                },
                headers={"Content-Type": "application/x-www-form-urlencoded"},
            )
        except Exception:
            # If revocation fails (e.g. token already dead), we still want to redirect
            pass

    url = (
        f"{settings.COGNITO_DOMAIN}/logout"
        f"?client_id={settings.COGNITO_APP_CLIENT_ID}"
        f"&logout_uri=http://localhost:8000/"
    )
    
    return RedirectResponse(url)


