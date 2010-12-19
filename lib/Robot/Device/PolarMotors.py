from myhdl import instances
from Robot.Utils.Polar import AngleDistanceToLeftRight

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

    speed_converter = AngleDistanceToLeftRight(angle_speed, distance_speed,
                                               left_speed, right_speed)

    return instances()
