from functools import lru_cache
from typing import List, Optional
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )


    AWS_ACCESS_KEY_ID: Optional[str] = None
    AWS_SECRET_ACCESS_KEY: Optional[str] = None
    AWS_REGION: Optional[str] = None
    AWS_S3_BUCKET: Optional[str] = None
    AWS_CLOUDFRONT_DOMAIN: Optional[str] = None

    # App
    APP_NAME: str = "OMNIA"
    APP_VERSION: str = "1.0.0"
    ENVIRONMENT: str = Field(default="development")  # development|test|production
    DEBUG: bool = Field(default=False)

    # Docs control (separate from DEBUG)
    ENABLE_DOCS: bool = Field(default=True)

    # Logging
    LOG_LEVEL: str = Field(default="INFO")
    LOG_FORMAT: str = Field(default="console")  # console|json

    # Server
    HOST: str = Field(default="0.0.0.0")
    PORT: int = Field(default=8003)

    # Kafka (used in lifespan extra)
    KAFKA_ENABLED: bool = Field(default=False)

    # CORS
    CORS_ORIGINS: str = Field(default="http://localhost:5173,http://127.0.0.1:5173,http://localhost:3000,http://127.0.0.1:3000,http://13.236.146.72:5173")
    CORS_ALLOW_CREDENTIALS: bool = Field(default=False)
    CORS_ALLOW_METHODS: List[str] = Field(default_factory=lambda: ["*"])
    CORS_ALLOW_HEADERS: List[str] = Field(default_factory=lambda: ["*"])

    @property
    def CORS_ORIGINS_LIST(self) -> List[str]:
        origins = [o.strip() for o in self.CORS_ORIGINS.split(",") if o.strip()]
        return origins or ["http://localhost:5173"]
    
    

    # Database
    POSTGRES_USER: Optional[str] = None
    POSTGRES_PASSWORD: Optional[str] = None
    POSTGRES_HOST: Optional[str] = None
    POSTGRES_PORT: int = 5432
    POSTGRES_DB: Optional[str] = None

    DATABASE_ECHO: bool = False
    DATABASE_POOL_SIZE: int = 10
    DATABASE_MAX_OVERFLOW: int = 5
    DATABASE_POOL_TIMEOUT: int = 30
    DATABASE_POOL_RECYCLE: int = 1800

    # Password Policy
    PASSWORD_MIN_LENGTH: int = Field(default=8, ge=6)
    PASSWORD_REQUIRE_UPPERCASE: bool = Field(default=True)
    PASSWORD_REQUIRE_LOWERCASE: bool = Field(default=True)
    PASSWORD_REQUIRE_DIGIT: bool = Field(default=True)
    PASSWORD_REQUIRE_SPECIAL: bool = Field(default=True)

    # JWT
    JWT_SECRET_KEY: str = Field(default="change-me")
    JWT_ALGORITHM: str = Field(default="HS256")
    JWT_ISSUER: str = Field(default="omnia-api")

    # Token Expiry
    ACCESS_TOKEN_EXPIRE_MINUTES: int = Field(default=60, ge=1)
    REFRESH_TOKEN_EXPIRE_DAYS: int = Field(default=7, ge=1)
    EMAIL_VERIFICATION_EXPIRE_HOURS: int = Field(default=24, ge=1)
    PASSWORD_RESET_EXPIRE_HOURS: int = Field(default=1, ge=1)

    # SMTP Settings
    SMTP_HOST: Optional[str] = None
    SMTP_PORT: int = 587
    SMTP_USER: Optional[str] = None
    SMTP_PASSWORD: Optional[str] = None
    SMTP_FROM: str = "noreply@omnia-app.me"
    SMTP_TLS: bool = True

    # QR Code
    QR_SECRET_KEY: str = Field(default="change-me-qr-secret")

    @property
    def DATABASE_URL(self) -> str:
        if self.ENVIRONMENT == "test":
            return "sqlite:///./test.db"

        if not all([self.POSTGRES_USER, self.POSTGRES_PASSWORD, self.POSTGRES_HOST, self.POSTGRES_DB]):
            raise RuntimeError("Postgres env vars missing (POSTGRES_USER/PASSWORD/HOST/DB)")

        return (
            f"postgresql://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}"
            f"@{self.POSTGRES_HOST}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"
        )

    # Backwards compatibility for your logging_config.py
    @property
    def DB_ECHO(self) -> bool:
        return self.DATABASE_ECHO


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
