# Lab 5 — Static Code Analysis

**Course:** Software Engineering  
**Lab:** Lab 5 — Static Code Analysis  
**SRN:** PES1UG24CS316  
**Name:** Paras Agarwal  
**Assigned project:** Student Scholarship Eligibility Screener (starter repository [SETAPESU26/L5_11_scholarship_screener](https://github.com/SETAPESU26/L5_11_scholarship_screener))

## Objective

To improve the quality, security and style of a Python program using three
static analysis tools:

- **Pylint** checks code quality and logic errors.
- **Bandit** finds security problems.
- **Flake8** enforces the PEP 8 style guide.

The work followed four steps:

1. Run the original program and record a baseline report from each tool.
2. Document the findings in an issue table.
3. Fix them in three commits, one per tool.
4. Verify the fixes by re-running the tools, the program and a test suite.

## The application

`scholarship_system.py` screens scholarship applicants. When run, it:

1. asks for a merit formula (press Enter to keep the default);
2. computes each applicant's **merit score** from GPA and extracurricular
   credits;
3. marks an applicant **eligible** when the score reaches the cutoff **and**
   the family income is below the income limit;
4. saves the results to `scholarships.json`, loads them back and prints the
   shortlist.

If the results cannot be saved, for example because `scholarships.json` is
read-only, the program prints a one-line warning instead of crashing. It does
not read the old file back, so an older file cannot replace this run's
results, and it prints the shortlist from memory.

| Rule | Value |
|---|---|
| Default merit formula | `gpa * 10 + credits * 2` |
| Merit cutoff | score of at least 85 |
| Income limit | income below 800000 |
| GPA | required; a finite number from 0 to 10 |
| Extracurricular credits | optional, default 0; finite and not negative |
| Family income | optional, default 0; finite and not negative |

Invalid applicant data raises `ValueError`, and the applicant is not recorded.
The demo prints `Skipped <id>: <reasons>` for it. Applicant U003 has invalid
data (GPA 12.5, credits −3, income −1) and is kept in the demo on purpose to
show this check.

**Custom merit formulas** may use only:

- the variables `gpa` and `credits`;
- int or float constants;
- parentheses;
- the operators `+ - * /` and unary `+` / `-`.

A formula can be at most 100 characters and 50 syntax nodes long. Anything
else is rejected with a message and the current formula is kept, including
function calls, attribute access, subscripts, other names, `**`, comparisons,
and boolean, string, complex or infinite constants. Formulas are never passed
to `eval()`. If a formula divides by zero or gives a non-finite score for one
applicant, that applicant is skipped.

Sample data and the expected result with the default formula:

| Applicant | GPA | Credits | Income | Score | Result |
|---|---|---|---|---|---|
| U001 | 9.1 | 4 | 450000 | 99.0 | shortlisted |
| U002 | 7.2 | 1 | 300000 | 74.0 | below cutoff |
| U003 | 12.5 | −3 | −1 | — | skipped: invalid data |
| U004 | 6.5 | (0) | (0) | 65.0 | below cutoff |
| U005 | 8.4 | 3 | 600000 | 90.0 | shortlisted |

## Folder contents

```text
Lab-5_Static_Code_Analysis/
├── README.md                     this guide
├── scholarship_system.py         the screener (final version)
├── test_scholarship_system.py    46 functional tests (unittest)
├── issues.md                     issue table: findings and fixes
├── requirements.txt              pinned analysis tools
├── .gitignore                    ignores .venv/, __pycache__/, scholarships.json and the class-list PDF
├── .gitattributes                keeps the patch files byte-for-byte as generated
├── Lab_5_Static_Code_Analysis_Student_handout.pdf
├── commits/                      the three fix commits as patch files
│   ├── 0001-fix-bandit-security-findings.patch
│   ├── 0002-fix-pylint-quality-findings.patch
│   └── 0003-fix-flake8-style-findings.patch
└── reports/
    ├── before/                   original starter code
    │   ├── program_output.txt
    │   ├── pylint_report.txt
    │   ├── bandit_report.txt
    │   └── flake8_report.txt
    └── after/                    final code
        ├── program_output.txt
        ├── pylint_report.txt
        ├── bandit_report.txt
        ├── flake8_report.txt     empty: Flake8 reported nothing
        └── test_output.txt
```

## Setup (Windows PowerShell)

Run the commands below from this folder. Python 3.13.7 was used.

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install --upgrade pip
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
```

The program itself needs only the Python standard library.
`requirements.txt` pins the tool versions used for every report: Pylint 4.1.3,
Bandit 1.9.4 and Flake8 7.4.1.

## Run the application

```powershell
.\.venv\Scripts\python.exe scholarship_system.py
```

At the prompt, press Enter to keep the default formula or type one, for
example `gpa * 10 + credits * 3`. To supply the answer without typing it:

```powershell
cmd /c "echo.| .venv\Scripts\python.exe scholarship_system.py"
cmd /c "echo gpa * 10 + credits * 3| .venv\Scripts\python.exe scholarship_system.py"
```

These use `cmd`'s `echo` because Windows PowerShell can add an invisible
byte-order mark (U+FEFF) to text piped into a program. The screener then
rejects the formula as invalid and keeps the default. Each run writes
`scholarships.json` in the current folder; Git ignores this file.

## Run the tests

```powershell
.\.venv\Scripts\python.exe -m unittest -v
```

The 46 tests fall into six groups:

- **Formula security:** end-to-end through the prompt, including a
  code-injection payload.
- **Merit scores and formula checking.**
- **Eligibility rules and input validation.**
- **JSON persistence:** saving, including write failures such as a
  permission error or a full disk (simulated), and loading missing,
  malformed, undecodable and wrongly structured files.
- **Shortlist output.**
- **`main()` and import behaviour,** including a run whose results cannot be
  saved.

The tests use temporary folders and leave no files behind. Each requirement
was also broken on purpose in a copy of the code (21 variants, such as
restoring `logs=[]`, allowing `**` or reading an old results file back after
a failed save), and the suite failed every time.

## Run the static analysis tools

```powershell
.\.venv\Scripts\python.exe -m pylint scholarship_system.py
.\.venv\Scripts\python.exe -m bandit -r scholarship_system.py
.\.venv\Scripts\python.exe -m flake8 scholarship_system.py
```

These commands saved the reports in `reports/after/`. The `reports/before/`
files were produced the same way from the original code.

```powershell
.\.venv\Scripts\python.exe -m pylint scholarship_system.py | Out-File -Encoding utf8 reports\after\pylint_report.txt
.\.venv\Scripts\python.exe -m bandit -r scholarship_system.py | Out-File -Encoding utf8 reports\after\bandit_report.txt
.\.venv\Scripts\python.exe -m flake8 scholarship_system.py | Out-File -Encoding utf8 reports\after\flake8_report.txt
cmd /c ".venv\Scripts\python.exe -m unittest -v > reports\after\test_output.txt 2>&1"
```

A few notes on these commands:

- `Out-File -Encoding utf8` is used because `>` in Windows PowerShell 5.1 can
  write UTF-16.
- Each tool exits with a non-zero code when it finds issues. On the original
  code that is expected and is not a setup error.
- Bandit also prints `[main] INFO` lines to the console. They are not part of
  the report.

## Reports

| Report | Before (original starter code) | After (final code) |
|---|---|---|
| Program output | [`reports/before/program_output.txt`](reports/before/program_output.txt) | [`reports/after/program_output.txt`](reports/after/program_output.txt) |
| Pylint | [`reports/before/pylint_report.txt`](reports/before/pylint_report.txt) | [`reports/after/pylint_report.txt`](reports/after/pylint_report.txt) |
| Bandit | [`reports/before/bandit_report.txt`](reports/before/bandit_report.txt) | [`reports/after/bandit_report.txt`](reports/after/bandit_report.txt) |
| Flake8 | [`reports/before/flake8_report.txt`](reports/before/flake8_report.txt) | [`reports/after/flake8_report.txt`](reports/after/flake8_report.txt) |
| Tests | — | [`reports/after/test_output.txt`](reports/after/test_output.txt) |

The before reports were generated from the unmodified starter file (starter
commit `aa6e272`) before any change was made. Each `program_output.txt`
records five runs with different answers to the formula prompt, and each run
shows its exit code:

1. the default formula;
2. a custom formula;
3. invalid syntax;
4. an unknown name;
5. a harmless code-injection probe.

## Results

| Check | Before | After |
|---|---|---|
| Pylint 4.1.3 | **4.69/10**, 26 messages | **10.00/10**, 0 messages |
| Bandit 1.9.4 | **2 issues**: B307 `eval` (Medium), B110 `try`/`except`/`pass` (Low) | **0 issues** |
| Flake8 7.4.1 | **12**: F401 ×2, E302 ×7, E305, E712, E722 | **0** |
| Program, default answer | U003 (invalid data) shortlisted with score 119.0 | U003 skipped with its reasons; U001 99.0 and U005 90.0 shortlisted |
| Program, injection probe | injected code ran and set U005's score to 100 | formula rejected, default kept |
| Program, formula `gpa *` | crashed with `SyntaxError` (exit code 1) | formula rejected, run completes (exit code 0) |
| Program, results file cannot be written | crashed with `PermissionError` (exit code 1) | one-line warning, shortlist printed from memory (exit code 0) |
| Functional tests | — | **46 run, 46 passed** |

No checks were disabled and the source has no `# noqa`, `# nosec` or
`# pylint: disable` comments.

## Issues found and fixed

The full table, with tool codes, original line numbers and the fix for each
finding, is in [`issues.md`](issues.md). In summary:

- **Security (Bandit):**
  - `eval()` on a formula typed by the user allowed arbitrary code execution
    (B307). It was replaced by a restricted arithmetic evaluator.
  - A bare `try`/`except`/`pass` hid every error (B110). It now handles
    specific exceptions, logs a warning and reports failure.
- **Bugs found by the tools:**
  - A mutable default argument `logs=[]` shared one list between calls
    (W0102).
  - Files were opened without `with` or an explicit encoding (R1732, W1514).
- **Bugs found by running the program:**
  - Invalid applicants such as U003 were shortlisted.
  - A custom formula applied only to the last applicant.
  - Invalid formulas crashed the program.
  - Importing the module ran the interactive demo.
- **Found in code review (no tool reported it):**
  - A results file that could not be written, such as a read-only file,
    crashed the program. The failure is now reported, the old file is not
    read back, and the shortlist comes from memory.
- **Code quality and style (Pylint, Flake8):**
  - `global` statements were removed and the shadowed built-in `credits` was
    renamed.
  - The unused import was removed, `== True` was replaced by a truthiness
    test, `printShortlist` was renamed and an f-string replaced `%`
    formatting.
  - Docstrings were added.
  - PEP 8 blank lines were added around top-level definitions.

## Commits

Lab 5 is four commits: the unmodified starter code, then one fix commit per
tool.

1. `chore(lab5): add scholarship screener starter and baseline reports` —
   the original `scholarship_system.py` exactly as supplied (starter commit
   `aa6e272`), `.gitignore`, the lab handout, `requirements.txt` and the
   baseline reports in `reports/before/`. Nothing is fixed in this commit.
2. `fix(security): address Bandit findings` — the safe formula evaluator,
   specific exception handling, the Bandit report and the security
   regression tests.
3. `fix(quality): resolve Pylint findings` — Pylint 10.00/10, input
   validation, a single formula for all applicants, the `__main__` guard,
   handling of results-file write errors and 46 tests.
4. `style: resolve Flake8 findings and finalize Lab 5` — PEP 8 blank lines,
   the final reports, the documentation, the ignore rule for the class-list
   PDF (it lists other students' names and SRNs) and the patch files.

### Patch files

`commits/` holds the three fix commits as patch files:

| Patch file | Commit |
|---|---|
| `0001-fix-bandit-security-findings.patch` | `fix(security): address Bandit findings` |
| `0002-fix-pylint-quality-findings.patch` | `fix(quality): resolve Pylint findings` |
| `0003-fix-flake8-style-findings.patch` | `style: resolve Flake8 findings and finalize Lab 5` |

They were made with `git format-patch --zero-commit`, so each one contains
the commit message and the full diff, with zeros in place of the commit hash.
The third patch leaves out the `commits/` folder, because a patch cannot
contain itself.

To replay them, apply them in order from the repository root on a copy of the
first Lab 5 commit (find its hash with `git log --oneline`):

```powershell
git worktree add ..\lab5-replay <hash of the first Lab 5 commit>
cd ..\lab5-replay
git apply --index ..\PES1UG24CS316_SE_LABS\Lab-5_Static_Code_Analysis\commits\0001-fix-bandit-security-findings.patch
git apply --index ..\PES1UG24CS316_SE_LABS\Lab-5_Static_Code_Analysis\commits\0002-fix-pylint-quality-findings.patch
git apply --index ..\PES1UG24CS316_SE_LABS\Lab-5_Static_Code_Analysis\commits\0003-fix-flake8-style-findings.patch
```

The result matches the final commit apart from the `commits/` folder.
