from myhdl import Signal, intbv, always_comb, instance, instances
from Robot.Utils.Constants import LOW, HIGH

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

    _count = Signal(intbv(0, min = count.min, max = count.max)) # so that count can be read and set
    _speed = Signal(intbv(0, min = speed.min, max = speed.max)) # so that speed can be read and set

    # Read quadrature encoder's channels and keep internal count
    @instance
    def handle_count():
        previous_a = LOW
        previous_b = LOW
        while True:
            yield clk25.posedge, rst_n.negedge
            if rst_n == LOW:
                _count.next = 0
            else:
                if a ^ previous_a ^ b ^ previous_b == 1: # it moved
                    if a ^ previous_b == 1: # forward
                        if _count == _count.max - 1:
                            _count.next = _count.min
                        else:
                            _count.next = _count + 1
                    else:
                        if _count == _count.min:
                            _count.next = _count.max - 1
                        else:
                            _count.next = _count - 1
                previous_a = a.val
                previous_b = b.val

    # Generate a 250 Hz clock
    clk250hz = Signal(LOW)
    @instance
    def gen_clk250hz():
        # count to 50000 to generate a 500 Hz overflowing counter (25M/50000=500)
        # toggle clock at each overflow: 250 Hz clock
        _cnt = intbv(0, min = 0, max = 50000)
        while True:
            yield clk25.posedge
            if _cnt == _cnt.max - 1:
                _cnt[:] = 0
                clk250hz.next = not clk250hz
            else:
                _cnt += 1

    # Compute the speed at 250 Hz
    @instance
    def handle_speed():
        _previous_count = intbv(0)[len(_count):]
        _range = _count.max - _count.min
        while True:
            yield clk250hz.posedge, rst_n.negedge
            if rst_n == LOW:
                _speed.next = 0
                _previous_count[:] = 0
            else:
                _tmp = _count - _previous_count

                # handle underflows and overflows:
                # - if the counter overflowed:  _count - _previous_count is REALLY negative (<< 0)
                # - if the counter underflowed: _count - _previous_count is REALLY positive (>> 0)
                # the limit of 'really' is arbitrarily set to half the possible range of the count
                if _tmp <= -(_range >> 1):
                    _tmp += _range
                if _tmp >= (_range >> 1):
                    _tmp -= _range

                # adjust to count in ticks/s
                _tmp *= 250
                if _tmp >= _speed.max:
                    _speed.next = _speed.max - 1
                elif _tmp < _speed.min:
                    _speed.next = _speed.min
                else:
                    _speed.next = _tmp
                _previous_count[:] = count

    # Copies the internal count to the count output
    @always_comb
    def drive_count():
        count.next = _count

    # Copies the internal speed to the speed output
    @always_comb
    def drive_speed():
        speed.next = _speed

    return instances()
