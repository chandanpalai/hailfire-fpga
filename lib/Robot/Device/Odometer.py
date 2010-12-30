from myhdl import Signal, intbv, instance, instances
from Robot.Utils.Constants import LOW, HIGH
from Robot.Utils.Counter import Counter

def OdometerReader(count, speed, a, b, clk25, rst_n):
    """

    Quadrature decoder for odometers

    Uses a 25 MHz clock to sample a quadrature encoder's A and B signals
    and keep count of the number of ticks it made. Also keeps track of the
    speed of the odometer, using a 250Hz clock to compute it.

    Uses rising and falling edges of both signals for a x4 decoder.

    count

        Output count in ticks. Wraps around when needed.

    speed

        Signed output speed in ticks/s. Cropped to fit in the given intbv.

    a, b

        Channels A and B of the quadrature encoder

    clk25

        25 MHz clock input. Channels A and B are sampled on rising and falling
        clock edges (x4 decoding). The speed is computed every 4 ms (250 Hz).

    rst_n

        Active low reset input (count and speed are reset when active)

    """

    count_en  = Signal(LOW)
    count_dir = Signal(LOW)

    # Read quadrature encoder's channels and generate count_en and count_dir signals
    @instance
    def handle_count():
        previous_a = LOW
        previous_b = LOW
        while True:
            yield clk25.posedge
            count_en.next  = (a ^ previous_a ^ b ^ previous_b == 1) # it moved
            count_dir.next = (a ^ previous_b == 1) # forward
            previous_a = a.val
            previous_b = b.val

    # Use count_en and count_dir to maintain the odometer count
    count_counter = Counter(count       = count,
                            clk         = count_en,
                            inc_or_dec  = count_dir,
                            wrap_around = True,
                            rst_n       = rst_n)

    # Use count_en and count_dir to count the odometer ticks and compute the
    # odometer speed just like the odometer count (except wrap around)
    int_speed = Signal(intbv(0, min = speed.min, max = speed.max))
    speed_rst_n = Signal(HIGH)
    speed_counter = Counter(count       = int_speed,
                            clk         = count_en,
                            inc_or_dec  = count_dir,
                            wrap_around = False,
                            rst_n       = speed_rst_n)

    # Copy the resulting speed count every 4ms (250Hz) and reset the counter
    # so that it restarts at 0. int_speed thus contain the number of ticks between
    # two resets, i.e. the speed.
    @instance
    def handle_speed():
        # count to 100000 to generate a 250 Hz overflowing counter
        overflowing_cnt = intbv(0, min = 0, max = 100000)
        while True:
            yield clk25.posedge, rst_n.negedge
            if rst_n == LOW:
                speed_rst_n.next = LOW
            else:
                if overflowing_cnt == overflowing_cnt.max - 1:
                    # adjust speed to ticks/s while respecting speed bounds
                    tmp = 250 * int_speed
                    if tmp >= int_speed.max:
                        speed.next = intbv(int_speed.max - 1)
                    elif tmp < int_speed.min:
                        speed.next = intbv(int_speed.min)
                    else:
                        speed.next = tmp

                    # reset 250Hz counter and speed counter
                    overflowing_cnt[:] = 0
                    speed_rst_n.next = LOW
                else:
                    # carry on, then.
                    overflowing_cnt += 1
                    speed_rst_n.next = HIGH

    return instances()
