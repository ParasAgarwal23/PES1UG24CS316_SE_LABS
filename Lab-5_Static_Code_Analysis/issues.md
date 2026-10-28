# Lab 5 — Issue Table

**Name:** Paras Agarwal  
**SRN:** PES1UG24CS316  
**File analysed:** `scholarship_system.py` (Student Scholarship Eligibility Screener)

Line numbers refer to the **original** starter file, exactly as reported in
[`reports/before/`](reports/before/). Tools: Pylint 4.1.3, Bandit 1.9.4 and
Flake8 7.4.1 on Python 3.13.7. Rows 1–15 are ordered by severity: security
first, then bugs, then code quality and style. Row 16 was found in code
review and is listed last.

**Types:** *Security* — exploitable weakness. *Bug* — wrong or fragile
behaviour. *Quality* — maintainability problem. *Style* — PEP 8 and naming.
Rows marked *found by running the program*, *found while writing the tests*
or *found in code review* were not reported by any tool.

| Issue | Type | Line(s) | Description | Fix Approach |
|---|---|---|---|---|
| 1. Arbitrary code execution through `eval()` — Bandit **B307** (severity Medium, confidence High, CWE-78), Pylint **W0123** eval-used, Pylint **W0613** ×2 unused-argument | Security | 12 (eval); 11; 24–26 and 51–53 (formula comes from `input()`) | `calculate_merit_score()` returned `eval(MERIT_FORMULA)`, and `main()` stored whatever was typed at the prompt as the formula, so any Python expression ran with the program's permissions. Confirmed on the original: the probe `__import__("builtins").print(...) or 100` printed its message and set U005's score to 100 (run 5 in `reports/before/program_output.txt`). Malformed formulas such as `gpa *` and `income * 2` crashed the program with a traceback (runs 3–4). The W0613 warnings appeared because `gpa` and `credits` were only used inside the eval string. | Replaced `eval()` with a small AST interpreter. `parse_formula()` parses with `ast.parse(mode="eval")` and allows only the names `gpa` and `credits`, finite int/float constants, `+ - * /`, unary `+ -` and parentheses, with at most 100 characters and 50 syntax nodes. `_evaluate()` walks the checked tree. Division by zero and non-finite results raise `ValueError`. `change_formula()` validates before storing, the stored formula is checked again at every evaluation, and `main()` reports a rejected formula and keeps the current one. |
| 2. `try`/`except`/`pass` swallowing every error — Bandit **B110** (severity Low, confidence High, CWE-703), Pylint **W0702** bare-except, Flake8 **E722** | Security | 35–38 | `load_results()` wrapped the read in a bare `except: pass`, which silently hid a missing file, a permission error, corrupt JSON and even programming errors or `KeyboardInterrupt`. The caller could not tell whether loading worked. | Catch only `FileNotFoundError` and `(OSError, UnicodeDecodeError, json.JSONDecodeError)`, log a warning and return `False`, or return `True` on success. The in-memory results are left unchanged when loading fails. A file whose JSON does not have the expected structure is also rejected. |
| 3. Mutable default argument — Pylint **W0102** dangerous-default-value | Bug | 14 (used at 21) | `logs=[]` is created once, when the function is defined, so every call that did not pass `logs` appended to the same hidden list. It grew for as long as the program ran, sharing state between calls. | Default changed to `logs=None`. An entry is appended only to a list that the caller passes. A regression test checks that `__defaults__` is still `(None,)` after repeated calls and that separate lists stay separate. |
| 4. Invalid applicant data accepted and shortlisted — *found by running the program* | Bug | 14–22; data at 49 | There was no input validation. U003 (GPA 12.5 on a 10-point scale, credits −3, income −1) scored 119.0, the highest score, and was shortlisted (run 1 in `reports/before/program_output.txt`). Strings, `None`, booleans, NaN and infinity were also accepted or failed later. | `_validate_scores()` requires a finite `gpa` between 0 and 10. `credits` and `income` still default to 0, as in the original, but must be finite and not negative. Booleans are rejected, and all problems are reported in one `ValueError`. `student_id` must be a non-empty string. Nothing is recorded for invalid data, and `main()` prints `Skipped <id>: <reason>`. U003 is kept in the demo to show the check working. |
| 5. Formula prompt in the middle of the batch — *found by running the program* | Bug | 47–54 | U001–U004 were scored before the formula prompt, so a custom formula applied only to U005. With `gpa * 10 + credits * 3`, U001 kept 99.0 from the default formula while U005 got 93.0 from the new one: one shortlist, two formulas (run 2 in `reports/before/program_output.txt`). | The prompt now comes first, then every applicant is scored in one loop with the same formula. An error for one applicant is reported and the run continues. Final run 2 gives U001 103.0 and U005 93.0. |
| 6. Files opened without `with` and without an encoding — Pylint **R1732** consider-using-with ×2, **W1514** unspecified-encoding ×2 | Bug | 29–31, 36 | `persist_results()` closed its file by hand, so the handle leaked if writing failed, and `load_results()` never closed the file it opened. Without `encoding=`, the platform default (cp1252 on Windows) is used, so non-ASCII text in the JSON file could be misread. | `with open(file, "w", encoding="utf-8")` with `json.dump()`, and `with open(file, encoding="utf-8")` with `json.load()`. A test loads a UTF-8 results file whose applicant id contains "ë". |
| 7. `global` statements rebinding module state — Pylint **W0603** global-statement ×2 | Quality | 25, 34 | `change_formula()` and `load_results()` rebound module globals. Rebinding `results` also left any other reference to the old dict (for example `from scholarship_system import results`) holding stale data. | The active formula lives in a `settings` dict that is changed in place, and `load_results()` updates `results` with `clear()` and `update()`. A test checks that the same dict object is kept. |
| 8. Interactive demo runs on import — *found while writing the tests* | Bug | 59 | `main()` was called at module level, so `import scholarship_system` prompted for input, scored the demo applicants and wrote `scholarships.json`. | Added an `if __name__ == "__main__":` guard. A test imports the module in a fresh interpreter and checks that there is no output and no file. |
| 9. Built-in name `credits` shadowed — Pylint **W0622** redefined-builtin ×2 | Quality | 11, 16 | The parameter and a local variable hid the built-in `credits` object, which is confusing and error-prone. | Renamed to `extra_credits` in the Python code. Formulas still use the documented variable name `credits`. |
| 10. Unused imports — Pylint **W0611** ×2, Flake8 **F401** ×2 | Style | 2, 3 | `math` and `sys` were imported but never used. | `sys` was removed. `math` is now used by the safe evaluator (`math.isfinite`), so it is no longer unused. |
| 11. Comparison to `True` — Pylint **C0121** singleton-comparison, Flake8 **E712** | Style | 43 | `results[r]["eligible"] == True` compares against a singleton instead of testing the value. | `if record["eligible"]:`. The value is always a bool, which is checked when results are loaded. |
| 12. Function name not in snake_case — Pylint **C0103** invalid-name | Style | 40–44 | `printShortlist` does not follow the snake_case naming convention. The loop also looked each record up again by key. | Renamed to `print_shortlist` and the loop now iterates over `results.items()`. The printed format is unchanged. |
| 13. Old-style `%` string formatting — Pylint **C0209** consider-using-f-string | Style | 21 | `"%s scored %s" % (student_id, score)` is harder to read than an f-string. | Replaced with `f"{student_id} scored {score}"`. |
| 14. Missing docstrings — Pylint **C0114** ×1, **C0116** ×7 | Style | 1, 11, 14, 24, 28, 33, 40, 46 | The module and all seven functions had no docstrings. | Added a module docstring and a docstring for every function, including the new helpers. |
| 15. Missing blank lines around top-level definitions — Flake8 **E302** ×7, **E305** ×1 | Style | 11, 14, 24, 28, 33, 40, 46 (E302); 59 (E305) | PEP 8 requires two blank lines around top-level functions, and the file used one. The final file has 13 functions, so the Flake8 run just before the style fix reported E302 ×13 and E305 ×1. | Added the second blank line before every top-level definition and before the `__main__` guard. In the style commit, the only change to `scholarship_system.py` is these blank lines. |
| 16. Results-file write errors crashed the program — *found in code review* | Bug | 28–31; 55–56 | `persist_results()` let every `OSError` escape, so a read-only `scholarships.json` or an invalid path stopped the program with a traceback before the shortlist was printed. Confirmed on the original with a folder named `scholarships.json` (`PermissionError`, exit code 1); the code after the security commit behaved the same. Catching the error alone would not be enough, because `main()` then called `load_results()`, which could read an older file and print its shortlist as this run's. | `persist_results()` catches `OSError`, logs `Could not save results to <file>: <error>` and returns `False`, or `True` once the file is written, and leaves the in-memory results untouched. `main()` reads the file back only after a successful save; otherwise it prints the shortlist from memory. Tests cover a missing folder, a folder in place of the file, a simulated permission error, a simulated full disk, a simulated read-only older file and a full program run that cannot save. |

