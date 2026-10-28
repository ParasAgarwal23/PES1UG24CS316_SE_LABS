"""Student Scholarship Eligibility Screener.

Scores applicants from GPA and extracurricular credits, shortlists those
whose merit score reaches CUTOFF and whose family income is below
INCOME_LIMIT, and saves the results to a JSON file.

The merit formula can be changed at run time. Formulas are untrusted text,
so they are checked and evaluated by a small arithmetic-only interpreter
instead of eval().
"""

import ast
import json
import logging
import math
import operator

LOGGER = logging.getLogger(__name__)

DEFAULT_MERIT_FORMULA = "gpa * 10 + credits * 2"
INCOME_LIMIT = 800000
CUTOFF = 85
MAX_GPA = 10
RESULTS_FILE = "scholarships.json"

# Global state, updated in place: applicant results and the active formula.
results = {}
settings = {"merit_formula": DEFAULT_MERIT_FORMULA}

# Merit formulas are untrusted text (main() reads one from input), so they are
# checked and evaluated by a small arithmetic-only interpreter, never eval().
FORMULA_VARIABLES = ("gpa", "credits")
MAX_FORMULA_LENGTH = 100
MAX_FORMULA_NODES = 50
_BINARY_OPERATORS = {
    ast.Add: operator.add,
    ast.Sub: operator.sub,
    ast.Mult: operator.mul,
    ast.Div: operator.truediv,
}
_UNARY_OPERATORS = {ast.UAdd: operator.pos, ast.USub: operator.neg}
_ALLOWED_NODES = (ast.Expression, ast.BinOp, ast.UnaryOp, ast.Name, ast.Load,
                  ast.Constant, *_BINARY_OPERATORS, *_UNARY_OPERATORS)

def _is_finite_number(value):
    """Return True for an int or a finite float (bools are rejected)."""
    if isinstance(value, bool):
        return False
    if isinstance(value, int):
        return True
    return isinstance(value, float) and math.isfinite(value)

def _check_formula_node(node):
    """Raise ValueError unless *node* may appear in a merit formula."""
    if not isinstance(node, _ALLOWED_NODES):
        raise ValueError(
            f"{type(node).__name__} is not allowed in a merit formula")
    if isinstance(node, ast.Name) and node.id not in FORMULA_VARIABLES:
        raise ValueError(f"unknown name {node.id!r} in merit formula "
                         f"(allowed: {', '.join(FORMULA_VARIABLES)})")
    if isinstance(node, ast.Constant) and not _is_finite_number(node.value):
        raise ValueError(
            f"constant {node.value!r} is not allowed in a merit formula")

def parse_formula(formula):
    """Check that *formula* is safe arithmetic and return its syntax tree.

    A merit formula may only use the variables gpa and credits, int or float
    constants, parentheses, the operators + - * / and unary + or -. Anything
    else (function calls, attribute access, subscripts, other names, **,
    comparisons, ...) raises ValueError, as does a formula longer than
    MAX_FORMULA_LENGTH characters or with more than MAX_FORMULA_NODES nodes.
    """
    if not isinstance(formula, str):
        raise ValueError("merit formula must be a string")
    formula = formula.strip()
    if not formula:
        raise ValueError("merit formula is empty")
    if len(formula) > MAX_FORMULA_LENGTH:
        raise ValueError(
            f"merit formula is longer than {MAX_FORMULA_LENGTH} characters")
    try:
        tree = ast.parse(formula, mode="eval")
    except SyntaxError as error:
        raise ValueError(
            f"merit formula is not valid syntax ({error.msg})") from error
    nodes = list(ast.walk(tree))
    if len(nodes) > MAX_FORMULA_NODES:
        raise ValueError("merit formula is too complex")
    for node in nodes:
        _check_formula_node(node)
    return tree

def _evaluate(node, variables):
    """Evaluate a formula syntax tree that parse_formula() has checked."""
    if isinstance(node, ast.Expression):
        return _evaluate(node.body, variables)
    if isinstance(node, ast.BinOp):
        operation = _BINARY_OPERATORS[type(node.op)]
        return operation(_evaluate(node.left, variables),
                         _evaluate(node.right, variables))
    if isinstance(node, ast.UnaryOp):
        operation = _UNARY_OPERATORS[type(node.op)]
        return operation(_evaluate(node.operand, variables))
    if isinstance(node, ast.Name):
        return float(variables[node.id])
    if isinstance(node, ast.Constant):
        return float(node.value)
    raise ValueError(
        f"{type(node).__name__} is not allowed in a merit formula")

def calculate_merit_score(gpa, extra_credits):
    """Return the merit score for a GPA and extracurricular credits.

    The active formula sees them as the variables gpa and credits. Raises
    ValueError if the formula is unsafe, divides by zero or does not give a
    finite score.
    """
    tree = parse_formula(settings["merit_formula"])
    try:
        score = _evaluate(tree, {"gpa": gpa, "credits": extra_credits})
    except (ZeroDivisionError, OverflowError) as error:
        raise ValueError(
            f"merit formula cannot be evaluated: {error}") from error
    if not math.isfinite(score):
        raise ValueError(f"merit formula gave a non-finite score ({score})")
    return score

