"""Functional tests for scholarship_system.py.

Run from the Lab-5_Static_Code_Analysis directory:  python -m unittest -v
"""

import contextlib
import io
import json
import os
import subprocess
import sys
import tempfile
import unittest
from unittest import mock

import scholarship_system as screener

HERE = os.path.dirname(os.path.abspath(__file__))
PROGRAM = os.path.join(HERE, "scholarship_system.py")
U001 = {"gpa": 9.1, "credits": 4, "income": 450000}   # score 99.0, eligible
U002 = {"gpa": 7.2, "credits": 1, "income": 300000}   # score 74.0, too low
U005 = {"gpa": 8.4, "credits": 3, "income": 600000}   # score 90.0, eligible


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


class ScreenerTestCase(unittest.TestCase):
    """Base class: each test starts with no results and the default formula."""

    def setUp(self):
        self.reset_screener()
        self.addCleanup(self.reset_screener)

    @staticmethod
    def reset_screener():
        """Clear the results and restore the default merit formula."""
        screener.results.clear()
        screener.settings["merit_formula"] = screener.DEFAULT_MERIT_FORMULA

    def make_temp_dir(self):
        """Create a temporary directory that is removed after the test."""
        scratch = tempfile.TemporaryDirectory()
        self.addCleanup(scratch.cleanup)
        return scratch.name


class MeritScoreTests(ScreenerTestCase):
    """calculate_merit_score(), change_formula() and the formula checks."""

    def test_default_formula(self):
        self.assertEqual(screener.settings["merit_formula"],
                         "gpa * 10 + credits * 2")
        self.assertAlmostEqual(screener.calculate_merit_score(9.1, 4), 99.0)

    def test_representative_inputs(self):
        cases = [(8.4, 3, 90.0), (7.2, 1, 74.0), (6.5, 0, 65.0),
                 (10, 0, 100.0), (0, 0, 0.0)]
        for gpa, extra_credits, expected in cases:
            with self.subTest(gpa=gpa, credits=extra_credits):
                self.assertAlmostEqual(
                    screener.calculate_merit_score(gpa, extra_credits),
                    expected)

    def test_permitted_custom_formulas(self):
        cases = {"gpa * 10 + credits * 3": 103.0,
                 "(gpa + credits) / 2": 6.55,
                 "-gpa + +credits * 25": 90.9,
                 "  gpa * 9.5  ": 86.45}
        for formula, expected in cases.items():
            with self.subTest(formula=formula):
                screener.change_formula(formula)
                self.assertEqual(screener.settings["merit_formula"],
                                 formula.strip())
                self.assertAlmostEqual(
                    screener.calculate_merit_score(9.1, 4), expected)

    def test_malicious_formulas_are_rejected(self):
        payloads = ['__import__("os").system("echo hacked")',
                    'open("secret.txt").read()', 'eval("1")', 'exec("1")',
                    "gpa.__class__.__mro__",
                    "().__class__.__bases__[0].__subclasses__()",
                    "[gpa][0]", "lambda: 1", "(x := 5)", 'f"{gpa}"',
                    "[n for n in range(9)]"]
        for payload in payloads:
            with self.subTest(payload=payload):
                with self.assertRaises(ValueError):
                    screener.change_formula(payload)
                self.assertEqual(screener.settings["merit_formula"],
                                 screener.DEFAULT_MERIT_FORMULA)

    def test_unknown_variables_are_rejected(self):
        for formula in ("income * 2", "CUTOFF", "__builtins__", "results",
                        "GPA * 10"):
            with self.subTest(formula=formula):
                with self.assertRaisesRegex(ValueError, "unknown name"):
                    screener.parse_formula(formula)

    def test_unsupported_operations_are_rejected(self):
        for formula in ("gpa ** 2", "gpa % 3", "gpa // 2", "gpa > 5",
                        "gpa and credits", "not gpa", "~gpa", "gpa << 1",
                        "gpa if credits else 1", "(gpa, credits)"):
            with self.subTest(formula=formula):
                with self.assertRaisesRegex(ValueError, "not allowed"):
                    screener.parse_formula(formula)

    def test_non_numeric_and_non_finite_constants_are_rejected(self):
        for formula in ('"abc" * 10', "True * gpa", "None", "1j * gpa",
                        "1e999"):
            with self.subTest(formula=formula):
                with self.assertRaisesRegex(ValueError, "constant"):
                    screener.parse_formula(formula)

    def test_malformed_empty_and_oversized_formulas_are_rejected(self):
        for formula in ("gpa *", "import os", "", "   ", "gpa\x00",
                        "g" * 101, "+".join(["gpa"] * 20), 42, None):
            with self.subTest(formula=formula):
                with self.assertRaises(ValueError):
                    screener.parse_formula(formula)

    def test_division_by_zero_is_rejected(self):
        screener.change_formula("gpa / credits")
        self.assertAlmostEqual(screener.calculate_merit_score(9.0, 3), 3.0)
        with self.assertRaisesRegex(ValueError, "division by zero"):
            screener.calculate_merit_score(9.0, 0)

    def test_non_finite_scores_are_rejected(self):
        screener.change_formula("gpa * 1e308 * 10")
        with self.assertRaisesRegex(ValueError, "non-finite"):
            screener.calculate_merit_score(9.1, 4)
        screener.change_formula("gpa")
        with self.assertRaisesRegex(ValueError, "non-finite"):
            screener.calculate_merit_score(float("nan"), 0)

    def test_formula_is_checked_again_when_scoring(self):
        # Even a formula stored without change_formula() is never executed.
        screener.settings["merit_formula"] = '__import__("os").getcwd()'
        with self.assertRaises(ValueError):
            screener.calculate_merit_score(9.1, 4)


