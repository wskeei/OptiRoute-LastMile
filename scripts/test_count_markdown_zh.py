import tempfile
import unittest
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parent))

from count_markdown_zh import collect_markdown_files, count_chinese_chars, summarize_paths


class CountChineseCharsTests(unittest.TestCase):
    def test_count_chinese_chars_counts_only_han_characters(self) -> None:
        text = "# 标题\nHello，世界123\nK-Means 聚类与GA\n"
        self.assertEqual(count_chinese_chars(text), 7)

    def test_collect_markdown_files_returns_markdown_files_from_directory(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            root = Path(tmp_dir)
            (root / "a.md").write_text("中文", encoding="utf-8")
            (root / "b.txt").write_text("中文", encoding="utf-8")
            (root / "nested").mkdir()
            (root / "nested" / "c.md").write_text("更多中文", encoding="utf-8")

            files = collect_markdown_files([root])

            self.assertEqual(files, [root / "a.md", root / "nested" / "c.md"])

    def test_summarize_paths_aggregates_multiple_markdown_files(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            root = Path(tmp_dir)
            first = root / "first.md"
            second = root / "second.md"
            first.write_text("第一章：系统设计", encoding="utf-8")
            second.write_text("第二章：算法实现", encoding="utf-8")

            summaries, total = summarize_paths([first, second])

            self.assertEqual(len(summaries), 2)
            self.assertEqual(summaries[0].chinese_chars, 7)
            self.assertEqual(summaries[1].chinese_chars, 7)
            self.assertEqual(total, 14)


if __name__ == "__main__":
    unittest.main()
