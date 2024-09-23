from typing import Literal

from pydantic import BaseModel
from pydantic import PostgresDsn
from pydantic_settings import BaseSettings, SettingsConfigDict


LOG_DEFAULT_FORMAT = "[%(asctime)s.%(msecs)03d] %(module)10s:%(lineno)-3d %(levelname)-7s - %(message)s"

class RunConfig(BaseModel):
    host: str = "0.0.0.0"
    port: int = 8085
    title: str = "DevOps offer API"


class ApiPrefix(BaseModel):
    prefix_auth: str = "/api/auth"
    prefix_jwt: str = "/api/auth/jwt"
    prefix_users: str = "/api/users"
    prefix_category: str = "/api/categories"
    prefix_answer: str = "/api/answers"
    prefix_question: str = "/api/questions"


class DatabaseConfig(BaseModel):
    url: PostgresDsn
    echo: bool = False
    echo_pool: bool = False
    pool_size: int = 50
    max_overflow: int = 10

    naming_convention: dict[str, str] = {
        "ix": "ix_%(column_0_label)s",
        "uq": "uq_%(table_name)s_%(column_0_N_name)s",
        "ck": "ck_%(table_name)s_%(constraint_name)s",
        "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
        "pk": "pk_%(table_name)s",
    }

class AccessTokenConfig(BaseModel):
    secret: str
    lifetime_seconds: int = 3600

class LoggingConfig(BaseModel):
    log_level: Literal[
        'debug',
        'info',
        'warning',
        'error',
        'critical',
    ] = 'info'
    log_format: str = LOG_DEFAULT_FORMAT


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        case_sensitive=False,
        env_nested_delimiter="__",
    )
    run: RunConfig = RunConfig()
    api: ApiPrefix = ApiPrefix()
    logging: LoggingConfig = LoggingConfig()
    db: DatabaseConfig
    access_token: AccessTokenConfig


settings = Settings()
