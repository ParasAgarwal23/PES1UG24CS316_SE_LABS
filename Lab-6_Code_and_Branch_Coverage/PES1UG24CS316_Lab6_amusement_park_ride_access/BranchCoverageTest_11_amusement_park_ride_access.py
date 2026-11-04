"""Branch coverage tests for amusement_park_ride_access.py.

The tests are grouped by decision. Every if/elif is tested with a case where
it is true and a case where it is false, and every for loop with a case where
its body runs and one where it ends (or never starts). Boundary values are
used for each comparison: fee 0, height 0 and 120, 4 and 5 rejections, and an
unlatched streak of 1 and 2.
"""
import pytest
from amusement_park_ride_access import process_ride_admissions, inspect_safety_restraints


def make_patron(height_cm, is_child=False, health_warning=False):
    return {"height_cm": height_cm, "health_warning": health_warning, "is_child": is_child}


def make_group(ride_type, patrons, has_fast_lane=False, is_open=True):
    return {
        "is_open": is_open,
        "ride_type": ride_type,
        "has_fast_lane": has_fast_lane,
        "patrons": patrons,
    }


def admit(groups, fee=5.0):
    """Run process_ride_admissions() and return (total_revenue, status)."""
    result = process_ride_admissions(groups, fee)
    return result["total_revenue"], result["status"]


# ---------------------------------------------------------------------------
# Decision: if not isinstance(groups, list) or express_pass_fee < 0
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("groups, fee", [
    (("family",), 5.0),   # true: a tuple is not a list
    (None, 5.0),          # true: no groups at all
    ([], -0.01),          # true: a list, but the fee is just below zero
])
def test_validation_true_raises_value_error(groups, fee):
    with pytest.raises(ValueError, match="Invalid groups list or pass fee"):
        process_ride_admissions(groups, fee)


@pytest.mark.parametrize("fee", [0.0, 12.5])
def test_validation_false_for_list_and_non_negative_fee(fee):
    # A fee of exactly 0 is allowed. With an empty list the group loop never runs.
    assert admit([], fee) == (0.0, "ZERO_ADMISSIONS")


# ---------------------------------------------------------------------------
# Loop: for group in groups
# ---------------------------------------------------------------------------

def test_group_loop_processes_every_group():
    groups = [
        make_group("roller_coaster", [make_patron(150)]),
        make_group("water_ride", [make_patron(150)]),
        make_group("family", [make_patron(150)]),
    ]
    assert admit(groups) == (53.0, "COMPLETED")


# ---------------------------------------------------------------------------
# Decision: if not group.get("is_open", False)
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("is_open, expected", [
    (True, (10.0, "COMPLETED")),          # false: the group is processed
    (False, (0.0, "ZERO_ADMISSIONS")),    # true: the group is skipped
])
def test_open_and_closed_group(is_open, expected):
    assert admit([make_group("family", [make_patron(150)], is_open=is_open)]) == expected


def test_group_without_is_open_key_is_treated_as_closed():
    group = {"ride_type": "family", "patrons": [make_patron(150)]}
    assert admit([group]) == (0.0, "ZERO_ADMISSIONS")


def test_closed_group_patrons_are_not_counted_as_rejections():
    # Five patrons who would all be rejected, but the group is closed.
    group = make_group("family", [make_patron(100)] * 5, is_open=False)
    assert admit([group]) == (0.0, "ZERO_ADMISSIONS")


# ---------------------------------------------------------------------------
# Decisions: if ride_type == "roller_coaster" / elif "water_ride" /
#            elif "family" / else (unknown ride)
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("ride_type, expected", [
    ("roller_coaster", (25.0, "COMPLETED")),       # first condition true
    ("water_ride", (18.0, "COMPLETED")),           # first false, second true
    ("family", (10.0, "COMPLETED")),               # first two false, third true
    ("bumper_cars", (0.0, "ZERO_ADMISSIONS")),     # all false: else branch
    ("Roller_Coaster", (0.0, "ZERO_ADMISSIONS")),  # the comparison is case-sensitive
])
def test_ride_type_selection(ride_type, expected):
    assert admit([make_group(ride_type, [make_patron(150)])]) == expected


def test_missing_ride_type_takes_the_family_branch():
    group = {"is_open": True, "patrons": [make_patron(150)]}
    assert admit([group]) == (10.0, "COMPLETED")


def test_unknown_ride_type_skips_the_fast_lane_fee():
    group = make_group("bumper_cars", [make_patron(150)], has_fast_lane=True)
    assert admit([group]) == (0.0, "ZERO_ADMISSIONS")


def test_each_unknown_ride_group_counts_as_one_rejection():
    # Five unknown-ride groups give five rejections, although each has two patrons.
    groups = [make_group("go_karts", [make_patron(150), make_patron(150)])] * 5
    assert admit(groups) == (0.0, "SAFETY_AUDIT")