def _validate_scores(test_scores):
    """Return (gpa, extra_credits, income) from an applicant's test scores.

    gpa is required and must be between 0 and MAX_GPA; credits and income
    default to 0 and must not be negative. Every value must be a finite
    number. Raises ValueError listing all the problems found.
    """
    if "gpa" not in test_scores:
        raise ValueError("gpa is required")
    gpa = test_scores["gpa"]
    extra_credits = test_scores.get("credits", 0)
    income = test_scores.get("income", 0)
    problems = []
    for name, value, maximum in (("gpa", gpa, MAX_GPA),
                                 ("credits", extra_credits, None),
                                 ("income", income, None)):
        if not _is_finite_number(value):
            problems.append(f"{name} must be a finite number (got {value!r})")
        elif value < 0 or (maximum is not None and value > maximum):
            limit = (f"between 0 and {maximum}" if maximum is not None
                     else "0 or more")
            problems.append(f"{name} must be {limit} (got {value!r})")
    if problems:
        raise ValueError("; ".join(problems))
    return gpa, extra_credits, income

def evaluate_applicant(student_id, test_scores, logs=None):
    """Score one applicant, record the result and return their eligibility.

    test_scores holds "gpa" and optionally "credits" and "income" (see
    _validate_scores). An applicant is eligible when the merit score is at
    least CUTOFF and income is below INCOME_LIMIT. Invalid data raises
    ValueError and nothing is recorded. If a logs list is passed, a
    "<id> scored <score>" entry is appended to it.
    """
    if not isinstance(student_id, str) or not student_id.strip():
        raise ValueError(
            f"student id must be a non-empty string (got {student_id!r})")
    gpa, extra_credits, income = _validate_scores(test_scores)
    score = calculate_merit_score(gpa, extra_credits)
    eligible = score >= CUTOFF and income < INCOME_LIMIT
    results[student_id] = {"score": score, "eligible": eligible}
    if logs is not None:
        logs.append(f"{student_id} scored {score}")
    return eligible

def change_formula(new_formula):
    """Make new_formula the active merit formula if it is safe arithmetic.

    Raises ValueError, keeping the current formula, if it is not.
    """
    parse_formula(new_formula)
    settings["merit_formula"] = new_formula.strip()

def persist_results(file=RESULTS_FILE):
    """Save the current results to a UTF-8 JSON file.

    Returns True on success. If the file cannot be written (for example, it
    is read-only or its folder does not exist), a warning is logged, the
    in-memory results are kept and False is returned.
    """
    try:
        with open(file, "w", encoding="utf-8") as handle:
            json.dump(results, handle)
    except OSError as error:
        LOGGER.warning("Could not save results to %s: %s", file, error)
        return False
    return True

def _is_valid_results(data):
    """Return True if data has the shape that persist_results() writes."""
    return isinstance(data, dict) and all(
        isinstance(record, dict)
        and _is_finite_number(record.get("score"))
        and isinstance(record.get("eligible"), bool)
        for record in data.values())

def load_results(file=RESULTS_FILE):
    """Replace the in-memory results with those saved in a JSON file.

    Returns True on success. If the file is missing, unreadable or does not
    hold valid results, a warning is logged, the in-memory results are kept
    unchanged and False is returned.
    """
    try:
        with open(file, encoding="utf-8") as handle:
            loaded = json.load(handle)
    except FileNotFoundError:
        LOGGER.warning("No saved results found at %s", file)
        return False
    except (OSError, UnicodeDecodeError, json.JSONDecodeError) as error:
        LOGGER.warning("Could not load results from %s: %s", file, error)
        return False
    if not _is_valid_results(loaded):
        LOGGER.warning("Ignoring %s: it does not contain valid results", file)
        return False
    results.clear()
    results.update(loaded)
    return True

def print_shortlist():
    """Print the id and merit score of every eligible applicant."""
    print("Shortlisted applicants:")
    for student_id, record in results.items():
        if record["eligible"]:
            print(" ", student_id, "score =", record["score"])

def main():
    """Ask for a merit formula, then screen, save and shortlist applicants."""
    formula = input("Merit formula (Enter to keep default): ").strip()
    if formula:
        try:
            change_formula(formula)
        except ValueError as error:
            print(f"Formula rejected: {error}. "
                  f"Keeping {settings['merit_formula']!r}.")
    applicants = [
        ("U001", {"gpa": 9.1, "credits": 4, "income": 450000}),
        ("U002", {"gpa": 7.2, "credits": 1, "income": 300000}),
        # Invalid sample kept to show validation (GPA > 10, negative values).
        ("U003", {"gpa": 12.5, "credits": -3, "income": -1}),
        ("U004", {"gpa": 6.5}),
        ("U005", {"gpa": 8.4, "credits": 3, "income": 600000}),
    ]
    for student_id, test_scores in applicants:
        try:
            evaluate_applicant(student_id, test_scores)
        except ValueError as error:
            print(f"Skipped {student_id}: {error}")
    # Read the file back only if this run's results were saved; otherwise an
    # older file would replace them. The shortlist then comes from memory.
    if persist_results():
        load_results()
    print_shortlist()

if __name__ == "__main__":
    main()
