from myhdl import Signal, intbv, always, instances
from Robot.Utils.Constants import LOW, HIGH

CLK_DIVIDER = 2**10

def MotorDriver(pwm, dir, en_n, clk25, speed, cs_n, rst_n, optocoupled):
    """

    PWM signal generator with direction signal for DC motors.

    The generated PWM frequency is approximately 25 KHz (25 MHz / 1024).
    The duty cycle can be fully controlled via a 11-bit speed input.

    pwm -- output PWM signal
    dir -- output direction signal
    en_n -- active low output enable signal
    clk25 -- 25 MHz clock input
    speed -- 11-bit signed speed value in clock ticks
    cs_n -- active low chip select (speed is read when active)
    rst_n -- active low reset input (pwm and direction are reset when active)
    optocoupled -- set to True if outputs should be inverted to account for optocouplers

    """

    assert speed.min >= -CLK_DIVIDER and speed.max <= CLK_DIVIDER, 'wrong speed constraints'

    # account for optocouplers
    LOW_OPTO  = LOW if not optocoupled else HIGH
    HIGH_OPTO = HIGH if not optocoupled else LOW

    # count to 1024 to generate a 25 kHz PWM (approximately)
    cnt = Signal(intbv(0, min = 0, max = CLK_DIVIDER))

    # duty cycle is 0 to 1024 too
    dcl = Signal(intbv(0, min = 0, max = CLK_DIVIDER))

    @always(clk25.posedge, rst_n.negedge)
    def HandleConsign():
        """ Read speed, handle reset and increment counter """
        if rst_n == LOW:
            dcl.next = 0
            dir.next = HIGH_OPTO
            en_n.next = HIGH_OPTO
        else:
            # handle new speed
            if cs_n == LOW:
                if speed >= 0:
                    dcl.next = speed
                    dir.next = HIGH_OPTO
                elif -speed >= dcl.max: # handle -1024 case
                    dcl.next = intbv(dcl.max - 1)
                    dir.next = LOW_OPTO
                else:
                    dcl.next = -speed
                    dir.next = LOW_OPTO

            # could use modulo but brings in a megawizard function
            if cnt != cnt.max - 1:
                cnt.next = cnt + 1
            else:
                cnt.next = 0

    @always(cnt, dcl)
    def DriveOutput():
        """ Drive PWM output signal """
        if cnt < dcl:
            pwm.next = HIGH_OPTO
        else:
            pwm.next = LOW_OPTO

    return instances()
