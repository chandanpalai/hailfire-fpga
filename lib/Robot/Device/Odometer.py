from myhdl import intbv, instance, instances
from Robot.Utils.Constants import LOW, CLK_FREQ

def OdometerReader(count, a, b, clk25, rst_n):
    """

    Quadrature decoder for odometers

    Uses a 25 MHz clock to sample a quadrature encoder's A and B signals
    and keep count of the number of ticks it made.

    Uses rising and falling edges of both signals for a x4 decoder.

    count

        Output count in ticks. Wraps around when needed.

    a, b

        Channels A and B of the quadrature encoder

    clk25

        25 MHz clock input. Channels A and B are sampled on rising and falling
        clock edges (x4 decoding).

    rst_n

        Active low reset input (count is reset when active)

    """

    @instance
    def KeepCount():
        # previous values of both channels
        previous_a = a.val
        previous_b = b.val

        # R/W copy of count
        int_count = intbv(0, min = count.min, max = count.max)

        while True:
            yield clk25.posedge, rst_n.negedge
            if rst_n == LOW:
                int_count[:] = 0
            else:
                # It moved
                if a ^ previous_a ^ b ^ previous_b == 1:
                    # Forward
                    if a ^ previous_b == 1:
                        # Increment count, with wrap around
                        if int_count != int_count.max - 1:
                            int_count += 1
                        else:
                            int_count[:] = intbv(int_count.min)
                    # Backward
                    else:
                        # Decrement count, with wrap around
                        if int_count != int_count.min:
                            int_count -= 1
                        else:
                            int_count[:] = intbv(int_count.max - 1)

                count.next = int_count
                previous_a = a.val
                previous_b = b.val

    return instances()
