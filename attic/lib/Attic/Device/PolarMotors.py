from myhdl import Signal, always, instances, intbv
from Attic.Utils.Polar import AngleDistanceToLeftRight

def PolarMotors(angle_speed, distance_speed, left_speed, right_speed):
    """

    Virtual angle and distance motors

    Convert polar motor speeds (angle, distance) to differential drive motor
    speeds (left, right).

    angle_speed

        Input speed for the virtual angle motor.

    distance_speed

        Input speed for the virtual distance motor.

    left_speed

        Output speed for the left motor.

    right_speed

        Output speed for the right motor.

    """

    # left and right speeds with suitable constraints for AngleDistanceToLeftRight
    greater_left_speed = Signal(intbv(0, min = distance_speed.min - angle_speed.max,
                                         max = distance_speed.max - angle_speed.min))

    greater_right_speed = Signal(intbv(0, min = distance_speed.min + angle_speed.min,
                                          max = distance_speed.max + angle_speed.max))

    speed_converter = AngleDistanceToLeftRight(angle_speed, distance_speed,
                                               greater_left_speed, greater_right_speed)

    @always(greater_left_speed)
    def drive_left_speed():
        """ Clip greater_left_speed to left_speed """
        if greater_left_speed >= left_speed.max:
            left_speed.next = intbv(left_speed.max - 1)
        elif greater_left_speed < left_speed.min:
            left_speed.next = intbv(left_speed.min)
        else:
            left_speed.next = greater_left_speed

    @always(greater_right_speed)
    def drive_right_speed():
        """ Clip greater_right_speed to right_speed """
        if greater_right_speed >= right_speed.max:
            right_speed.next = intbv(right_speed.max - 1)
        elif greater_right_speed < right_speed.min:
            right_speed.next = intbv(right_speed.min)
        else:
            right_speed.next = greater_right_speed

    return instances()