class EligibilityTests(ScreenerTestCase):
    """evaluate_applicant(): eligibility rules, defaults and validation."""

    def test_eligible_applicant(self):
        self.assertTrue(screener.evaluate_applicant("U001", U001))
        self.assertEqual(screener.results["U001"],
                         {"score": 99.0, "eligible": True})

    def test_applicant_below_merit_cutoff(self):
        self.assertFalse(screener.evaluate_applicant("U002", U002))
        self.assertEqual(screener.results["U002"],
                         {"score": 74.0, "eligible": False})

    def test_score_equal_to_cutoff_is_eligible(self):
        self.assertTrue(screener.evaluate_applicant("U010", {"gpa": 8.5}))

    def test_applicant_at_or_above_income_limit(self):
        strong = {"gpa": 9.8, "credits": 2}
        for income in (800000, 800001, 2500000):
            with self.subTest(income=income):
                self.assertFalse(screener.evaluate_applicant(
                    "U011", {**strong, "income": income}))
        self.assertTrue(screener.evaluate_applicant(
            "U012", {**strong, "income": 799999}))

    def test_missing_credits_and_income_default_to_zero(self):
        self.assertFalse(screener.evaluate_applicant("U004", {"gpa": 6.5}))
        self.assertEqual(screener.results["U004"],
                         {"score": 65.0, "eligible": False})
        self.assertTrue(screener.evaluate_applicant("U013", {"gpa": 9.0}))
        self.assertEqual(screener.results["U013"],
                         {"score": 90.0, "eligible": True})

    def test_invalid_sample_applicant_u003_is_rejected(self):
        with self.assertRaises(ValueError) as caught:
            screener.evaluate_applicant(
                "U003", {"gpa": 12.5, "credits": -3, "income": -1})
        for field in ("gpa", "credits", "income"):
            self.assertIn(field, str(caught.exception))
        self.assertNotIn("U003", screener.results)

    def test_invalid_values_are_rejected(self):
        invalid = [{}, {"credits": 3}, {"gpa": -0.1}, {"gpa": 10.01},
                   {"gpa": "9.1"}, {"gpa": None}, {"gpa": True},
                   {"gpa": float("nan")}, {"gpa": float("inf")},
                   {"gpa": 9, "credits": -1}, {"gpa": 9, "credits": "3"},
                   {"gpa": 9, "credits": float("nan")},
                   {"gpa": 9, "income": -5}, {"gpa": 9, "income": "low"},
                   {"gpa": 9, "income": float("inf")}]
        for scores in invalid:
            with self.subTest(scores=scores):
                with self.assertRaises(ValueError):
                    screener.evaluate_applicant("U020", scores)
        self.assertEqual(screener.results, {})

    def test_boundary_values_are_accepted(self):
        for scores in ({"gpa": 0}, {"gpa": 10},
                       {"gpa": 10.0, "credits": 0, "income": 0}):
            with self.subTest(scores=scores):
                screener.evaluate_applicant("U021", scores)
                self.assertIn("U021", screener.results)

    def test_invalid_student_ids_are_rejected(self):
        for student_id in ("", "   ", None, 7):
            with self.subTest(student_id=student_id):
                with self.assertRaises(ValueError):
                    screener.evaluate_applicant(student_id, U001)

    def test_log_entry_is_added_to_a_given_list(self):
        logs = []
        screener.evaluate_applicant("U001", U001, logs)
        self.assertEqual(logs, ["U001 scored 99.0"])

    def test_repeated_calls_do_not_share_state(self):
        # The original default logs=[] was one list shared by every call.
        for student_id in ("A1", "A2", "A3"):
            screener.evaluate_applicant(student_id, U001)
        self.assertEqual(screener.evaluate_applicant.__defaults__, (None,))
        first, second = [], []
        screener.evaluate_applicant("B1", U001, first)
        screener.evaluate_applicant("B2", U005, second)
        self.assertEqual(first, ["B1 scored 99.0"])
        self.assertEqual(second, ["B2 scored 90.0"])


