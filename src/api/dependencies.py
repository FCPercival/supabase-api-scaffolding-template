from fastapi import Depends
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from src.api.utils.auth_helpers import validate_jwt_token, verify_supabase_session
from src.services.auth_service import AuthService

security = HTTPBearer()


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
) -> str:
    """
    Verify JWT token and return user_id
    """
    token = credentials.credentials
    user_id = validate_jwt_token(token)
    verify_supabase_session(token)
    return user_id


def get_auth_service() -> AuthService:
    """Dependency for auth service"""
    return AuthService()
