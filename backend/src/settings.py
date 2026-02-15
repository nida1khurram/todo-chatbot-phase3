import logging
from pydantic_settings import BaseSettings
from typing import Optional
import os

# Set up logging
logger = logging.getLogger(__name__)

class Settings(BaseSettings):
    # Database settings
    database_url: Optional[str] = os.getenv("DATABASE_URL")
    db_user: str = os.getenv("DB_USER", "postgres")
    db_password: str = os.getenv("DB_PASSWORD", "")
    db_host: str = os.getenv("DB_HOST", "localhost")
    db_port: str = os.getenv("DB_PORT", "5432")
    db_name: str = os.getenv("DB_NAME", "todo_app")
    db_echo: bool = os.getenv("DB_ECHO", "False").lower() == "true"

    # JWT settings
    secret_key: str = os.getenv("SECRET_KEY", "your-super-secret-key-change-in-production")
    algorithm: str = os.getenv("ALGORITHM", "HS256")
    access_token_expire_minutes: int = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30"))

    # Better Auth settings
    better_auth_secret: str = os.getenv("BETTER_AUTH_SECRET", "")
    better_auth_url: str = os.getenv("BETTER_AUTH_URL", "http://localhost:3000")

    # Kafka settings
    kafka_bootstrap_servers: str = os.getenv("KAFKA_BOOTSTRAP_SERVERS", "localhost:9092")
    kafka_security_protocol: str = os.getenv("KAFKA_SECURITY_PROTOCOL", "PLAINTEXT")
    kafka_sasl_mechanism: str = os.getenv("KAFKA_SASL_MECHANISM", "")
    kafka_sasl_plain_username: str = os.getenv("KAFKA_SASL_PLAIN_USERNAME", "")
    kafka_sasl_plain_password: str = os.getenv("KAFKA_SASL_PLAIN_PASSWORD", "")

    class Config:
        env_file = ".env"
        extra = "ignore"  # Ignore extra fields in .env that don't match class attributes

# Initialize settings and log configuration
settings = Settings()
logger.info("Application settings loaded successfully")
logger.info(f"Database host: {settings.db_host}")
logger.info(f"JWT algorithm: {settings.algorithm}")
logger.info(f"Access token expiration: {settings.access_token_expire_minutes} minutes")