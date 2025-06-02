import logging
import os

from pydantic_settings import BaseSettings

from src.core.constants import Defaults, EnvVars, Logging
from src.core.messages import LogMessages
from src.core.secrets import load_secrets_from_gsm, should_use_gsm

logger = logging.getLogger(__name__)


class Settings(BaseSettings):
    """Application settings"""

    # Base
    APP_NAME: str = Defaults.APP_NAME
    API_V1_STR: str = Defaults.API_V1_STR

    # App metadata
    APP_VERSION: str = Defaults.APP_VERSION
    APP_DESCRIPTION: str = Defaults.APP_DESCRIPTION

    # CORS settings
    CORS_ORIGINS: list[str] = Defaults.CORS_ORIGINS

    # Supabase
    SUPABASE_URL: str
    SUPABASE_KEY: str
    SUPABASE_JWT_SECRET: str

    # Application settings
    DEBUG: bool = Defaults.DEBUG
    TESTING: bool = Defaults.TESTING
    LOG_LEVEL: str = Defaults.LOG_LEVEL
    USE_GSM: bool = Defaults.USE_GSM

    model_config = {"env_file": ".env", "case_sensitive": True}


def get_settings():
    """
    Get application settings with Google Secret Manager integration

    In production, this will fetch secrets from GSM using the VM's service account.
    In development/testing, it will use environment variables or .env file.
    """
    # Check if we should use GSM before loading settings
    use_gsm = should_use_gsm()
    is_testing = should_use_testing()
    
    # For testing/development, use environment variables
    if is_testing or not use_gsm:
        logger.info(LogMessages.LOADING_FROM_ENV)
        return Settings()

    # For production, load secrets from GSM
    try:
        logger.info(LogMessages.LOADING_FROM_GSM)
        load_secrets_from_gsm()
        return Settings()
    except Exception as e:
        logger.error(LogMessages.GSM_ERROR_FALLBACK.format(error=e))
        logger.warning(LogMessages.GSM_FALLBACK_WARNING)
        return Settings()


def should_use_testing() -> bool:
    """Check if testing mode is enabled"""
    return os.environ.get(EnvVars.TESTING, "").lower() in ("true", "1", "t") 

# Load settings using the function
settings = get_settings()

# Set log level
LOG_LEVEL = Logging.LEVELS.get(settings.LOG_LEVEL.upper(), Logging.DEFAULT_LEVEL)
