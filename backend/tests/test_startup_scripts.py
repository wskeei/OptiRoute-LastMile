from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]
SCRIPTS_DIR = REPO_ROOT / "scripts"


def read_script(name: str) -> str:
    return (SCRIPTS_DIR / name).read_text(encoding="utf-8")


def test_dev_up_script_exists_and_runs_app_stack() -> None:
    script_path = SCRIPTS_DIR / "dev-up.sh"

    assert script_path.exists()

    content = read_script("dev-up.sh")
    assert 'source "${SCRIPT_DIR}/_common.sh"' in content
    assert "reset_backend_database" in content
    assert "run_backend_migrations" in content
    assert "seed_backend_data" in content
    assert "start_backend" in content
    assert "start_frontend" in content


def test_bootstrap_script_exists_and_installs_then_starts() -> None:
    script_path = SCRIPTS_DIR / "bootstrap-and-up.sh"

    assert script_path.exists()

    content = read_script("bootstrap-and-up.sh")
    assert 'source "${SCRIPT_DIR}/_common.sh"' in content
    assert "install_backend_dependencies" in content
    assert "install_frontend_dependencies" in content
    assert "reset_backend_database" in content
    assert "start_backend" in content
    assert "start_frontend" in content


def test_common_script_contains_shared_helpers() -> None:
    script_path = SCRIPTS_DIR / "_common.sh"

    assert script_path.exists()

    content = read_script("_common.sh")
    assert "require_command" in content
    assert "start_backend" in content
    assert "start_frontend" in content
    assert "cleanup" in content
    assert "uv run alembic upgrade head" in content
    assert "uv run python seed_shanghai_data.py" in content
    assert "uv sync" in content
    assert "npm install" in content
