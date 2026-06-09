"""Unit tests for fetch_pr_diff.parse_diff.

Run from the repo root with:  python3 -m unittest discover -s tests
"""
import os
import sys
import unittest

sys.path.insert(
    0,
    os.path.join(
        os.path.dirname(__file__), "..", ".agents", "skills", "review-pr", "scripts"
    ),
)
from fetch_pr_diff import parse_diff


class ParseDiffTest(unittest.TestCase):
    def test_line_numbering_added_removed_context(self):
        diff = (
            "diff --git a/src/app.py b/src/app.py\n"
            "index 1111111..2222222 100644\n"
            "--- a/src/app.py\n"
            "+++ b/src/app.py\n"
            "@@ -10,6 +10,7 @@ def foo():\n"
            "     a = 1\n"
            "     b = 2\n"
            "-    c = 3\n"
            "+    c = 4\n"
            "+    d = 5\n"
            "     return a\n"
        )
        lines = parse_diff(diff).splitlines()

        self.assertIn("## File: 'src/app.py'", lines)
        # metadata (index / --- / +++) is dropped
        self.assertFalse(any("index 1111111" in l for l in lines))
        self.assertFalse(any(l.startswith("--- ") or l.startswith("+++ ") for l in lines))
        # hunk header keeps the function context but not the line ranges
        self.assertIn("@@ ... @@ def foo():", lines)
        # context numbered with the new-file line (content keeps its own indent)
        self.assertIn("10      a = 1", lines)
        self.assertIn("11      b = 2", lines)
        # removed line uses the old-file number
        self.assertIn("12 -    c = 3", lines)
        # added lines use the new-file number and advance independently
        self.assertIn("12 +    c = 4", lines)
        self.assertIn("13 +    d = 5", lines)
        # context after the change: new-file line advanced to 14
        self.assertIn("14      return a", lines)

    def test_new_file_starts_at_one(self):
        diff = (
            "diff --git a/new.txt b/new.txt\n"
            "new file mode 100644\n"
            "index 0000000..3333333\n"
            "--- /dev/null\n"
            "+++ b/new.txt\n"
            "@@ -0,0 +1,2 @@\n"
            "+line one\n"
            "+line two\n"
        )
        lines = parse_diff(diff).splitlines()
        self.assertIn("1 +line one", lines)
        self.assertIn("2 +line two", lines)

    def test_no_newline_marker_is_skipped(self):
        diff = (
            "diff --git a/f.txt b/f.txt\n"
            "index 1..2 100644\n"
            "--- a/f.txt\n"
            "+++ b/f.txt\n"
            "@@ -1 +1 @@\n"
            "-foo\n"
            "\\ No newline at end of file\n"
            "+bar\n"
            "\\ No newline at end of file\n"
        )
        lines = parse_diff(diff).splitlines()
        # the "\ No newline" markers are dropped and do not shift numbering
        self.assertFalse(any("No newline" in l for l in lines))
        self.assertIn("1 -foo", lines)
        self.assertIn("1 +bar", lines)

    def test_multiple_files_reset_numbering(self):
        diff = (
            "diff --git a/one.py b/one.py\n"
            "index 1..2 100644\n"
            "--- a/one.py\n"
            "+++ b/one.py\n"
            "@@ -5,1 +5,2 @@\n"
            " keep\n"
            "+added in one\n"
            "diff --git a/two.py b/two.py\n"
            "index 3..4 100644\n"
            "--- a/two.py\n"
            "+++ b/two.py\n"
            "@@ -100,1 +100,2 @@\n"
            " keep2\n"
            "+added in two\n"
        )
        lines = parse_diff(diff).splitlines()
        self.assertIn("## File: 'one.py'", lines)
        self.assertIn("## File: 'two.py'", lines)
        self.assertIn("6 +added in one", lines)
        self.assertIn("101 +added in two", lines)

    def test_multiple_hunks_in_one_file(self):
        diff = (
            "diff --git a/m.py b/m.py\n"
            "index 1..2 100644\n"
            "--- a/m.py\n"
            "+++ b/m.py\n"
            "@@ -1,1 +1,2 @@\n"
            " first\n"
            "+added near top\n"
            "@@ -50,1 +51,2 @@\n"
            " later\n"
            "+added near bottom\n"
        )
        lines = parse_diff(diff).splitlines()
        self.assertIn("2 +added near top", lines)
        self.assertIn("52 +added near bottom", lines)


if __name__ == "__main__":
    unittest.main()
