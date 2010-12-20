from myhdl import Signal, intbv, always, concat, delay, downrange
from random import randrange
from Robot.Utils.Constants import LOW, HIGH

def ClkGen(clk):
    """ Test clock generator.

    clk -- clock signal

    """
    # Each delay unit simulates a half-period.
    # An half-period amounts to 0.02 us of our 25MHz clock
    @always(delay(1))
    def genClk():
        clk.next = not clk
    return genClk

def random_write(n):
    """ Generate and return a random intbv suitable for a write operation

    n -- length of the written value in number of bytes

    """
    data = intbv(randrange(0xFF))[8:] # key
    data[7] = 1 # write
    data = concat(data, intbv(n)[8:]) # length
    for j in range(n):
        data = concat(data, intbv(randrange(0xFF))[8:]) # value bytes
    return data

def random_read(n):
    """ Generate and return a random intbv suitable for a read operation

    n -- length of the expected value in number of bytes

    """
    data = intbv(randrange(0xFF))[8:] # key
    data[7] = 0 # read
    data = concat(data, intbv(n)[8:]) # length
    for j in range(n):
        data = concat(data, intbv(0)[8:]) # placeholder bytes for value
    return data

def spi_transfer(miso, mosi, sclk, ss_n, master_to_slave, slave_to_master):
    """ Send data like an SPI master would """
    yield delay(50)
    ss_n.next = LOW
    yield delay(10)
    for i in downrange(len(master_to_slave)):
        sclk.next = 1
        mosi.next = master_to_slave[i]
        yield delay(10)
        sclk.next = 0
        slave_to_master[i] = miso
        yield delay(10)
    ss_n.next = HIGH

def count_high(line, clk, count):
    """ Increment count while 'line' is high at clk.posedge """
    yield clk.posedge
    while line == HIGH:
        count += 1
        yield clk.posedge

def quadrature_encode(steps, ch_a, ch_b):
    # - A rises before B:
    #  * if A is low, rise A
    #  * if A is already high, rise B
    # - A falls before B:
    #  * if A is high, lower A
    #  * if A is already low, lower B
    for i in range(steps):
        if ch_a == LOW and ch_b == LOW:
            ch_a.next = HIGH
        elif ch_a == HIGH and ch_b == LOW:
            ch_b.next = HIGH
        elif ch_a == HIGH and ch_b == HIGH:
            ch_a.next = LOW
        elif ch_a == LOW and ch_b == HIGH:
            ch_b.next = LOW
        yield delay(10)
