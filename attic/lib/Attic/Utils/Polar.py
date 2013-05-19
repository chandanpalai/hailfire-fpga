from myhdl import always_comb, instances

def AngleDistanceToLeftRight(angle_val, distance_val, left_val, right_val):
    """

    Convert polar values (angle, distance) to differential values (left, right).

    angle_val, distance_val

        Input (angle, distance) values.

    left_val, right_val

        Output (left, right) values.

    """

    assert left_val.min <= distance_val.min - angle_val.max, 'insufficient left_val.min'
    assert left_val.max >= distance_val.max - angle_val.min, 'insufficient left_val.max'

    assert right_val.min <= distance_val.min + angle_val.min, 'insufficient right_val.min'
    assert right_val.max >= distance_val.max + angle_val.max, 'insufficient right_val.max'

    @always_comb
    def wheels_from_polar():
        left_val.next  = distance_val - angle_val
        right_val.next = distance_val + angle_val

    return instances()

def LeftRightToAngleDistance(left_val, right_val, angle_val, distance_val):
    """

    Convert differential values (left, right) to polar values (angle, distance).

    left_val, right_val

        Input (left, right) values.

    angle_val, distance_val

        Output (angle, distance) values.

    """

    assert angle_val.min <= (right_val.min - left_val.max) / 2, 'insufficient angle_val.min'
    assert angle_val.max >= (right_val.max - left_val.min) / 2, 'insufficient angle_val.max'

    assert distance_val.min <= (right_val.min + left_val.min) / 2, 'insufficient distance_val.min'
    assert distance_val.max >= (right_val.max + left_val.max) / 2, 'insufficient distance_val.max'

    @always_comb
    def polar_from_wheels():
        angle_val.next    = (right_val - left_val) >> 1
        distance_val.next = (right_val + left_val) >> 1

    return instances()
