import math

def validate_height_and_fastpass(rider_spec):
    if not isinstance(rider_spec, str):
        raise TypeError("Rider spec must be a string")
    parts = rider_spec.strip().split(':')
    if len(parts) != 2:
        raise ValueError("Rider spec must be in the format Height:FastPass")
    height_str, pass_str = parts
    height = int(height_str)
    if height <= 0:
        raise ValueError("Height must be a positive number of cm")
    pass_map = {"YES": True, "NO": False}
    pass_key = pass_str.strip().upper()
    if pass_key not in pass_map:
        raise ValueError("FastPass must be YES or NO")
    has_fastpass = pass_map[pass_key]
    eligible = height >= 120
    status = "FastPass Priority" if has_fastpass else "Standard Entry"
    return f"Height {height}cm: {'Approved' if eligible else 'Denied'} ({status})"

def compute_dispatch_throughput(ride_metric_str):
    if not isinstance(ride_metric_str, str):
        raise TypeError("Ride metric must be a string")
    parts = ride_metric_str.split('/')
    if len(parts) != 2:
        raise ValueError("Ride metric must be in the format riders/mins")
    riders_str, mins_str = parts
    riders = float(riders_str)
    cycle_mins = float(mins_str)
    if not math.isfinite(riders) or riders < 0:
        raise ValueError("Riders must be a non-negative number")
    if not math.isfinite(cycle_mins) or cycle_mins <= 0:
        raise ValueError("Cycle minutes must be a positive number")
    rate = riders / cycle_mins
    if not math.isfinite(rate):
        raise ValueError("Throughput is too large to calculate")
    return round(rate, 2)

def resolve_safety_restraint_code(zone_code):
    if not isinstance(zone_code, str):
        raise TypeError("Zone code must be a string")
    prefix = zone_code.strip().upper()[:3]
    restraint_types = {
        "CST": "Over-the-Shoulder Harness",
        "WTR": "Lap Bar and Seatbelt",
        "DRP": "Hydraulic Shoulder Vest",
        "WHL": "Manual Safety Bar"
    }
    if prefix not in restraint_types:
        raise ValueError(f"Unknown ride zone code: {zone_code!r}")
    return restraint_types[prefix]

def main():
    print("==== Running validate_height_and_fastpass ====")
    r_input = input("Enter rider spec (Height:FastPass, e.g. 140:YES): ")
    try:
        print(validate_height_and_fastpass(r_input))
    except ValueError as e:
        print("Invalid rider spec:", e)

    print("\n==== Running compute_dispatch_throughput ====")
    t_input = input("Enter riders/mins (e.g. 48/2.5): ")
    try:
        print("Throughput (riders/min):", compute_dispatch_throughput(t_input))
    except ValueError as e:
        print("Invalid ride metric:", e)

    print("\n==== Running resolve_safety_restraint_code ====")
    z_input = input("Enter ride zone code (e.g. CST_01, WTR_A): ")
    try:
        print("Restraint:", resolve_safety_restraint_code(z_input))
    except ValueError as e:
        print("Invalid zone code:", e)

if __name__ == "__main__":
    main()