class PersistenceTests(ScreenerTestCase):
    """persist_results() and load_results()."""

    def setUp(self):
        super().setUp()
        self.folder = self.make_temp_dir()
        self.path = os.path.join(self.folder, "results.json")
        screener.evaluate_applicant("U001", U001)
        self.saved = {"U001": {"score": 99.0, "eligible": True}}

    def write(self, text):
        """Write *text* to the test's results file as UTF-8."""
        with open(self.path, "w", encoding="utf-8") as handle:
            handle.write(text)

    def test_save_writes_json_to_the_given_path(self):
        self.assertTrue(screener.persist_results(self.path))
        self.assertEqual(os.listdir(self.folder), ["results.json"])
        with open(self.path, encoding="utf-8") as handle:
            self.assertEqual(json.load(handle), self.saved)

    def test_unwritable_path_keeps_current_results(self):
        missing_folder = os.path.join(self.folder, "missing", "results.json")
        for path in (missing_folder, self.folder):   # no such folder, a folder
            with self.subTest(path=path):
                with self.assertLogs("scholarship_system", "WARNING"):
                    self.assertFalse(screener.persist_results(path))
                self.assertEqual(screener.results, self.saved)

    def test_permission_error_is_reported(self):
        # Simulated, so the test behaves the same on every platform.
        denied = PermissionError(13, "Permission denied")
        with mock.patch("builtins.open", side_effect=denied):
            with self.assertLogs("scholarship_system", "WARNING") as logged:
                self.assertFalse(screener.persist_results(self.path))
        self.assertIn("Permission denied", logged.output[0])
        self.assertEqual(screener.results, self.saved)

    def test_error_while_writing_is_reported(self):
        # The file opens, but writing fails, for example on a full disk.
        disk_full = OSError(28, "No space left on device")
        with mock.patch("json.dump", side_effect=disk_full):
            with self.assertLogs("scholarship_system", "WARNING") as logged:
                self.assertFalse(screener.persist_results(self.path))
        self.assertIn("No space left on device", logged.output[0])
        self.assertEqual(screener.results, self.saved)

    def test_load_restores_saved_results(self):
        screener.evaluate_applicant("U002", U002)
        expected = dict(screener.results)
        screener.persist_results(self.path)
        screener.results.clear()
        self.assertTrue(screener.load_results(self.path))
        self.assertEqual(screener.results, expected)

    def test_load_replaces_the_current_results_in_place(self):
        # Code holding a reference (from scholarship_system import results)
        # must see the loaded data, so the dict is updated, not rebound.
        shared = screener.results
        loaded = {"U005": {"score": 90.0, "eligible": True}}
        self.write(json.dumps(loaded))
        self.assertTrue(screener.load_results(self.path))
        self.assertIs(screener.results, shared)
        self.assertEqual(shared, loaded)

    def test_load_reads_utf8(self):
        data = {"Zoë-07": {"score": 91.5, "eligible": True}}
        self.write(json.dumps(data, ensure_ascii=False))
        self.assertTrue(screener.load_results(self.path))
        self.assertEqual(screener.results, data)

    def test_missing_file_keeps_current_results(self):
        with self.assertLogs("scholarship_system", "WARNING") as logged:
            self.assertFalse(screener.load_results(self.path))
        self.assertIn("No saved results", logged.output[0])
        self.assertEqual(screener.results, self.saved)

    def test_malformed_json_keeps_current_results(self):
        for text in ("{not json", "", '{"U9": {"score": 9'):
            with self.subTest(text=text):
                self.write(text)
                with self.assertLogs("scholarship_system", "WARNING"):
                    self.assertFalse(screener.load_results(self.path))
                self.assertEqual(screener.results, self.saved)

    def test_unexpected_structure_keeps_current_results(self):
        for data in ([1, 2], {"U9": "yes"}, {"U9": {"score": 90.0}},
                     {"U9": {"score": "high", "eligible": True}},
                     {"U9": {"score": 90.0, "eligible": "yes"}}):
            with self.subTest(data=data):
                self.write(json.dumps(data))
                with self.assertLogs("scholarship_system", "WARNING"):
                    self.assertFalse(screener.load_results(self.path))
                self.assertEqual(screener.results, self.saved)

    def test_unreadable_file_keeps_current_results(self):
        with open(self.path, "wb") as handle:
            handle.write(b"\xff\xfe not utf-8")
        for path in (self.path, self.folder):   # undecodable, a directory
            with self.subTest(path=path):
                with self.assertLogs("scholarship_system", "WARNING"):
                    self.assertFalse(screener.load_results(path))
                self.assertEqual(screener.results, self.saved)


