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
    count_counter = Counter(count, count_en, count_dir, HIGH, rst_n)

    # Use count_en and count_dir to count the odometer ticks and compute the
    # odometer speed just like the odometer count (except wrap around)
    _speed = Signal(intbv(0, min = speed.min, max = speed.max))
    _speed_rst_n = Signal(HIGH)
    speed_counter = Counter(_speed, count_en, count_dir, LOW, _speed_rst_n)
    
    # Copy the resulting speed count every 4ms (250Hz) and reset the counter
    # so that it restarts at 0. _speed thus contain the number of ticks between
    # two resets, i.e. the speed.
    @instance
    def handle_speed():
        # count to 100000 to generate a 250 Hz overflowing counter
        _cnt = intbv(0, min = 0, max = 100000)
        while True:
            yield clk25.posedge, rst_n.negedge
            if rst_n == LOW:
                _speed_rst_n.next = LOW
            else:
                if _cnt == _cnt.max - 1:
                    # adjust speed to ticks/s while respecting speed bounds
                    _tmp = 250 * _speed
                    if _tmp >= _speed.max:
                        speed.next = _speed.max - 1
                    elif _tmp < _speed.min:
                        speed.next = _speed.min
                    else:
                        speed.next = _tmp

                    # reset 250Hz counter and speed counter
                    _cnt[:] = 0
                    _speed_rst_n.next = LOW
                else:
                    # carry on, then.
                    _cnt += 1
                    _speed_rst_n.next = HIGH

    return instances()
