from myhdl import Signal, intbv, always

LOW, HIGH = bool(0), bool(1)

CLK_DIVIDER = 1024

def MotorDriver(pwm, dir, en_n, clk25, consign, rst_n):
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
    rst_n -- active low reset input (pwm, dir, en are reset when active)

    """

    # count to 1024 to generate a 25 kHz PWM (approximately)
    cnt = Signal(intbv(0, min = 0, max = CLK_DIVIDER))

    @always(clk25.posedge, rst_n.negedge)
    def driveMotor():
        """ Drive PWM output signal

        Reset consign when rst_n is active.
        Generate output signal on clock events.

        """
        if rst_n == LOW:
            pwm.next = LOW
            dir.next = HIGH
            en_n.next = HIGH
        else:
            if cnt < consign[10:]:
                pwm.next = HIGH
            else:
                pwm.next = LOW
            dir.next = consign[10]
            en_n.next = consign[11]
            cnt.next = (cnt + 1) % CLK_DIVIDER

    return driveMotor
