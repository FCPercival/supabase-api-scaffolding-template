from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPBearer

from src.api.dependencies import get_auth_service, get_current_user
from src.api.utils.auth_helpers import handle_auth_error, format_auth_response
from src.core.messages import ErrorMessages, SuccessMessages
from src.models.auth import (
    AuthResponse,
    PasswordResetRequest,
    UserCreate,
    UserLogin,
)
from src.services.auth_service import AuthService

router = APIRouter()
security = HTTPBearer()


@router.post("/signup", response_model=AuthResponse, status_code=status.HTTP_201_CREATED)
async def signup(
    user_data: UserCreate,
    auth_service: AuthService = Depends(get_auth_service),
):
    """Register a new user account"""
    try:
        result = await auth_service.signup(user_data)
        return format_auth_response(result)
    except Exception as e:
        raise handle_auth_error(e) from e


@router.post("/login", response_model=AuthResponse)
async def login(
    user_data: UserLogin,
    auth_service: AuthService = Depends(get_auth_service),
):
    """Log in with email and password"""
    try:
        result = await auth_service.login(user_data)
        return format_auth_response(result)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=ErrorMessages.INVALID_CREDENTIALS,
        ) from None
    except Exception as e:
        raise handle_auth_error(e) from e


@router.post("/logout", status_code=status.HTTP_200_OK)
async def logout(
    token: HTTPBearer = Depends(security),
    auth_service: AuthService = Depends(get_auth_service),
):
    """Log out the current user"""
    try:
        if not token.credentials:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=ErrorMessages.INVALID_TOKEN)

        success = await auth_service.logout(token.credentials)
        if not success:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=ErrorMessages.LOGOUT_FAILED,
            )

        return {"message": SuccessMessages.LOGOUT_SUCCESS}
    except Exception as e:
        raise handle_auth_error(e) from e


@router.post("/reset-password", status_code=status.HTTP_200_OK)
async def reset_password(
    request: PasswordResetRequest,
    auth_service: AuthService = Depends(get_auth_service),
):
    """Request a password reset"""
    try:
        await auth_service.request_password_reset(request.email)
        return {"message": SuccessMessages.PASSWORD_RESET_SENT}
    except Exception as e:
        raise handle_auth_error(e) from e


@router.get("/session-check", status_code=status.HTTP_200_OK)
async def session_check(
    user_id: str = Depends(get_current_user)
):
    """Check if the current session is valid"""
    # If we reach here, JWT validation passed = session is valid
    return {"valid": True, "user_id": user_id}


# TODO: Add OAuth endpoints for production-ready social authentication:
# - GET /oauth/{provider} - Initiate OAuth login
# - GET /oauth/{provider}/callback - Handle OAuth callback
# - Support for Google, GitHub, and other providers via Supabase Auth
