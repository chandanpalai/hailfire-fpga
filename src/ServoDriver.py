from myhdl import Signal, intbv, always, instances

LOW, HIGH = bool(0), bool(1)

CLK_DIVIDER = 500000

def ServoDriver(pwm, clk25, consign, cs_n, rst_n):
    """ PWM signal generator for servo motors

    Uses a 25 MHz clock to generate a PWM suitable for servo motors.

    Servo motors work best with a 50 Hz PWM. On this 20 ms period, the
    following duty cycle values are the only ones really useful:
     * 0 ms: servo motor is disabled
     * approximately 1.5 ms: servo motor is at 0 deg
     * approximately 0.5 ms: servo motor is at full right (or left?)
     * approximately 2.5 ms: servo motor is at full left (or right?)
     * all values between 0.5 ms and 2.5 ms.

    In particular, all values beyond 2.5 ms are useless and only induce
    jitter on the servo position. A clock cycle being 0.04 us, 2.5 ms is
    62500 clock cycles. This mean that the useful duty cycle values can
    all be reached with the fullest precision possible with a 16-bit duty
    cycle consign (0 to 65535, with values from 1 to 12500 and from 62500
    to 65535 being useless).

    pwm -- output signal
    clk25 -- 25 MHz clock input
    consign -- 16-bit consign value in clock ticks
    cs_n -- active low chip select (consign is read when active)
    rst_n -- active low reset input (pwm is reset when active)

    """

    # count to 500000 to generate a 50 Hz PWM: 25000000/500000 = 50
    cnt = Signal(intbv(0, min = 0, max = CLK_DIVIDER))

    # duty cycle is a 16-bit integer
    dcl = Signal(intbv(0)[16:])

    @always(clk25.posedge, rst_n.negedge)
    def HandleConsign():
        """ Read consign, handle reset and increment counter """
        if rst_n == LOW:
            dcl.next = 0
        else:
            # handle new consign
            if cs_n == LOW:
                dcl.next = consign

            # could use modulo but brings in a megawizard function
            if cnt == CLK_DIVIDER - 1:
                cnt.next = 0
            else:
                cnt.next = cnt + 1

    @always(cnt, dcl)
    def DriveOutput():
        """ Drive PWM output signal """
        if cnt < dcl:
            pwm.next = HIGH
        else:
            pwm.next = LOW

    return instances()
