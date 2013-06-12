import sys
sys.path.append('../lib')
sys.path.append('../../lib')
sys.path.append('../../test')

import unittest

from myhdl import Signal, Simulation, StopSimulation, intbv, join, toVHDL
from Robot.Utils.Constants import LOW, HIGH
from Attic.Utils.Counter import Counter
from TestUtils import ClkGen

def TestBench(CounterTester):
    count = Signal(intbv(0, min = -2**3, max = 2**3))
    clk = Signal(LOW)
    inc_or_dec = Signal(HIGH)
    wrap_around = Signal(LOW)
    rst_n = Signal(HIGH)

    # instanciate modules
    Counter_inst = toVHDL(Counter, count, clk, inc_or_dec, wrap_around, rst_n)
    CounterTester_inst = CounterTester(count, clk, inc_or_dec, wrap_around, rst_n)
    ClkGen_inst = ClkGen(clk)

    return Counter_inst, CounterTester_inst, ClkGen_inst

class TestCounter(unittest.TestCase):

    def CounterTester(self, count, clk, inc_or_dec, wrap_around, rst_n):

        def wait_for_clk_period():
            yield join(clk.posedge, clk.negedge)

        def reset_counter():
            rst_n.next = LOW
            yield clk.posedge
            rst_n.next = HIGH

        self.assertEquals(count, 0)

        # Does the counter increment?
        inc_or_dec.next = HIGH
        yield wait_for_clk_period()
        self.assertEquals(count, 1)

        # Does the counter decrement?
        inc_or_dec.next = LOW
        yield wait_for_clk_period()
        self.assertEquals(count, 0)

        # Does the counter handle negative values?
        yield wait_for_clk_period()
        self.assertEquals(count, -1)

        # Does the counter wrap around?
        wrap_around.next = HIGH
        ## underflow
        inc_or_dec.next = LOW
        for i in range(2**3):
            yield wait_for_clk_period()
        self.assertEquals(count, (-1 - 2**3) % 8)
        ## overflow
        inc_or_dec.next = HIGH
        for i in range(2**3):
            yield wait_for_clk_period()
        self.assertEquals(count, -1)

        # Does the counter respect bounds?
        wrap_around.next = LOW
        ## lower bound
        inc_or_dec.next = LOW
        for i in range(2**5):
            yield wait_for_clk_period()
        self.assertEquals(count, count.min)
        ## upper bound
        inc_or_dec.next = HIGH
        for i in range(2**5):
            yield wait_for_clk_period()
        self.assertEquals(count, count.max - 1)

        # Does the counter accept being reset?
        yield reset_counter()
        self.assertEquals(count, 0)

        print 'DONE'

        raise StopSimulation()

    def testCounter(self):
        """ Ensures that counter works as espected """
        sim = Simulation(TestBench(self.CounterTester))
        sim.run()

if __name__ == '__main__':
    unittest.main()
