import logging

from src.core.constants import OAuth, Supabase
from src.core.messages import ErrorMessages, LogMessages
from src.core.supabase_client import get_supabase_client
from src.models.auth import UserCreate, UserLogin

class AuthService:
    """Service for authentication operations"""

    def __init__(self):
        self.client = get_supabase_client()

    async def signup(self, user_data: UserCreate) -> dict:
        """Register a new user in Supabase Auth"""
        try:
            auth_response = self.client.auth.sign_up(
                {
                    "email": user_data.email,
                    "password": user_data.password,
                    "options": {
                        "data": {
                            Supabase.FULL_NAME_FIELD: user_data.full_name,
                        }
                    },
                }
            )

            if not hasattr(auth_response, "user") or not auth_response.user:
                raise ValueError(f"{ErrorMessages.REGISTRATION_FAILED}: Could not create user")

            logging.info(LogMessages.USER_CREATED.format(user_id=auth_response.user.id))

            return self._format_auth_response(auth_response)

        except Exception as e:
            logging.error(f"Signup error: {e!s}")
            raise ValueError(f"{ErrorMessages.REGISTRATION_FAILED}: {e!s}") from e

    async def login(self, user_data: UserLogin) -> dict:
        """Authenticate a user with email and password"""
        try:
            auth_response = self.client.auth.sign_in_with_password(
                {
                    "email": user_data.email,
                    "password": user_data.password,
                }
            )

            if (
                not hasattr(auth_response, "user")
                or not auth_response.user
                or not auth_response.session
            ):
                raise ValueError(f"{ErrorMessages.AUTHENTICATION_FAILED}: Invalid credentials")

            logging.info(LogMessages.USER_LOGGED_IN.format(user_id=auth_response.user.id))
            return self._format_auth_response(auth_response)

        except Exception as e:
            logging.error(f"Login error: {e!s}")
            raise ValueError(f"{ErrorMessages.AUTHENTICATION_FAILED}: {e!s}") from e

    async def logout(self, token: str) -> bool:
        """Logout a user session"""
        try:
            self.client.auth.sign_out()
            logging.info(LogMessages.USER_LOGGED_OUT)
            return True
        except Exception as e:
            logging.error(f"Logout error: {e!s}")
            return False

    async def request_password_reset(self, email: str) -> bool:
        """Send password reset email"""
        try:
            self.client.auth.reset_password_for_email(email)
            return True
        except Exception as e:
            logging.error(f"Password reset error: {e!s}")
            return False

    async def get_user(self, user_id: str) -> dict | None:
        """Get user data from Supabase Auth"""
        try:
            user_response = self.client.auth.get_user()
            if not user_response or not user_response.user:
                return None

            user = user_response.user
            
            # Safely handle user_metadata which might be string or dict
            user_metadata = user.user_metadata
            if isinstance(user_metadata, dict):
                full_name = user_metadata.get(Supabase.FULL_NAME_FIELD, "")
            else:
                # If user_metadata is not a dict, default to empty string
                full_name = ""
                
            return {
                "id": user.id,
                "email": user.email,
                "full_name": full_name,
            }
        except Exception as e:
            logging.error(f"Get user error: {e!s}")
            return None

    async def oauth_login(self, provider: str, redirect_url: str) -> dict:
        """Initiate OAuth login flow - let Supabase handle PKCE"""
        if provider != OAuth.GOOGLE:
            raise ValueError(f"Unsupported provider: {provider}")
        
        # Let Supabase handle PKCE internally - just pass the redirect URL
        auth_response = self.client.auth.sign_in_with_oauth({
            "provider": "google",
            "options": {
                "redirect_to": redirect_url
            }
        })
        
        return {
            "auth_url": auth_response.url
        }

    async def handle_oauth_callback(self, provider: str, code: str, redirect_url: str) -> dict:
        """Handle OAuth callback - let Supabase handle PKCE code exchange"""
        if provider != OAuth.GOOGLE:
            raise ValueError(f"Unsupported provider: {provider}")
        
        try:
            # Pass proper CodeExchangeParams format - Supabase will get code_verifier from storage
            code_exchange_params = {
                "auth_code": code,
                "redirect_to": redirect_url
            }
            
            auth_response = self.client.auth.exchange_code_for_session(code_exchange_params)
            
            if not auth_response.user or not auth_response.session:
                raise ValueError("Failed to exchange code for session")
            
            logging.info(LogMessages.USER_LOGGED_IN.format(user_id=auth_response.user.id))
            return self._format_auth_response(auth_response)
            
        except Exception as e:
            logging.error(f"OAuth callback error: {e!s}")
            raise ValueError(f"OAuth authentication failed: {e!s}") from e

    def _format_auth_response(self, auth_response) -> dict:
        """Format Supabase auth response into standardized format"""
        # Safely extract user metadata - handle both dict and string cases
        user_metadata = auth_response.user.user_metadata
        if isinstance(user_metadata, str):
            # If user_metadata is a string, create empty dict and log this case
            logging.warning(f"User metadata is string instead of dict: {user_metadata}")
            user_metadata = {}
        elif user_metadata is None:
            user_metadata = {}
        
        # Extract full_name from user_metadata if it's a dict
        full_name = ""
        if isinstance(user_metadata, dict):
            full_name = user_metadata.get(Supabase.FULL_NAME_FIELD, "")
        
        user_dict = {
            "id": auth_response.user.id,
            "email": auth_response.user.email,
            "user_metadata": user_metadata,
            "full_name": full_name,
            "created_at": auth_response.user.created_at,
        }

        session_dict = {}
        if auth_response.session and hasattr(auth_response.session, 'access_token'):
            session_dict = {
                "access_token": auth_response.session.access_token,
                "refresh_token": auth_response.session.refresh_token,
            }

        return {
            "user": user_dict,
            "session": session_dict,
        }