class ShortlistTests(ScreenerTestCase):
    """print_shortlist() output."""

    @staticmethod
    def shortlist():
        """Return what print_shortlist() prints."""
        buffer = io.StringIO()
        with contextlib.redirect_stdout(buffer):
            screener.print_shortlist()
        return buffer.getvalue()

    def test_includes_eligible_and_excludes_ineligible(self):
        screener.evaluate_applicant("U001", U001)
        screener.evaluate_applicant("U002", U002)
        screener.evaluate_applicant(
            "U006", {"gpa": 9.8, "credits": 2, "income": 950000})
        screener.evaluate_applicant("U005", U005)
        self.assertEqual(self.shortlist(),
                         "Shortlisted applicants:\n"
                         "  U001 score = 99.0\n"
                         "  U005 score = 90.0\n")

    def test_empty_shortlist(self):
        self.assertEqual(self.shortlist(), "Shortlisted applicants:\n")
        screener.evaluate_applicant("U002", U002)
        self.assertEqual(self.shortlist(), "Shortlisted applicants:\n")

    def test_score_display_follows_the_active_formula(self):
        screener.change_formula("gpa * 10 + credits * 3")
        screener.evaluate_applicant("U001", U001)
        self.assertEqual(self.shortlist(),
                         "Shortlisted applicants:\n  U001 score = 103.0\n")


