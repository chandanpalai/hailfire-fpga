from myhdl import instance, instances, intbv
from Robot.Utils.Constants import LOW, CLK_FREQ

def LEDDriver(led, clk, rst_n):
    """

    Toggle a LED every second (1s off, 1s on).

    led

        Output signal

    clk

        Clock input

    rst_n

        Active low reset input (resets internal counter when active).

    """

    TOGGLE_FREQ = 1
    CNT_MAX = int(CLK_FREQ/TOGGLE_FREQ - 1)

    @instance
    def DriveLED():
        """ Toggle LED every second """

        # cnt overflows at 1Hz
        cnt = intbv(0, min = 0, max = CNT_MAX + 1)
        led_on = LOW

        while True:
            yield clk.posedge, rst_n.negedge
            if rst_n == LOW:
                cnt[:] = 0
                led_on = LOW
            else:
                if cnt == CNT_MAX:
                    cnt[:] = 0
                    led_on = not led_on
                    led.next = led_on
                else:
                    cnt += 1

    return instances()
