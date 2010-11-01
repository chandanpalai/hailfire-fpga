from myhdl import Signal, intbv, always, instances

LOW, HIGH = bool(0), bool(1)

CLK_DIVIDER = 1024

def MotorDriver(pwm, dir, en_n, clk25, consign, cs_n, rst_n):
    """ PWM signal generator with direction and enable signals for DC motors.

    The generated PWM frequency is approximately 25 KHz (25 MHz / 1024).
    The duty cycle (speed) can be fully controlled via a 10-bit consign.
    The direction can be controlled with the 11th bit of the consign.
    The motor can be enabled or disabled with the 12th bit of the consign.

    pwm -- output PWM signal
    dir -- output direction signal
    en_n -- active low output enable signal
    clk25 -- 25 MHz clock input
    consign -- enable bit, dir bit and 10-bit consign value in clock ticks
    cs_n -- active low chip select (consign is read when active)
    rst_n -- active low reset input (pwm, dir, en are reset when active)

    """

    # count to 1024 to generate a 25 kHz PWM (approximately)
    cnt = Signal(intbv(0, min = 0, max = CLK_DIVIDER))

    # duty cycle is a 10-bit integer
    dcl = Signal(intbv(0)[10:])

    @always(clk25.posedge, rst_n.negedge)
    def HandleConsign():
        """ Read consign, handle reset and increment counter """
        if rst_n == LOW:
            dcl.next = 0
            dir.next = HIGH
            en_n.next = HIGH
        else:
            # handle new consign
            if cs_n == LOW:
                dcl.next = consign[10:]
                dir.next = consign[10]
                en_n.next = consign[11]

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