# ---------------------------------------------------------------------------
# Loop: for patron in patrons
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("group", [
    {"is_open": True, "ride_type": "water_ride", "has_fast_lane": True, "patrons": []},
    {"is_open": True, "ride_type": "water_ride", "has_fast_lane": True},  # no "patrons" key
])
def test_group_with_no_patrons_still_pays_fast_lane_fee(group):
    # The patron loop ends straight away; only the fast-lane fee is charged.
    assert admit([group], 6.0) == (6.0, "COMPLETED")


# ---------------------------------------------------------------------------
# Decision: if height_cm <= 0
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("patron, expected", [
    ({"height_cm": -10}, (0.0, "ZERO_ADMISSIONS")),   # true
    ({"height_cm": 0}, (0.0, "ZERO_ADMISSIONS")),     # true: boundary
    ({}, (0.0, "ZERO_ADMISSIONS")),                   # true: a missing height counts as 0
    ({"height_cm": 150}, (10.0, "COMPLETED")),        # false
])
def test_invalid_height(patron, expected):
    assert admit([make_group("family", [patron])]) == expected


def test_invalid_height_is_checked_before_health_warning():
    # The first patron is rejected for the height, so the roller coaster group
    # is not cancelled and the second patron still pays.
    patrons = [make_patron(0, health_warning=True), make_patron(150)]
    assert admit([make_group("roller_coaster", patrons)]) == (25.0, "COMPLETED")


# ---------------------------------------------------------------------------
# Decision: if has_health_warning
#   and the nested decision: if ride_type == "roller_coaster"
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("health_warning, expected", [
    (True, (0.0, "ZERO_ADMISSIONS")),    # true: patron rejected
    (False, (25.0, "COMPLETED")),        # false: patron goes on to the height check
])
def test_health_warning_true_and_false(health_warning, expected):
    patrons = [make_patron(150, health_warning=health_warning)]
    assert admit([make_group("roller_coaster", patrons)]) == expected


@pytest.mark.parametrize("ride_type, expected", [
    ("roller_coaster", (0.0, "ZERO_ADMISSIONS")),  # nested if true: total reset, loop broken
    ("water_ride", (36.0, "COMPLETED")),           # nested if false: only this patron skipped
    ("family", (20.0, "COMPLETED")),
])
def test_health_warning_on_roller_coaster_and_other_rides(ride_type, expected):
    patrons = [make_patron(150), make_patron(150, health_warning=True), make_patron(150)]
    assert admit([make_group(ride_type, patrons)]) == expected


def test_break_on_roller_coaster_stops_counting_rejections():
    patrons = [make_patron(150, health_warning=True)] + [make_patron(100)] * 4
    # Roller coaster: the loop breaks at the first patron, so there is only 1 rejection.
    assert admit([make_group("roller_coaster", patrons)]) == (0.0, "ZERO_ADMISSIONS")
    # Family ride: the loop continues, so all 5 patrons are rejected.
    assert admit([make_group("family", patrons)]) == (0.0, "SAFETY_AUDIT")


def test_cancelled_roller_coaster_group_keeps_fast_lane_fee():
    patrons = [make_patron(150), make_patron(150, health_warning=True)]
    groups = [
        make_group("roller_coaster", patrons, has_fast_lane=True),
        make_group("family", [make_patron(150)]),
    ]
    # The roller coaster tickets are wiped, but its fee is added after the
    # patron loop: 5.0 + 10.0
    assert admit(groups, 5.0) == (15.0, "COMPLETED")


# ---------------------------------------------------------------------------
# Decision: elif height_cm < 120
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("height_cm, expected", [
    (1, (0.0, "ZERO_ADMISSIONS")),       # true: smallest valid height
    (119, (0.0, "ZERO_ADMISSIONS")),     # true: just below the limit
    (120, (18.0, "COMPLETED")),          # false: exactly the limit is allowed
    (121, (18.0, "COMPLETED")),          # false
])
def test_height_limit_boundary(height_cm, expected):
    assert admit([make_group("water_ride", [make_patron(height_cm)])]) == expected


def test_short_child_is_rejected_before_child_pricing():
    group = make_group("family", [make_patron(110, is_child=True)])
    assert admit([group]) == (0.0, "ZERO_ADMISSIONS")


# ---------------------------------------------------------------------------
# Decision: elif is_child (else: adult price)
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("ride_type, is_child, expected_revenue", [
    ("roller_coaster", True, 15.0),
    ("roller_coaster", False, 25.0),
    ("water_ride", True, 10.8),
    ("water_ride", False, 18.0),
    ("family", True, 6.0),
    ("family", False, 10.0),
])
def test_child_and_adult_price_at_height_limit(ride_type, is_child, expected_revenue):
    group = make_group(ride_type, [make_patron(120, is_child=is_child)])
    assert admit([group]) == (expected_revenue, "COMPLETED")


