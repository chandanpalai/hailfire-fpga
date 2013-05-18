from myhdl import Signal, always, always_comb, instances, intbv
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

    # cnt overflows at 1Hz
    TOGGLE_FREQ = 1
    CNT_MAX = int(CLK_FREQ/TOGGLE_FREQ - 1)
    cnt = Signal(intbv(0, min = 0, max = CNT_MAX + 1))

    led_internal = Signal(LOW)

    @always(clk.posedge, rst_n.negedge)
    def drive_led_internal():
        """ Toggle led_inout signal every second """
        if rst_n == LOW:
            cnt.next = 0
            led_internal.next = LOW
        else:
            if cnt == CNT_MAX:
                cnt.next = 0
                led_internal.next = not led_internal
            else:
                cnt.next = cnt + 1

    @always_comb
    def drive_led():
        """ Drive led output signal """
        led.next = led_internal

    return instances()
