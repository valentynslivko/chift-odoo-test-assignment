from functools import lru_cache
from typing import Optional, Self

from pydantic import Field, field_validator, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore",
    )

    SQLALCHEMY_ASYNC_DATABASE_URI: Optional[str] = None
    SQLALCHEMY_ENABLE_ECHO: Optional[bool] = False
    POSTGRES_HOST: str = Field(default="postgres")
    POSTGRES_USER: str = Field(default="postgres")
    POSTGRES_PASSWORD: str = Field(default="postgres")
    POSTGRES_DB: str = Field(default="postgres")
    POSTGRES_PORT: str = Field(default="5432")

    DEBUG: bool = Field(False)

    REDIS_BROKER_URI: str = Field("redis://redis:6379/0")
    REDIS_BACKEND_URI: str = Field("redis://redis:6379/1")
    REDIS_CACHE_URI: str = Field("redis://redis:6379/2")
    BACKEND_CORS_ORIGINS: Optional[str | list] = Field(default="[*]")

    ODOO_API_KEY: str
    ODOO_HOST: str
    ODOO_PORT: str
    ODOO_DATABASE: str
    ODOO_USER: str

    @model_validator(mode="after")
    def build_database_uri(self) -> Self:
        if not self.SQLALCHEMY_ASYNC_DATABASE_URI:
            self.SQLALCHEMY_ASYNC_DATABASE_URI = (
                f"postgresql+asyncpg://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}"
                f"@{self.POSTGRES_HOST}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"
            )

        return self

    def construct_sync_uri(self) -> str:
        return (
            f"postgresql://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}"
            f"@{self.POSTGRES_HOST}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"
        )

    @field_validator("BACKEND_CORS_ORIGINS")
    def convert_cors_str_to_list(cls, env_var):
        """
        BACKEND_CORS_ORIGINS must be a list of strings in .env file, example:
        `BACKEND_CORS_ORIGINS=[*, http://localhost]`
        """
        if isinstance(env_var, str):
            if not env_var.startswith("[") and not env_var.endswith("]"):
                raise ValueError(
                    "BACKEND_CORS_ORIGINS environment variable must be spelled as python list, example: [*, http://localhost]"  # noqa: E501
                )
            cors_headers = (
                env_var.replace("[", "").replace("]", "").replace('"', "").split(",")
            )
            return cors_headers
        return env_var


@lru_cache
def get_settings():
    return Settings()
