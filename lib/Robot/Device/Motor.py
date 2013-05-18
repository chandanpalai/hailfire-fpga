from myhdl import Signal, always, always_comb, instances, intbv
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

    # cnt overflows at 25KHz (approximately)
    CNT_MAX = 2**10 - 1;
    cnt = Signal(intbv(0, min = 0, max = CNT_MAX + 1))

    # 10-bit duty cycle
    duty_cycle = Signal(intbv(0)[10:])
    dir_internal = Signal(HIGH_OPTO)
    pwm_internal = Signal(LOW_OPTO)

    @always(clk25.posedge, rst_n.negedge)
    def drive_internal_signals():
        """ Drive internal signals """
        if rst_n == LOW:
            cnt.next = 0
            duty_cycle.next = 0
            dir_internal.next = HIGH_OPTO
            pwm_internal.next = LOW_OPTO
        else:
            # accept new consign at the beginning of a period
            if cnt == 0:
                # extract duty cycle and direction
                if speed >= 0:
                    duty_cycle.next = speed
                    dir_internal.next = HIGH_OPTO
                elif -speed >= CNT_MAX: # handle -1024 case
                    duty_cycle.next = CNT_MAX
                    dir_internal.next = LOW_OPTO
                else:
                    duty_cycle.next = -speed
                    dir_internal.next = LOW_OPTO

                # start high unless no speed at all
                if speed == 0:
                    pwm_internal.next = LOW_OPTO
                else:
                    pwm_internal.next = HIGH_OPTO
            else:
                # reached consign?
                if cnt == duty_cycle:
                    pwm_internal.next = LOW_OPTO

            if cnt == CNT_MAX:
                cnt.next = 0
            else:
                cnt.next = cnt + 1

    @always_comb
    def drive_output_signals():
        """ Drive output signals """
        pwm.next = pwm_internal
        dir.next = dir_internal
        en_n.next = LOW_OPTO

    return instances()
