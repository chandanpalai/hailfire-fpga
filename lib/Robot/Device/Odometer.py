from myhdl import Signal, intbv, always_comb, instance, instances
from Robot.Utils.Constants import LOW, HIGH

MAX_COUNT = 2**16

def OdometerReader(count, a, b, clk25, rst_n):
    """ Quadrature decoder for odometers

    Uses a 25 MHz clock to sample a quadrature encoder's A and B signals
    and keep count of the number of ticks it made.

    Uses rising and falling edges of both signals for a x4 decoder.

    count -- 16-bit output count, subject to overflow and underflow
    a -- channel A of the quadrature encoder
    b -- channel B of the quadrature encoder
    clk25 -- 25 MHz clock input
    rst_n -- active low reset input (count is reset when active)

    """

    int_count = Signal(intbv(0)[len(count):]) # so that count can be read and set

    @instance
    def HandleOdometer():
        """ Read quadrature encoder's channels and keep internal count """
        previous_a = LOW
        previous_b = LOW
        while True:
            yield clk25.posedge, rst_n.negedge
            if rst_n == LOW:
                int_count.next = 0
            else:
                if a ^ previous_a ^ b ^ previous_b == 1: # it moved
                    if a ^ previous_b == 1: # forward
                        # could use modulo but brings in a megawizard function
                        if int_count == MAX_COUNT - 1:
                            int_count.next = 0
                        else:
                            int_count.next = int_count + 1
                    else:
                        # could use modulo but brings in a megawizard function
                        if int_count == 0:
                            int_count.next = MAX_COUNT - 1
                        else:
                            int_count.next = int_count - 1
                previous_a = a.val
                previous_b = b.val

    @always_comb
    def DriveCount():
        """ Copies the internal count to the count output """
        count.next = int_count

    return instances()
