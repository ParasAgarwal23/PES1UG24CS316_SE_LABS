"""Code (line) coverage tests for amusement_park_ride_access.py.

Each test runs one block of statements of the module, so that together they
execute every line of process_ride_admissions() and
inspect_safety_restraints() at least once.
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


# ---------------------------------------------------------------------------
# process_ride_admissions(): input validation
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("groups, fee", [
    ("roller_coaster", 5.0),   # groups is not a list
    ([], -5.0),                # negative express pass fee
])
def test_invalid_input_raises_value_error(groups, fee):
    with pytest.raises(ValueError, match="Invalid groups list or pass fee"):
        process_ride_admissions(groups, fee)


# ---------------------------------------------------------------------------
# process_ride_admissions(): ticket prices and the fast lane
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("ride_type, expected_revenue", [
    ("roller_coaster", 25.0),
    ("water_ride", 18.0),
    ("family", 10.0),
])
def test_adult_pays_full_ticket_for_each_ride(ride_type, expected_revenue):
    groups = [make_group(ride_type, [make_patron(150)])]
    result = process_ride_admissions(groups, 5.0)
    assert result["total_revenue"] == expected_revenue
    assert result["status"] == "COMPLETED"


def test_missing_ride_type_is_priced_as_family_ride():
    groups = [{"is_open": True, "patrons": [make_patron(150)]}]
    result = process_ride_admissions(groups, 5.0)
    assert result["total_revenue"] == 10.0
    assert result["status"] == "COMPLETED"


@pytest.mark.parametrize("ride_type, expected_revenue", [
    ("roller_coaster", 15.0),
    ("water_ride", 10.8),      # 18.0 * 0.60 is 10.799999999999999 before rounding
    ("family", 6.0),
])
def test_child_pays_sixty_percent_of_ticket(ride_type, expected_revenue):
    groups = [make_group(ride_type, [make_patron(130, is_child=True)])]
    result = process_ride_admissions(groups, 5.0)
    assert result["total_revenue"] == expected_revenue
    assert result["status"] == "COMPLETED"


def test_fast_lane_fee_is_added_once_per_group():
    patrons = [make_patron(150), make_patron(140, is_child=True)]
    groups = [make_group("water_ride", patrons, has_fast_lane=True)]
    result = process_ride_admissions(groups, 7.5)
    assert result["total_revenue"] == 36.3   # 18.0 + 10.8 + 7.5
    assert result["status"] == "COMPLETED"


# ---------------------------------------------------------------------------
# process_ride_admissions(): groups and patrons that are skipped or rejected
# ---------------------------------------------------------------------------

def test_closed_group_is_skipped():
    groups = [make_group("family", [make_patron(150)], has_fast_lane=True, is_open=False)]
    result = process_ride_admissions(groups, 5.0)
    assert result["total_revenue"] == 0.0
    assert result["status"] == "ZERO_ADMISSIONS"


def test_unknown_ride_type_rejects_the_group():
    # The group is skipped before the fast-lane fee is added.
    groups = [make_group("haunted_house", [make_patron(150)], has_fast_lane=True)]
    result = process_ride_admissions(groups, 5.0)
    assert result["total_revenue"] == 0.0
    assert result["status"] == "ZERO_ADMISSIONS"


def test_patron_with_invalid_height_is_rejected():
    groups = [make_group("family", [make_patron(0), make_patron(150)])]
    result = process_ride_admissions(groups, 5.0)
    assert result["total_revenue"] == 10.0
    assert result["status"] == "COMPLETED"


def test_patron_shorter_than_120_cm_is_rejected():
    groups = [make_group("water_ride", [make_patron(110), make_patron(150)])]
    result = process_ride_admissions(groups, 5.0)
    assert result["total_revenue"] == 18.0
    assert result["status"] == "COMPLETED"


# ---------------------------------------------------------------------------
# process_ride_admissions(): health warnings
# ---------------------------------------------------------------------------

def test_health_warning_cancels_whole_roller_coaster_group():
    # The adult already charged is wiped out and the last patron is never checked.
    patrons = [make_patron(150), make_patron(160, health_warning=True), make_patron(170)]
    groups = [make_group("roller_coaster", patrons)]
    result = process_ride_admissions(groups, 5.0)
    assert result["total_revenue"] == 0.0
    assert result["status"] == "ZERO_ADMISSIONS"


def test_health_warning_on_other_ride_rejects_only_that_patron():
    patrons = [make_patron(150, health_warning=True), make_patron(150)]
    groups = [make_group("family", patrons)]
    result = process_ride_admissions(groups, 5.0)
    assert result["total_revenue"] == 10.0
    assert result["status"] == "COMPLETED"


# ---------------------------------------------------------------------------
# process_ride_admissions(): final status and total revenue
# ---------------------------------------------------------------------------

def test_more_than_four_rejections_triggers_safety_audit():
    # Five rejected patrons (four too short, one invalid height) and one adult.
    patrons = [make_patron(100), make_patron(105), make_patron(110),
               make_patron(115), make_patron(0), make_patron(150)]
    result = process_ride_admissions([make_group("family", patrons)], 5.0)
    assert result["total_revenue"] == 10.0
    assert result["status"] == "SAFETY_AUDIT"


def test_revenue_of_several_groups_is_added_and_rounded():
    groups = [
        make_group("roller_coaster", [make_patron(180), make_patron(125, is_child=True)],
                   has_fast_lane=True),
        make_group("water_ride", [make_patron(130, is_child=True),
                                  make_patron(135, is_child=True)]),
        make_group("family", [make_patron(150)], is_open=False),
    ]
    result = process_ride_admissions(groups, 4.99)
    # (25.0 + 15.0 + 4.99) + (10.8 + 10.8); the closed group adds nothing
    assert result["total_revenue"] == 66.59
    assert result["status"] == "COMPLETED"


# ---------------------------------------------------------------------------
# inspect_safety_restraints()
# ---------------------------------------------------------------------------

def test_no_restraint_data():
    assert inspect_safety_restraints([]) == "NO_DATA"


def test_restraints_without_two_unlatched_readings_in_a_row_are_safe():
    # A single unlatched reading (0) followed by a latched one is allowed.
    assert inspect_safety_restraints([[1, 1, 1], [1, 0, 1]]) == "SAFE"


def test_two_unlatched_readings_in_a_row_lock_the_ride():
    assert inspect_safety_restraints([[1, 1], [1, 0, 0, 1]]) == "EMERGENCY_LOCK"
