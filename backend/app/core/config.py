from pathlib import Path
from typing import List, Optional

from pydantic import AnyHttpUrl, ValidationInfo, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

BACKEND_DIR = Path(__file__).resolve().parents[2]


def build_sqlite_database_uri(database_file: str) -> str:
    database_path = Path(database_file).expanduser()
    if not database_path.is_absolute():
        database_path = BACKEND_DIR / database_path
    return f"sqlite:///{database_path.resolve().as_posix()}"


class Settings(BaseSettings):
    PROJECT_NAME: str = "快递末端配送系统"
    API_V1_STR: str = "/api/v1"
    
    # SQLite 数据库配置
    SQLITE_DB_FILE: str = "sql_app.db"
    SQLALCHEMY_DATABASE_URI: Optional[str] = None

    @field_validator("SQLALCHEMY_DATABASE_URI", mode="before")
    @classmethod
    def assemble_db_connection(cls, v: Optional[str], info: ValidationInfo) -> str:
        if isinstance(v, str) and v:
            return v
        return build_sqlite_database_uri(info.data.get("SQLITE_DB_FILE", "sql_app.db"))

    # Celery 配置
    # 默认尝试使用 Redis，如果失败可以切换到 SQLAlchemy/SQLite
    CELERY_BROKER_URL: str = "redis://localhost:6379/0"
    CELERY_RESULT_BACKEND: str = "redis://localhost:6379/0"
    
    # 安全配置
    SECRET_KEY: str = "your-secret-key-here-for-dev"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 8  # 8 days
    
    # 跨域配置
    BACKEND_CORS_ORIGINS: List[AnyHttpUrl] = []

    model_config = SettingsConfigDict(
        case_sensitive=True,
        env_file=str(BACKEND_DIR / ".env"),
    )

settings = Settings()
