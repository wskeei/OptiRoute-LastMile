from pathlib import Path

from app.core.config import BACKEND_DIR, build_sqlite_database_uri


def test_build_sqlite_database_uri_anchors_relative_paths_to_backend_dir():
    uri = build_sqlite_database_uri("sql_app.db")

    assert uri == f"sqlite:///{(BACKEND_DIR / 'sql_app.db').resolve().as_posix()}"


def test_build_sqlite_database_uri_preserves_absolute_paths():
    custom_db = Path("/tmp/opti-route-test.db")

    uri = build_sqlite_database_uri(str(custom_db))

    assert uri == f"sqlite:///{custom_db.as_posix()}"
