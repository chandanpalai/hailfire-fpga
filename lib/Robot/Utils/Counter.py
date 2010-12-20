from myhdl import Signal, always, always_comb, instances, intbv
from Robot.Utils.Constants import LOW, HIGH

def Counter(count, clk, inc_or_dec, wrap_around, rst_n):
    """

    Bi-directional counter

    count

        Output count.

    clk

        Clock input: the counter is incremented or decremented (depending on
        inc_or_dec) on rising clock edges.

    inc_or_dec

        Control counting behavior: increment when high, decrement when low.

    wrap_around

        Control count bahavior at limits:
            - wraps around when this is high (overflows or underflows),
            - is limited to count.min and count.max values if this is low.

    rst_n

        Asynchronous reset input.

    """

    # read/write clone of count
    int_count = Signal(intbv(0, min = count.min, max = count.max))

    # counter logic
    @always(clk.posedge, rst_n.negedge)
    def do_count():
        if rst_n == LOW:
            int_count.next = 0
        else:
            if inc_or_dec == HIGH:
                if int_count != int_count.max - 1:
                    int_count.next = int_count + 1
                elif wrap_around == HIGH:
                    int_count.next = int_count.min
            else:
                if int_count != int_count.min:
                    int_count.next = int_count - 1
                elif wrap_around == HIGH:
                    int_count.next = int_count.max - 1

    # copies the internal count to the count output
    @always_comb
    def drive_count():
        count.next = int_count

    return instances()
