import logging

from fastapi import HTTPException, status
from jose import JWTError, jwt

from src.core.config import settings
from src.core.constants import Supabase
from src.core.messages import ErrorMessages, LogMessages
from src.core.supabase_client import get_supabase_client

logger = logging.getLogger(__name__)


def validate_jwt_token(token: str) -> str:
    """
    Extract and validate JWT token, return user_id
    
    Args:
        token: JWT token string
        
    Returns:
        user_id extracted from token
        
    Raises:
        HTTPException: If token is invalid
    """
    try:
        # Decode and verify token
        payload = jwt.decode(
            token,
            settings.SUPABASE_JWT_SECRET,
            algorithms=["HS256"],
            options={
                "verify_signature": True,
                "verify_exp": True,
                "verify_aud": True,
                "require_exp": True,
            },
            audience="authenticated",
        )

        # Extract user_id from sub claim
        user_id = payload.get("sub")
        if not user_id:
            logger.warning(LogMessages.JWT_MISSING_SUB)
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=ErrorMessages.INVALID_TOKEN_MISSING_USER,
            )

        return user_id

    except JWTError as err:
        logger.warning(LogMessages.JWT_VALIDATION_FAILED.format(error=err))
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=ErrorMessages.INVALID_TOKEN,
        ) from err


def verify_supabase_session(token: str) -> None:
    """
    Verify token against Supabase to ensure session is still active
    
    Args:
        token: JWT token string
        
    Raises:
        HTTPException: If session is invalid
    """
    try:
        supabase = get_supabase_client()
        supabase.auth.get_user(token)
    except Exception as session_err:
        logger.warning(LogMessages.SESSION_VALIDATION_FAILED.format(error=session_err))
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=ErrorMessages.SESSION_EXPIRED,
        ) from session_err


def handle_auth_error(e: Exception) -> HTTPException:
    """
    Convert auth errors to appropriate HTTP exceptions
    
    Args:
        e: Exception from auth operation
        
    Returns:
        HTTPException with appropriate status code and message
    """
    if isinstance(e, ValueError):
        return HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )
    
    return HTTPException(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        detail=f"Authentication error: {e!s}",
    )


def format_auth_response(result: dict) -> dict:
    """
    Format Supabase auth result into standardized response
    
    Args:
        result: Raw result from Supabase auth operation
        
    Returns:
        Formatted auth response with user and token data
    """
    # Use pre-extracted full_name if available, otherwise extract safely
    full_name = result["user"].get("full_name", "")
    if not full_name:
        # Fallback: safely handle user_metadata which might be string or dict for OAuth users
        user_metadata = result["user"]["user_metadata"]
        if isinstance(user_metadata, dict):
            full_name = user_metadata.get(Supabase.FULL_NAME_FIELD, "")
    
    user_data = {
        "id": result["user"]["id"],
        "email": result["user"]["email"],
        "full_name": full_name,
        "created_at": result["user"]["created_at"],
    }

    # Handle optional session data
    token_data = {
        "access_token": "",
        "refresh_token": "",
        "token_type": "bearer",
    }

    # Safely handle session data which might be dict or other type
    session_data = result.get("session")
    if session_data and isinstance(session_data, dict) and session_data.get("access_token"):
        token_data = {
            "access_token": session_data["access_token"],
            "refresh_token": session_data["refresh_token"],
            "token_type": "bearer",
        }

    return {
        "user": user_data,
        "token": token_data,
    } 