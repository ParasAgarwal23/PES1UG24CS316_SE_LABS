"""Functional tests for scholarship_system.py.

Run from the Lab-5_Static_Code_Analysis directory:  python -m unittest -v
"""

import os
import subprocess
import sys
import tempfile
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
PROGRAM = os.path.join(HERE, "scholarship_system.py")


def run_program(answer, cwd):
    """Run the screener in *cwd*, answer its formula prompt, return result."""
    return subprocess.run(
        [sys.executable, PROGRAM], input=answer + "\n", capture_output=True,
        text=True, cwd=cwd, timeout=60, check=False,
    )


class FormulaSecurityTests(unittest.TestCase):
    """A formula typed at the prompt must never run as Python code."""

    def setUp(self):
        scratch = tempfile.TemporaryDirectory()
        self.addCleanup(scratch.cleanup)
        self.workdir = scratch.name

    def test_injected_code_is_not_executed(self):
        payload = ('__import__("pathlib").Path("injected.txt")'
                   '.write_text("x") or 100')
        result = run_program(payload, self.workdir)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertFalse(
            os.path.exists(os.path.join(self.workdir, "injected.txt")),
            "the formula was executed as Python code")
        self.assertIn("Formula rejected", result.stdout)

    def test_invalid_formulas_are_rejected_without_crashing(self):
        for formula in ("gpa *", "income * 2", "gpa ** 2", "open('x')"):
            with self.subTest(formula=formula):
                result = run_program(formula, self.workdir)
                self.assertEqual(result.returncode, 0, result.stderr)
                self.assertIn("Formula rejected", result.stdout)
                # The default formula stays in force.
                self.assertIn("U005 score = 90.0", result.stdout)

    def test_default_formula_scores_are_unchanged(self):
        result = run_program("", self.workdir)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("U001 score = 99.0", result.stdout)
        self.assertIn("U005 score = 90.0", result.stdout)

    def test_valid_custom_formula_is_still_supported(self):
        result = run_program("gpa * 10 + credits * 3", self.workdir)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertNotIn("Formula rejected", result.stdout)
        self.assertIn("U005 score = 93.0", result.stdout)


if __name__ == "__main__":
    unittest.main()
