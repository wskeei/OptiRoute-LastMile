from __future__ import annotations

import argparse
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable


HAN_PATTERN = re.compile(r"[\u3400-\u4DBF\u4E00-\u9FFF\uF900-\uFAFF]")


@dataclass(frozen=True)
class FileSummary:
    path: Path
    chinese_chars: int


def count_chinese_chars(text: str) -> int:
    return len(HAN_PATTERN.findall(text))


def collect_markdown_files(paths: Iterable[Path]) -> list[Path]:
    markdown_files: set[Path] = set()

    for path in paths:
        resolved = Path(path)
        if resolved.is_dir():
            markdown_files.update(file for file in resolved.rglob("*.md") if file.is_file())
        elif resolved.is_file() and resolved.suffix.lower() == ".md":
            markdown_files.add(resolved)

    return sorted(markdown_files)


def summarize_paths(paths: Iterable[Path]) -> tuple[list[FileSummary], int]:
    files = collect_markdown_files(paths)
    summaries: list[FileSummary] = []

    for file_path in files:
        text = file_path.read_text(encoding="utf-8")
        summaries.append(FileSummary(path=file_path, chinese_chars=count_chinese_chars(text)))

    total = sum(item.chinese_chars for item in summaries)
    return summaries, total


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Count Chinese characters in Markdown files.")
    parser.add_argument(
        "paths",
        nargs="*",
        default=["."],
        help="Markdown files or directories to scan. Defaults to current directory.",
    )
    return parser


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()
    raw_paths = [Path(path) for path in args.paths]

    summaries, total = summarize_paths(raw_paths)

    if not summaries:
        print("No Markdown files found.")
        return 1

    for summary in summaries:
        print(f"{summary.chinese_chars:>6}  {summary.path}")

    print(f"{'-' * 40}")
    print(f"{total:>6}  TOTAL")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