# ---------------------------------------------------------------------------
# Decision: if group.get("has_fast_lane", False)
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("has_fast_lane, expected_revenue", [
    (True, 17.5),    # true: fee added
    (False, 10.0),   # false: no fee
])
def test_fast_lane_true_and_false(has_fast_lane, expected_revenue):
    group = make_group("family", [make_patron(150)], has_fast_lane=has_fast_lane)
    assert admit([group], 7.5) == (expected_revenue, "COMPLETED")


def test_group_without_fast_lane_key_pays_no_fee():
    group = {"is_open": True, "ride_type": "family", "patrons": [make_patron(150)]}
    assert admit([group], 7.5) == (10.0, "COMPLETED")


def test_fast_lane_fee_is_charged_once_per_group_not_per_patron():
    group = make_group("family", [make_patron(150)] * 3, has_fast_lane=True)
    assert admit([group], 7.5) == (37.5, "COMPLETED")


# ---------------------------------------------------------------------------
# Decision: if rejected_patrons > 4
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("rejected, expected", [
    (4, (10.0, "COMPLETED")),      # false: exactly 4 is still allowed
    (5, (10.0, "SAFETY_AUDIT")),   # true
])
def test_safety_audit_boundary(rejected, expected):
    patrons = [make_patron(150)] + [make_patron(100)] * rejected
    assert admit([make_group("family", patrons)]) == expected


def test_rejections_from_every_reason_and_group_add_up():
    groups = [
        # 1 rejection: unknown ride type
        make_group("bumper_cars", [make_patron(150)]),
        # 2 rejections: height 0 and too short
        make_group("family", [make_patron(0), make_patron(110)]),
        # 1 rejection: health warning; the child still pays 10.8
        make_group("water_ride", [make_patron(150, health_warning=True),
                                  make_patron(130, is_child=True)]),
        # 1 rejection: negative height
        make_group("family", [make_patron(-5)]),
    ]
    # 5 rejections in total, so the audit status comes with the rounded revenue.
    assert admit(groups) == (10.8, "SAFETY_AUDIT")


# ---------------------------------------------------------------------------
# Decision: if total_revenue == 0.0 (else: COMPLETED with rounded revenue)
# ---------------------------------------------------------------------------

def test_zero_revenue_gives_zero_admissions():
    group = make_group("water_ride", [make_patron(100), make_patron(0)])
    assert admit([group]) == (0.0, "ZERO_ADMISSIONS")


def test_zero_fast_lane_fee_alone_is_still_zero_admissions():
    group = make_group("family", [], has_fast_lane=True)
    assert admit([group], 0.0) == (0.0, "ZERO_ADMISSIONS")


def test_positive_revenue_is_completed_and_rounded():
    # Three water-ride children: 3 * 10.799999999999999 is rounded to 32.4.
    group = make_group("water_ride", [make_patron(130, is_child=True)] * 3)
    assert admit([group]) == (32.4, "COMPLETED")


# ---------------------------------------------------------------------------
# inspect_safety_restraints(): if not restraint_streams
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("streams", [[], None])
def test_no_restraint_data(streams):
    assert inspect_safety_restraints(streams) == "NO_DATA"


def test_stream_without_readings_is_not_no_data():
    # [[]] is not empty, so the check is false; the inner loop then never runs.
    assert inspect_safety_restraints([[]]) == "SAFE"


# ---------------------------------------------------------------------------
# Decisions: if sensor_val == 0 / if unlatched_streak >= 2
#            (else: a latched reading resets the streak)
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("readings, expected", [
    ([1, 1, 1], "SAFE"),                 # sensor_val == 0 is always false
    ([2, 7], "SAFE"),                    # any non-zero value means latched
    ([0], "SAFE"),                       # == 0 true, streak 1, so >= 2 is false
    ([1, 0], "SAFE"),                    # a single unlatched reading at the end
    ([0, 0], "EMERGENCY_LOCK"),          # streak 2, so >= 2 is true
    ([1, 0, 0, 1], "EMERGENCY_LOCK"),
    ([0, 1, 0], "SAFE"),                 # the latched reading resets the streak
    ([0, 1, 0, 0], "EMERGENCY_LOCK"),    # a later pair still locks
    ([0, 5, 0, 5, 0], "SAFE"),
])
def test_unlatched_streak_in_one_stream(readings, expected):
    assert inspect_safety_restraints([readings]) == expected


# ---------------------------------------------------------------------------
# Loop: for sensor_readings in restraint_streams (the streak restarts per stream)
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("streams, expected", [
    ([[1, 0], [0, 1]], "SAFE"),                  # zeros in different streams are not consecutive
    ([[1, 1, 1], [1, 0, 0]], "EMERGENCY_LOCK"),  # the second stream locks
    ([[0, 0], [1, 1]], "EMERGENCY_LOCK"),        # the first stream locks; the second is never read
    ([[1], [1], [1]], "SAFE"),                   # every stream is read to the end
])
def test_several_restraint_streams(streams, expected):
    assert inspect_safety_restraints(streams) == expected