class ProgramTests(ScreenerTestCase):
    """main() and the module's import behaviour."""

    def run_main(self, answer, folder=None):
        """Run main() in *folder* (default: a new temporary directory).

        Returns (output, folder).
        """
        folder = folder or self.make_temp_dir()
        self.addCleanup(os.chdir, os.getcwd())
        os.chdir(folder)
        buffer = io.StringIO()
        with mock.patch("builtins.input", return_value=answer), \
                contextlib.redirect_stdout(buffer):
            screener.main()
        return buffer.getvalue(), folder

    def test_demonstration_with_default_formula(self):
        output, folder = self.run_main("")
        self.assertIn("Skipped U003: gpa must be between 0 and 10", output)
        self.assertTrue(output.endswith("Shortlisted applicants:\n"
                                        "  U001 score = 99.0\n"
                                        "  U005 score = 90.0\n"))
        self.assertEqual(os.listdir(folder), ["scholarships.json"])

    def test_custom_formula_applies_to_every_applicant(self):
        output, _ = self.run_main("gpa * 10 + credits * 3")
        self.assertIn("U001 score = 103.0", output)
        self.assertIn("U005 score = 93.0", output)

    def test_rejected_formula_keeps_the_default(self):
        output, _ = self.run_main("gpa ** 2")
        self.assertIn("Formula rejected", output)
        self.assertIn("U001 score = 99.0", output)

    def test_failed_save_does_not_reload_an_older_file(self):
        # scholarships.json from an earlier run has become read-only (this is
        # simulated, so it behaves the same on every platform). Saving fails,
        # and the old file must not be read back in place of this run's
        # results.
        folder = self.make_temp_dir()
        old_file = os.path.join(folder, "scholarships.json")
        old_text = json.dumps({"OLD1": {"score": 120.0, "eligible": True}})
        with open(old_file, "w", encoding="utf-8") as handle:
            handle.write(old_text)
        real_open = open

        def read_only_open(file, mode="r", **kwargs):
            if "w" in mode:
                raise PermissionError(13, "Permission denied", file)
            return real_open(file, mode, **kwargs)

        with mock.patch("builtins.open", read_only_open), \
                self.assertLogs("scholarship_system", "WARNING") as logged:
            output, _ = self.run_main("", folder)
        self.assertIn("Could not save results", logged.output[0])
        self.assertTrue(output.endswith("Shortlisted applicants:\n"
                                        "  U001 score = 99.0\n"
                                        "  U005 score = 90.0\n"))
        self.assertNotIn("OLD1", screener.results)
        with open(old_file, encoding="utf-8") as handle:
            self.assertEqual(handle.read(), old_text)

    def test_unwritable_results_file_does_not_crash_the_program(self):
        # A folder named scholarships.json cannot be opened for writing.
        folder = self.make_temp_dir()
        os.mkdir(os.path.join(folder, "scholarships.json"))
        result = run_program("", folder)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertNotIn("Traceback", result.stderr)
        self.assertIn("Could not save results to scholarships.json",
                      result.stderr)
        self.assertIn("U001 score = 99.0", result.stdout)
        self.assertIn("U005 score = 90.0", result.stdout)

    def test_import_does_not_run_the_demonstration(self):
        folder = self.make_temp_dir()
        env = dict(os.environ, PYTHONPATH=HERE, PYTHONDONTWRITEBYTECODE="1")
        result = subprocess.run(
            [sys.executable, "-c", "import scholarship_system"],
            input="\n", capture_output=True, text=True, cwd=folder, env=env,
            timeout=60, check=False)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(result.stdout, "")         # no prompt, no shortlist
        self.assertEqual(os.listdir(folder), [])    # no scholarships.json


if __name__ == "__main__":
    unittest.main()
