from myhdl import Signal, always, always_comb, instances, intbv
from Robot.Utils.Constants import LOW, HIGH
from Robot.Utils.Counter import Counter

CLK_DIVIDER = 2**10

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

    assert speed.min >= -CLK_DIVIDER and speed.max <= CLK_DIVIDER, 'wrong speed constraints'

    # account for optocouplers
    LOW_OPTO  = LOW if not optocoupled else HIGH
    HIGH_OPTO = HIGH if not optocoupled else LOW

    # count to 1024 to generate a 25 kHz PWM (approximately)
    count   = Signal(intbv(0, min = 0, max = CLK_DIVIDER))
    counter = Counter(count       = count,
                      clk         = clk25,
                      inc_or_dec  = HIGH,
                      wrap_around = True,
                      rst_n       = rst_n)

    # duty cycle is 0 to 1024 too
    duty_cycle = Signal(intbv(0, min = 0, max = CLK_DIVIDER))

    @always(speed)
    def read_speed():
        """ Extract duty cycle from speed input """
        if speed >= 0:
            duty_cycle.next = speed
        elif -speed >= duty_cycle.max: # handle -1024 case
            duty_cycle.next = intbv(duty_cycle.max - 1)
        else:
            duty_cycle.next = -speed

    @always_comb
    def drive_pwm():
        """ Drive pwm output signal """
        if count < duty_cycle:
            pwm.next = HIGH_OPTO
        else:
            pwm.next = LOW_OPTO

    @always_comb
    def drive_dir():
        """ Drive dir output signal """
        if speed >= 0:
            dir.next = HIGH_OPTO
        else:
            dir.next = LOW_OPTO

    @always(speed) # need to drive en_n so anything will do
    def drive_en():
        """ Drive en_n output signal """
        en_n.next = HIGH

    return instances()
