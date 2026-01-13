from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker, declarative_base
from app.core.config import settings

# 对于 SQLite, check_same_thread=False 是必须的
# timeout: 30s (默认为5s) 以减少 "database is locked" 错误
engine = create_engine(
    settings.SQLALCHEMY_DATABASE_URI, 
    connect_args={
        "check_same_thread": False,
        "timeout": 30
    }
)

# Enable Write-Ahead Logging (WAL) for better concurrency
# This allows readers to not block writers and vice versa
@event.listens_for(engine, "connect")
def set_sqlite_pragma(dbapi_connection, connection_record):
    cursor = dbapi_connection.cursor()
    cursor.execute("PRAGMA journal_mode=WAL")
    cursor.execute("PRAGMA synchronous=NORMAL")
    cursor.close()

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
