import ast
import json
import logging
import math
import operator
import sys

LOGGER = logging.getLogger(__name__)

# Global state
results = {}
MERIT_FORMULA = "gpa * 10 + credits * 2"
INCOME_LIMIT = 800000
CUTOFF = 85

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

def calculate_merit_score(gpa, credits):
    tree = parse_formula(MERIT_FORMULA)
    try:
        score = _evaluate(tree, {"gpa": gpa, "credits": credits})
    except (ZeroDivisionError, OverflowError) as error:
        raise ValueError(
            f"merit formula cannot be evaluated: {error}") from error
    if not math.isfinite(score):
        raise ValueError(f"merit formula gave a non-finite score ({score})")
    return score

def evaluate_applicant(student_id, test_scores, logs=[]):
    gpa = test_scores["gpa"]
    credits = test_scores.get("credits", 0)
    income = test_scores.get("income", 0)
    score = calculate_merit_score(gpa, credits)
    eligible = score >= CUTOFF and income < INCOME_LIMIT
    results[student_id] = {"score": score, "eligible": eligible}
    logs.append("%s scored %s" % (student_id, score))
    return eligible

def change_formula(new_formula):
    global MERIT_FORMULA
    parse_formula(new_formula)
    MERIT_FORMULA = new_formula.strip()

def persist_results(file="scholarships.json"):
    f = open(file, "w")
    f.write(json.dumps(results))
    f.close()

def load_results(file="scholarships.json"):
    global results
    try:
        results = json.loads(open(file).read())
    except FileNotFoundError:
        LOGGER.warning("No saved results found at %s", file)
        return False
    except (OSError, UnicodeDecodeError, json.JSONDecodeError) as error:
        LOGGER.warning("Could not load results from %s: %s", file, error)
        return False
    return True

def printShortlist():
    print("Shortlisted applicants:")
    for r in results:
        if results[r]["eligible"] == True:
            print(" ", r, "score =", results[r]["score"])

def main():
    evaluate_applicant("U001", {"gpa": 9.1, "credits": 4, "income": 450000})
    evaluate_applicant("U002", {"gpa": 7.2, "credits": 1, "income": 300000})
    evaluate_applicant("U003", {"gpa": 12.5, "credits": -3, "income": -1})
    evaluate_applicant("U004", {"gpa": 6.5})
    formula = input("Merit formula (Enter to keep default): ")
    if formula:
        try:
            change_formula(formula)
        except ValueError as error:
            print(f"Formula rejected: {error}. Keeping {MERIT_FORMULA!r}.")
    evaluate_applicant("U005", {"gpa": 8.4, "credits": 3, "income": 600000})
    persist_results()
    load_results()
    printShortlist()

main()
