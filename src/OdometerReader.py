from myhdl import Signal, intbv, always, always_comb

LOW, HIGH = bool(0), bool(1)

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

    int_count  = Signal(intbv(0)[16:]) # so that count can be read and set
    previous_a = Signal(LOW)
    previous_b = Signal(LOW)

    @always(clk25.posedge, rst_n.negedge)
    def readOdometer():
        """ Read quadrature encoder's channels and keep internal count """
        if rst_n == LOW:
            int_count.next = 0
            previous_a.next = a
            previous_b.next = b
        else:
            if a ^ previous_a ^ b ^ previous_b == 1: # it moved
                if a ^ previous_b == 1: # which direction
                    int_count.next = (int_count + 1) % MAX_COUNT
                else:
                    int_count.next = (int_count - 1) % MAX_COUNT
            previous_a.next = a
            previous_b.next = b

    @always_comb
    def driveOutput():
        """ Copies the internal count to the count output """
        count.next = int_count

    return readOdometer, driveOutput