## Results before and after

| Check | Before (original starter code) | After (final code) |
|---|---|---|
| Pylint | **4.69/10**, 26 messages (13 warning, 2 refactor, 11 convention) | **10.00/10**, 0 messages |
| Bandit | **2 issues**: B307 (Medium), B110 (Low) | **No issues identified** |
| Flake8 | **12**: F401 ×2, E302 ×7, E305, E712, E722 | **0** (the report file is empty) |
| Program, default answer | U001 99.0, **U003 119.0** and U005 90.0 shortlisted | U003 skipped with its reasons; U001 99.0 and U005 90.0 shortlisted |
| Program, injection probe | injected code ran and set U005's score to 100 | formula rejected, default kept |
| Program, formula `gpa *` | crashed with `SyntaxError` (exit code 1) | formula rejected, run completes (exit code 0) |
| Program, results file cannot be written | crashed with `PermissionError` (exit code 1) | one-line warning, shortlist printed from memory (exit code 0) |
| Functional tests | — | 46 run, 46 passed (`reports/after/test_output.txt`) |

All 26 Pylint messages, both Bandit issues and all 12 Flake8 diagnostics from
the baseline are resolved, as confirmed by the reports in
[`reports/after/`](reports/after/). No checks were disabled and the source
has no `# noqa`, `# nosec` or `# pylint: disable` comments. Some findings were
reported by more than one tool (the bare `except` by all three), so they are
grouped into single rows above.

## Fixes by commit

1. `chore(lab5): add scholarship screener starter and baseline reports` — no
   fixes: the original starter code and the baseline reports.
2. `fix(security): address Bandit findings` — rows 1 and 2.
3. `fix(quality): resolve Pylint findings` — rows 3 to 14 and row 16, plus the
   stricter results-file check from row 2.
4. `style: resolve Flake8 findings and finalize Lab 5` — row 15, plus the final
   reports and documentation.

Commits 2 to 4 are also saved as patch files in [`commits/`](commits/).
