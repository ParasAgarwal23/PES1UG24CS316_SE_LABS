# Lab 7 — Fuzzing for Input Validation Bugs

**Name:** Paras Agarwal  
**SRN:** PES1UG24CS316  
**Section:** F

**Course:** Software Engineering  
**Assigned project:** Amusement Park Ride Access (repository index 11, `Lab 7`
folder of [SETAPESU26/L6_L7_11_amusement_park_ride_access](https://github.com/SETAPESU26/L6_L7_11_amusement_park_ride_access))

## Objective

To explore fuzz testing as a security and quality assurance technique by
identifying and fixing bugs in the provided Python script using the
**Hypothesis** fuzzing library.

## The application

`processor.py` reads three values from the user in `main()` and passes them to
three functions:

| Function | Input | Output |
|---|---|---|
| `validate_height_and_fastpass(rider_spec)` | `Height:FastPass`, e.g. `140:YES` | `Height 140cm: Approved (FastPass Priority)`; 120 cm or taller is Approved, YES/NO selects FastPass Priority or Standard Entry |
| `compute_dispatch_throughput(ride_metric_str)` | `riders/mins`, e.g. `48/2.5` | riders per minute rounded to 2 decimal places (`19.2`) |
| `resolve_safety_restraint_code(zone_code)` | zone code, e.g. `CST_01` | restraint for the first three letters (CST, WTR, DRP or WHL) |

## Fuzz testing approach

The three starter tests in `test_processor.py` were completed with the
try/except pattern from the handout and six more `@given` property tests were
added (nine in total: four for `validate_height_and_fastpass`, three for
`compute_dispatch_throughput` and two for `resolve_safety_restraint_code`).
A `ValueError` or `TypeError` counts as a controlled rejection of bad input;
any other exception, or an impossible result, is a bug.

Strategies used: `st.text() | st.none()`, `st.integers()` (valid, zero and
negative heights), `st.floats()` (zero, negative, nan, inf), `st.sampled_from()`
and `st.booleans()`, and structured inputs such as `f"{height}:{fastpass}"`.

Properties checked:

- no function crashes on random or malformed input;
- valid input gives the correct result (120 cm boundary, `round(riders / mins, 2)`,
  the four known restraints in any letter case);
- heights of zero or less are rejected;
- a returned throughput is always finite and non-negative;
- a returned restraint is always one of the four known restraints.

## Bugs found and fixes

Against the original `processor.py` the suite gave **6 failed, 3 passed**.
Minimized failing inputs reported by Hypothesis:

| Bug discovered | Fix applied |
|---|---|
| All three functions crash with `AttributeError` on `None` | `isinstance(..., str)` check, raises `TypeError` |
| `validate_height_and_fastpass('1:')` crashes with `KeyError: ''` (FastPass not YES/NO) | FastPass value checked, raises `ValueError` |
| `validate_height_and_fastpass('0:YES')` accepts a 0 cm height | heights `<= 0` raise `ValueError` |
| `compute_dispatch_throughput('0.0/0.0')` crashes with `ZeroDivisionError` | cycle minutes must be finite and `> 0` |
| `compute_dispatch_throughput('1.0/-1.0')` returns `-1.0` | riders must be finite and `>= 0`; result checked with `math.isfinite` |
| `resolve_safety_restraint_code('')` crashes with `KeyError: ''` | unknown prefix raises `ValueError` |

Both input formats are also checked for exactly one separator (`:` or `/`), and
`main()` catches `ValueError` and prints a clear message instead of a
traceback. Function names, parameters and the output for valid input are
unchanged.

## How to run

Install the dependencies (a local virtual environment was used):

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install hypothesis
pip install pytest
```

Run the application:

```powershell
python processor.py
```

Run the Hypothesis tests:

```powershell
python -m pytest test_processor.py
```

## Results

| Run | Result |
|---|---|
| Hypothesis tests against the original `processor.py` | 6 failed, 3 passed |
| Hypothesis tests against the fixed `processor.py` | **9 passed** |

The test file was not changed between the two runs; only `processor.py` was
fixed. Tested with Python 3.13.7, pytest 9.2.0 and Hypothesis 6.170.15.

## Deliverables

```text
Lab-7_Fuzzing_for_Input_Validation_Bugs/
├── processor.py
├── test_processor.py
├── README.md
├── Lab7_Fuzzing_Report.pdf
└── screenshots/
    ├── 01_original_application.png
    ├── 02_hypothesis_failures.png
    ├── 03_fixed_application.png
    └── 04_hypothesis_passing.png
```

| File | Description |
|---|---|
| `processor.py` | the fixed application |
| `test_processor.py` | the completed Hypothesis fuzz tests |
| `Lab7_Fuzzing_Report.pdf` | lab report with the screenshots, the bugs found and the fixes |
| `screenshots/` | the four terminal screenshots: original execution, initial failures, fixed execution and final passing tests |

In `02_hypothesis_failures.png` the test command is run with `--tb=no` so that
the command and the full summary fit on one screen; this only hides the
tracebacks.
