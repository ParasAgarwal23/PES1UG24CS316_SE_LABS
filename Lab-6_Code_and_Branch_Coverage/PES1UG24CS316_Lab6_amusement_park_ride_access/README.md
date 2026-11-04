# Lab 6 — Code and Branch Coverage Analysis

**Name:** Paras Agarwal  
**SRN:** PES1UG24CS316  
**Section:** F

**Course:** Software Engineering  
**Assigned project:** Amusement Park Ride Access (repository index 11, starter
repository [SETAPESU26/L6_L7_11_amusement_park_ride_access](https://github.com/SETAPESU26/L6_L7_11_amusement_park_ride_access))

## Objective

To measure, analyse and improve the test coverage of a small Python module
with **pytest** and **Coverage.py**:

- measure the line and branch coverage of the starter test;
- read the coverage reports to find the untested lines and branches;
- write a test suite that reaches at least 90% **line (code) coverage**;
- write a second test suite that reaches at least 90% **branch coverage**,
  testing both the true and the false outcome of every decision.

## The application

`amusement_park_ride_access.py` handles ride admission and ticketing for an
amusement park, and checks the safety-restraint latch sensors on a ride. It
only uses the Python standard library and has no `main` block; it is used by
importing its two functions. The module and the starter test are kept exactly
as supplied (same bytes as the assigned repository).

### `process_ride_admissions(groups, express_pass_fee)`

`groups` is a list of dictionaries, one per group waiting for a ride. Each
group may have `is_open`, `ride_type`, `has_fast_lane` and a list of
`patrons`; each patron may have `height_cm`, `health_warning` and `is_child`.
The function returns a dictionary with `total_revenue` (rounded to 2 decimal
places) and a `status`.

| Rule | Value |
|---|---|
| Invalid input | `groups` is not a list, or `express_pass_fee < 0` → `ValueError` |
| Closed group (`is_open` false or missing) | skipped completely |
| Roller coaster ticket | 25.00 |
| Water ride ticket | 18.00 |
| Family ride ticket (also used when `ride_type` is missing) | 10.00 |
| Unknown ride type | the group counts as **one** rejection and is skipped |
| Height `<= 0` (or missing) | patron rejected |
| Health warning | patron rejected; on a **roller coaster** the whole group's total is reset to 0 and the rest of the group is not processed (`break`) |
| Height below 120 cm | patron rejected |
| Child (height at least 120 cm) | 60% of the base ticket |
| Adult (height at least 120 cm) | full base ticket |
| Fast lane (`has_fast_lane`) | `express_pass_fee` added once for the group |
| More than 4 rejections in total | status `SAFETY_AUDIT` (checked first) |
| Total revenue of 0.0 | status `ZERO_ADMISSIONS` |
| Otherwise | status `COMPLETED` |

### `inspect_safety_restraints(restraint_streams)`

`restraint_streams` is a list of sensor streams, one per restraint. Each
stream is a list of readings: `0` means the restraint is **unlatched**, any
other value means it is latched.

| Input | Result |
|---|---|
| Empty list (or `None`) | `NO_DATA` |
| Two consecutive `0` readings in the same stream | `EMERGENCY_LOCK` (returned immediately) |
| A latched reading | resets the unlatched streak to 0 |
| A new stream | starts again with a streak of 0 |
| All streams read without two consecutive `0`s | `SAFE` |

### Behaviour worth knowing

These follow directly from the original code. They are tested as they are; the
application was not changed.

- A roller-coaster group that is cancelled by a health warning still pays the
  fast-lane fee, because the fee is added after the patron loop.
- After that `break`, the remaining patrons of the group are not checked, so
  they are not counted as rejections either.
- The height `<= 0` check comes before the health-warning check, so such a
  patron is rejected once, for the invalid height, and does not cancel a
  roller-coaster group.
- A water-ride child ticket is `18.0 * 0.60 = 10.799999999999999` in Python;
  the result is rounded, so it is reported as `10.8`.
- `SAFETY_AUDIT` is checked before `ZERO_ADMISSIONS`, so five rejections with no
  revenue give `SAFETY_AUDIT` with a revenue of `0.0`.

## Tools used

| Tool | Version | Purpose |
|---|---|---|
| Python | 3.13.7 | runs the module and the tests |
| pytest | 9.2.0 | test framework |
| Coverage.py | 7.17.1 | measures line and branch coverage |

All coverage runs measure only the application module
(`--source=amusement_park_ride_access`), so the test files are not counted.
Every run writes to its own data file (`--data-file=...`), so one run cannot
overwrite another run's results.

## Baseline: coverage of the starter test

The starter test `test_amusement_park.py` has one test (a single adult on a
family ride). It was run unchanged with the handout's commands, adding only
`--source` and `--data-file` (see [Running the starter test](#running-the-starter-test)).

| Measurement | Covered | Total | Result |
|---|---|---|---|
| Line coverage | 28 statements | 58 | **48.28%** (report shows 48%) |
| Branch coverage | 16 branches | 40 | **40.00%** |
| Combined `Cover` column of the branch run | 44 | 98 | 45% |

```text
Name                            Stmts   Miss  Cover   Missing
-------------------------------------------------------------
amusement_park_ride_access.py      58     30    48%   3, 10, 16, 18, 22-23, 33-34, 37-41, 43-44, 46, 51, 56, 58, 63-75
```

```text
Name                            Stmts   Miss Branch BrPart  Cover   Missing
---------------------------------------------------------------------------
amusement_park_ride_access.py      58     30     40     12    45%   3, 10, 16, 18, 22-23, 33-34, 37-41, 43-44, 46, 51, 56, 58, 63-75
```

The starter test misses the invalid-input error, closed groups, the roller
coaster and water ride prices, unknown ride types, invalid and short heights,
health warnings, child pricing, the fast lane, the `SAFETY_AUDIT` and
`ZERO_ADMISSIONS` results, and the whole of `inspect_safety_restraints`
(lines 63-75).

## Code coverage testing

`CodeCoverageTest_11_amusement_park_ride_access.py` was written from the
`Missing` column of the baseline report. Each test is aimed at one block of
statements that the starter test never ran, and checks the actual revenue,
status or sensor result, not only that the code runs. Two small helpers,
`make_patron()` and `make_group()`, build the input dictionaries.
Parametrized tests are used where the same check is repeated for each ride
type.

| Test | Lines of `amusement_park_ride_access.py` it adds |
|---|---|
| `test_invalid_input_raises_value_error` (non-list `groups`, negative fee) | 3 |
| `test_adult_pays_full_ticket_for_each_ride` (3 ride types) | 16, 18 |
| `test_missing_ride_type_is_priced_as_family_ride` | default of line 12 |
| `test_child_pays_sixty_percent_of_ticket` (3 ride types) | 46 |
| `test_fast_lane_fee_is_added_once_per_group` | 51 |
| `test_closed_group_is_skipped` | 10, 58 |
| `test_unknown_ride_type_rejects_the_group` | 22-23 |
| `test_patron_with_invalid_height_is_rejected` | 33-34 |
| `test_patron_shorter_than_120_cm_is_rejected` | 43-44 |
| `test_health_warning_cancels_whole_roller_coaster_group` | 37-40 |
| `test_health_warning_on_other_ride_rejects_only_that_patron` | 41 |
| `test_more_than_four_rejections_triggers_safety_audit` | 56 |
| `test_revenue_of_several_groups_is_added_and_rounded` | checks the total of several groups and the rounding |
| `test_no_restraint_data` | 63-64 |
| `test_restraints_without_two_unlatched_readings_in_a_row_are_safe` | 66-71, 74-75 |
| `test_two_unlatched_readings_in_a_row_lock_the_ride` | 72 |

The expected values come from the rules in the code, for example a
water-ride child pays `18.0 * 0.60`, which is reported as `10.8`, and the
mixed-groups test expects `(25.0 + 15.0 + 4.99) + (10.8 + 10.8) = 66.59`.

## Code coverage result

The code coverage suite was run on its own, without `--branch`:

| Measurement | Result |
|---|---|
| Tests | 21 passed |
| Statements | 58 |
| Covered statements | 58 |
| Missing statements | 0 |
| **Line coverage** | **58 / 58 = 100%** (baseline 48.28%) |

```text
Name                            Stmts   Miss  Cover   Missing
-------------------------------------------------------------
amusement_park_ride_access.py      58      0   100%
-------------------------------------------------------------
TOTAL                              58      0   100%
```

## Branch coverage testing

Coverage.py counts a branch for every possible jump out of a decision line:
the true and false outcome of each `if`/`elif`, and "run the body" or
"leave the loop" for each `for` loop. The module has 20 decision lines, so it
has **40 branches**.

`BranchCoverageTest_11_amusement_park_ride_access.py` is organised by
decision. For each one there is a case that makes it true and a case that
makes it false, using boundary values where a comparison is involved (fee
`0`, heights `0`/`1`/`119`/`120`, 4 and 5 rejections, an unlatched streak of 1
and 2). Some tests also check what follows from a branch, for example that the
roller-coaster `break` stops counting rejections while the other rides
continue, and that the unlatched streak starts again for each stream.

| Decision (line) | True outcome tested with | False outcome tested with |
|---|---|---|
| `not isinstance(groups, list) or express_pass_fee < 0` (2) | a tuple, `None`, fee `-0.01` → `ValueError` | a list with fee `0.0` or `12.5` |
| `for group in groups` (8) | three groups, all processed | empty list, the loop never runs |
| `not group.get("is_open", False)` (9) | `is_open` false or missing → group skipped, its patrons not counted | `is_open` true |
| `ride_type == "roller_coaster"` (15) | roller coaster → 25.00 | the other ride types |
| `ride_type == "water_ride"` (17) | water ride → 18.00 | family and unknown rides |
| `ride_type == "family"` (19) | family, or no `ride_type` → 10.00 | `"bumper_cars"`, `"Roller_Coaster"` → one rejection per group, no fast-lane fee |
| `for patron in patrons` (27) | groups with patrons | empty or missing `patrons` → only the fast-lane fee |
| `height_cm <= 0` (32) | `-10`, `0`, missing height | `150`; a height of `0` with a health warning shows this check comes first |
| `has_health_warning` (36) | warning → patron rejected | no warning → patron priced |
| `ride_type == "roller_coaster"` inside the warning (38) | group total reset to 0 and `break`; the fast-lane fee is still added | water or family ride → only that patron is skipped |
| `height_cm < 120` (42) | `1`, `119`, and a 110 cm child | `120`, `121` |
| `is_child` (45) | child at 120 cm → 60% price, for each ride | adult at 120 cm → full price |
| `group.get("has_fast_lane", False)` (50) | fee added once per group, not per patron | `False` or the key missing |
| `rejected_patrons > 4` (55) | 5 rejections, also counted across groups and reasons | exactly 4 |
| `total_revenue == 0.0` (57) | every patron rejected; fast lane with a fee of 0 | positive revenue, rounded (3 × 10.8 = 32.4) |
| `not restraint_streams` (63) | `[]` and `None` → `NO_DATA` | `[[]]` → `SAFE` |
| `for sensor_readings in restraint_streams` (66) | several streams | all streams read → `SAFE` |
| `for sensor_val in sensor_readings` (68) | readings processed | stream finished (or empty) → next stream |
| `sensor_val == 0` (69) | `0` → streak + 1 | `1`, `2`, `5`, `7` → streak reset to 0 |
| `unlatched_streak >= 2` (71) | `[0, 0]`, `[0, 1, 0, 0]`, a pair in the second stream → `EMERGENCY_LOCK` | `[0]`, `[0, 1, 0]`, `[[1, 0], [0, 1]]` → keep reading |

## Branch coverage result

The branch coverage suite was run on its own, with `--branch`. The
branch-only percentage was read from the JSON report of the same run
(`covered_branches / num_branches`):

| Measurement | Result |
|---|---|
| Tests | 69 passed |
| Statements | 58 total, 58 covered, 0 missing |
| Branches | 40 total, 40 covered, 0 missing, 0 partial |
| Line coverage | 58 / 58 × 100 = 100.00% |
| **Branch coverage** | **40 / 40 × 100 = 100.00%** (baseline 16 / 40 = 40.00%) |
| Combined `Cover` column | 100% |

```text
Name                            Stmts   Miss Branch BrPart  Cover   Missing
---------------------------------------------------------------------------
amusement_park_ride_access.py      58      0     40      0   100%
---------------------------------------------------------------------------
TOTAL                              58      0     40      0   100%

Wrote JSON report to .coverage_branch.json
Branch coverage: 40/40 = 100.00%
```

## Test files

| File | Purpose |
|---|---|
| `test_amusement_park.py` | the original starter test (one test, unchanged) |
| `CodeCoverageTest_11_amusement_park_ride_access.py` | 21 test cases written for line coverage: every block of statements of both functions |
| `BranchCoverageTest_11_amusement_park_ride_access.py` | 69 test cases written for branch coverage: the true and false outcome of all 20 decisions, with boundary values |

## Screenshots

Both screenshots are captures of the Windows PowerShell window, in this folder
with the virtual environment active (`(.venv)` in the prompt).

| Screenshot | What it shows |
|---|---|
| [`screenshots/code_coverage.png`](screenshots/code_coverage.png) | the `coverage run` command for the code coverage suite, the pytest result (21 passed) and `coverage report -m` with 58 statements, 0 missing, **100%** |
| [`screenshots/branch_coverage.png`](screenshots/branch_coverage.png) | the `coverage run --branch` command for the branch coverage suite, the pytest result (69 passed), `coverage report -m` with 40 branches and 0 partial, the JSON export and the branch-only result **Branch coverage: 40/40 = 100.00%** |

## Setting up the virtual environment

Run these commands in Windows PowerShell from this folder
(`Lab-6_Code_and_Branch_Coverage/PES1UG24CS316_Lab6_amusement_park_ride_access`):

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install --upgrade pip
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\Activate.ps1
```

If PowerShell blocks `Activate.ps1`, allow scripts for the current window
only with `Set-ExecutionPolicy -Scope Process -ExecutionPolicy RemoteSigned`
and activate again. The prompt then starts with `(.venv)`.

## Running the starter test

Line coverage:

```powershell
coverage run --data-file=.coverage_baseline_line --source=amusement_park_ride_access -m pytest test_amusement_park.py
coverage report --data-file=.coverage_baseline_line -m
```

Branch coverage:

```powershell
coverage run --data-file=.coverage_baseline_branch --branch --source=amusement_park_ride_access -m pytest test_amusement_park.py
coverage report --data-file=.coverage_baseline_branch -m
```

## Running the code coverage tests

```powershell
coverage run --data-file=.coverage_code --source=amusement_park_ride_access -m pytest -q CodeCoverageTest_11_amusement_park_ride_access.py
coverage report --data-file=.coverage_code -m
```

## Running the branch coverage tests

```powershell
coverage run --data-file=.coverage_branch --branch --source=amusement_park_ride_access -m pytest -q BranchCoverageTest_11_amusement_park_ride_access.py
coverage report --data-file=.coverage_branch -m
coverage json --data-file=.coverage_branch -o .coverage_branch.json
python -c "import json; t=json.load(open('.coverage_branch.json', encoding='utf-8'))['totals']; print('Branch coverage: {}/{} = {:.2f}%'.format(t['covered_branches'], t['num_branches'], t['percent_branches_covered']))"
```

The last command reads the totals from the JSON report and prints covered
branches / total branches and the branch-only percentage. Before running the
commands a second time, delete the old JSON report
(`Remove-Item .coverage_branch.json`): Coverage.py treats files named
`.coverage_branch.*` as extra data files and would print a warning about it.

## Two separate coverage measurements

| | Line (code) coverage run | Branch coverage run |
|---|---|---|
| Test file | `CodeCoverageTest_11_amusement_park_ride_access.py` | `BranchCoverageTest_11_amusement_park_ride_access.py` |
| Coverage option | none (statements only) | `--branch` |
| Data file | `.coverage_code` | `.coverage_branch` |
| Report columns | `Stmts`, `Miss`, `Cover` | also `Branch` and `BrPart` (partially covered decision lines) |
| Percentage | covered statements / statements | covered branches / branches, from the JSON report |

In the branch run, the `Cover` column of `coverage report` is a **combined**
figure: (covered statements + covered branches) / (statements + branches). It
is not the branch percentage. For the starter test it showed 45%
((28 + 16) / (58 + 40)), while the branch-only coverage was 40%
(16 / 40). This is why the branch percentage is calculated separately from the
JSON report.

In this module, every `if` has a statement on both its true and its false
side, so running every line also takes every branch: the code coverage suite
also reaches 40 / 40 branches when it is run with `--branch`. This is
different from the handout's `calculate_discount` example, where an `if`
without an `else` gives a branch with no line of its own. The branch suite is
still needed for the boundary cases (for example a height of exactly 120 cm,
exactly 4 rejections, or a fee of 0), which line coverage alone does not ask
for.

## Git commits

| # | Commit message | Contents |
|---|---|---|
| 1 | `chore(lab6): add amusement park ride access starter` | the original application and starter test, the Lab 6 handout, `.gitignore`, `.gitattributes` and `requirements.txt` |
| 2 | `test(lab6): add code coverage tests and screenshot` | `CodeCoverageTest_11_amusement_park_ride_access.py` and `screenshots/code_coverage.png` |
| 3 | `test(lab6): add branch coverage tests and screenshot` | `BranchCoverageTest_11_amusement_park_ride_access.py`, `screenshots/branch_coverage.png`, this README and the Lab 6 entry in the root README |

`.gitattributes` keeps the two original files byte-for-byte as supplied (CRLF
line endings), which Git would otherwise convert on this computer.

## Folder contents

| File | Description |
|---|---|
| `amusement_park_ride_access.py` | the application under test (original) |
| `test_amusement_park.py` | the starter test (original) |
| `CodeCoverageTest_11_amusement_park_ride_access.py` | line (code) coverage tests |
| `BranchCoverageTest_11_amusement_park_ride_access.py` | branch coverage tests |
| `requirements.txt` | pinned versions of pytest and Coverage.py |
| `screenshots/code_coverage.png` | terminal screenshot of the final line coverage run |
| `screenshots/branch_coverage.png` | terminal screenshot of the final branch coverage run |

The Lab 6 handout PDF is in the parent folder, `Lab-6_Code_and_Branch_Coverage/`.
