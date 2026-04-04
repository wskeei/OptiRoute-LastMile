import os
import sys
from collections.abc import Sequence


def build_pytest_command(args: Sequence[str] | None = None) -> list[str]:
    return [sys.executable, "-m", "pytest", *(args if args is not None else sys.argv[1:])]


def main(args: Sequence[str] | None = None) -> None:
    os.execv(sys.executable, build_pytest_command(args))


if __name__ == "__main__":
    main()
