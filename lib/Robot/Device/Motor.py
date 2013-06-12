from myhdl import instance, instances, intbv
from Robot.Utils.Constants import LOW, HIGH

def MotorDriver(pwm, dir, en_n, clk25, speed, rst_n, optocoupled):
    """

    PWM signal generator with direction signal for DC motors.

    The generated PWM frequency is approximately 25 KHz (25 MHz / 1024).
    The duty cycle can be fully controlled via a 11-bit speed input.

    pwm

        Output PWM signal

    dir

        Output direction signal

    en_n

        Active low output enable signal

    clk25


        25 MHz clock input

    speed

        11-bit signed speed value in clock ticks

    rst_n

        Active low reset input (resets internal counter when active).
        Use the speed input to reset the speed of the motor.

    optocoupled

        Set to True if outputs should be inverted to account for optocouplers.

    """

    assert speed.min >= -2**10 and speed.max <= 2**10, 'wrong speed constraints'

    # account for optocouplers
    LOW_OPTO  = LOW if not optocoupled else HIGH
    HIGH_OPTO = HIGH if not optocoupled else LOW

    CNT_MAX = 2**10 - 1;

    @instance
    def DriveMotor():
        """ Generate PWM, dir and brake signals for motor """

        # cnt overflows at 25KHz (approximately)
        cnt = intbv(0, min = 0, max = CNT_MAX + 1)

        # 10-bit duty cycle
        duty_cycle = intbv(0)[10:]

        while True:
            yield clk25.posedge, rst_n.negedge
            if rst_n == LOW:
                cnt[:] = 0
                duty_cycle[:] = 0
                dir.next = HIGH_OPTO
                pwm.next = LOW_OPTO
                en_n.next = LOW_OPTO
            else:
                # accept new consign at the beginning of a period
                if cnt == 0:
                    # extract duty cycle and direction
                    if speed >= 0:
                        duty_cycle[:] = speed
                        dir.next = HIGH_OPTO
                    elif -speed >= CNT_MAX: # handle -1024 case
                        duty_cycle[:] = CNT_MAX
                        dir.next = LOW_OPTO
                    else:
                        duty_cycle[:] = -speed
                        dir.next = LOW_OPTO

                # reached consign?
                if cnt >= duty_cycle:
                    pwm.next = LOW_OPTO
                else:
                    pwm.next = HIGH_OPTO

                if cnt == CNT_MAX:
                    cnt[:] = 0
                else:
                    cnt += 1

                en_n.next = LOW_OPTO

    return instances()
