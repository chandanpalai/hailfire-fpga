from myhdl import instances
from Attic.Utils.Polar import LeftRightToAngleDistance

def PolarOdometers(left_count, left_speed, right_count, right_speed,
                   angle_count, angle_speed, distance_count, distance_speed):
    """

    Virtual angle and distance odometers

    Convert differential drive odometer counts and speeds (left, right) to
    polar odometers counts and speeds (angle, distance).

    left_count, left_speed

        Input count and speed of the left odometer.

    right_count, right_speed

        Input count and speed of the left odometer.

    angle_count, angle_speed

        Output count and speed of the virtual angle odometer.

    distance_count, distance_speed

        Output count and speed of the virtual distance odometer.

    """

    count_converter = LeftRightToAngleDistance(left_count, right_count,
                                               angle_count, distance_count)

    speed_converter = LeftRightToAngleDistance(left_speed, right_speed,
                                               angle_speed, distance_speed)

    return instances()
