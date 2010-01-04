from myhdl import Signal, intbv, always

LOW, HIGH = bool(0), bool(1)

CLK_DIVIDER = 500000

def ServoDriver(pwm, clk25, consign, cs_n, rst_n):
    """ PWM signal generator for servo motors

    Uses a 25 MHz clock to generate a PWM suitable for servo motors.

    Servo motors work best with a 50 Hz PWM. On this 20 ms period, the
    following duty cycle values are the only ones really useful:
     * 0 ms: servo motor is disabled
     * approximately 1.5 ms: servo motor is at 0 deg
     * approximately 0.5 ms: servo motor is at full right (or left)
     * approximately 2.5 ms: servo motor is at full left (or right)
     * all values between 0.5 ms and 2.5 ms.

    In particular, all values beyond 2.5 ms are useless and only induce
    jitter on the servo position. A clock cycle being 0.04 us, 2.5 ms is
    62500 clock cycles. This mean that the useful duty cycle values can
    all be reached with the fullest precision possible with a 16-bit duty
    cycle consign.

    pwm -- output signal
    clk25 -- 25 MHz clock input
    consign -- 16-bit consign value in clock ticks
    cs_n -- active low chip select (consign is read when active)
    rst_n -- active low reset input (pwm is reset when active)

    """

    # count to 500000 to generate a 50 Hz PWM: 25000000/500000 = 50
    cnt = Signal(intbv(0, min = 0, max = CLK_DIVIDER))

    # duty cycle is a 16-bit integer
    dcl = Signal(intbv(0)[16:]);

    @always(clk25.posedge, rst_n.negedge, cs_n.negedge)
    def driveServo():
        """ Drive PWM output signal

        Reset consign when rst_n is active.
        Read consign when cs_n is active.
        Generate output signal on clock events.

        """
        if rst_n == LOW:
            dcl.next = 0
        elif cs_n == LOW:
            dcl.next = consign
        else:
            if cnt < dcl:
                pwm.next = HIGH
            else:
                pwm.next = LOW
            cnt.next = (cnt + 1) % CLK_DIVIDER

    return driveServo
