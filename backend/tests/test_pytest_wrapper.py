import sys

import pytest

import backend_pytest


def test_build_pytest_command_uses_current_interpreter():
    assert backend_pytest.build_pytest_command(["-q", "tests/test_dispatch_api.py"]) == [
        sys.executable,
        "-m",
        "pytest",
        "-q",
        "tests/test_dispatch_api.py",
    ]


def test_main_execs_pytest_module(monkeypatch: pytest.MonkeyPatch):
    captured: dict[str, object] = {}

    def fake_execv(executable: str, argv: list[str]):
        captured["executable"] = executable
        captured["argv"] = argv

    monkeypatch.setattr(backend_pytest.os, "execv", fake_execv)

    backend_pytest.main(["-q"])

    assert captured == {
        "executable": sys.executable,
        "argv": [sys.executable, "-m", "pytest", "-q"],
    }
