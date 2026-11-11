import math

import pytest
from hypothesis import given, strategies as st
from processor import validate_height_and_fastpass, compute_dispatch_throughput, resolve_safety_restraint_code

RESTRAINTS = {
    "CST": "Over-the-Shoulder Harness",
    "WTR": "Lap Bar and Seatbelt",
    "DRP": "Hydraulic Shoulder Vest",
    "WHL": "Manual Safety Bar",
}

@given(st.text() | st.none())
def test_validate_height_and_fastpass_no_crash(s):
    try:
        result = validate_height_and_fastpass(s)
    except (ValueError, TypeError):
        return
    except Exception as e:
        assert False, f"validate_height_and_fastpass crashed on {s!r} with {type(e).__name__}: {e}"
    assert isinstance(result, str)

@given(st.integers(min_value=1), st.sampled_from(["YES", "NO", "yes", "no", " Yes "]))
def test_validate_height_and_fastpass_valid_spec(height, fastpass):
    result = validate_height_and_fastpass(f"{height}:{fastpass}")
    decision = "Approved" if height >= 120 else "Denied"
    status = "FastPass Priority" if fastpass.strip().upper() == "YES" else "Standard Entry"
    assert result == f"Height {height}cm: {decision} ({status})"

@given(st.integers(min_value=1, max_value=300), st.text())
def test_validate_height_and_fastpass_random_fastpass(height, fastpass):
    try:
        result = validate_height_and_fastpass(f"{height}:{fastpass}")
    except ValueError:
        return
    except Exception as e:
        assert False, f"validate_height_and_fastpass crashed on '{height}:{fastpass}' with {type(e).__name__}: {e}"
    assert fastpass.strip().upper() in ("YES", "NO"), f"FastPass {fastpass!r} was accepted: {result}"

@given(st.integers(max_value=0), st.sampled_from(["YES", "NO"]))
def test_validate_height_and_fastpass_rejects_invalid_height(height, fastpass):
    with pytest.raises(ValueError):
        validate_height_and_fastpass(f"{height}:{fastpass}")

@given(st.text() | st.none())
def test_compute_dispatch_throughput_safe(s):
    try:
        result = compute_dispatch_throughput(s)
    except (ValueError, TypeError):
        return
    except Exception as e:
        assert False, f"compute_dispatch_throughput crashed on {s!r} with {type(e).__name__}: {e}"
    assert math.isfinite(result) and result >= 0

@given(st.integers(min_value=0, max_value=10000), st.floats(min_value=0.1, max_value=120))
def test_compute_dispatch_throughput_valid_metric(riders, mins):
    assert compute_dispatch_throughput(f"{riders}/{mins}") == round(riders / mins, 2)

@given(st.floats(), st.floats())
def test_compute_dispatch_throughput_numeric_edge_cases(riders, mins):
    try:
        result = compute_dispatch_throughput(f"{riders}/{mins}")
    except ValueError:
        return
    except Exception as e:
        assert False, f"compute_dispatch_throughput crashed on '{riders}/{mins}' with {type(e).__name__}: {e}"
    assert math.isfinite(result) and result >= 0, f"'{riders}/{mins}' gave throughput {result}"

@given(st.text() | st.none())
def test_resolve_safety_restraint_code_safe(s):
    try:
        result = resolve_safety_restraint_code(s)
    except (ValueError, TypeError):
        return
    except Exception as e:
        assert False, f"resolve_safety_restraint_code crashed on {s!r} with {type(e).__name__}: {e}"
    assert result in RESTRAINTS.values()

@given(st.sampled_from(sorted(RESTRAINTS)), st.text(alphabet="ABCXYZ0123456789_-", max_size=5), st.booleans())
def test_resolve_safety_restraint_code_known_zones(prefix, suffix, lowercase):
    code = prefix + suffix
    if lowercase:
        code = code.lower()
    assert resolve_safety_restraint_code(code) == RESTRAINTS[prefix]
