import sys
sys.path.append('../lib')

import unittest

from myhdl import Signal, Simulation, StopSimulation, delay, intbv, join, traceSignals, toVHDL
from Robot.Device.Odometer import OdometerReader
from random import randrange
from Robot.Utils.Constants import LOW, HIGH
from TestUtils import ClkGen, quadrature_encode

def TestBench(OdometerTester):
    """ Instanciate modules and wire things up.
    OdometerTester -- test module to instanciate with OdometerReader and ClkGen
    """

    count = Signal(intbv(0, min = -2**10, max=2**10))
    a = Signal(LOW)
    b = Signal(LOW)
    clk = Signal(LOW)
    rst_n = Signal(HIGH)

    # instanciate modules
    OdometerReader_inst = toVHDL(OdometerReader, count, a, b, clk, rst_n)
    OdometerTester_inst = OdometerTester(count, a, b, clk, rst_n)
    ClkGen_inst = ClkGen(clk)

    return OdometerReader_inst, OdometerTester_inst, ClkGen_inst

class TestOdometerReader(unittest.TestCase):

    def OdometerTester(self, count, a, b, clk, rst_n):

        self.assertEquals(count, 0)
        yield delay(100) # readability in gtkwave

        # forward
        forward_steps = randrange(0xFF)
        print 'forward', forward_steps, 'steps'
        yield quadrature_encode(forward_steps, a, b)
        self.assertEquals(count, forward_steps)
        yield delay(100) # readability in gtkwave

        # backward
        backward_steps = randrange(0xFF)
        print 'backward', backward_steps, 'steps'
        yield quadrature_encode(backward_steps, b, a)
        self.assertEquals(count, forward_steps - backward_steps)
        yield delay(100) # readability in gtkwave

        # to 0
        steps_to_zero = backward_steps - forward_steps
        if steps_to_zero >= 0:
            # forwards to 0
            print 'forward', steps_to_zero, 'steps'
            yield quadrature_encode(steps_to_zero, a, b)
        else:
            # backwards to 0
            steps_to_zero = -steps_to_zero
            print 'backward', steps_to_zero, 'steps'
            yield quadrature_encode(steps_to_zero, b, a)
        self.assertEquals(count, 0)
        yield delay(100) # readability in gtkwave

        # backward
        backward_steps = randrange(0xFF)
        print 'backward', backward_steps, 'steps'
        yield quadrature_encode(backward_steps, b, a)
        self.assertEquals(count, -backward_steps)
        yield delay(100) # readability in gtkwave

        # forward
        forward_steps = randrange(0xFF)
        print 'forward', forward_steps, 'steps'
        yield quadrature_encode(forward_steps, a, b)
        self.assertEquals(count, forward_steps - backward_steps)
        yield delay(100) # readability in gtkwave

        # to 0
        steps_to_zero = backward_steps - forward_steps
        if steps_to_zero >= 0:
            # forwards to 0
            print 'forward', steps_to_zero, 'steps'
            yield quadrature_encode(steps_to_zero, a, b)
        else:
            # backwards to 0
            steps_to_zero = -steps_to_zero
            print 'backward', steps_to_zero, 'steps'
            yield quadrature_encode(steps_to_zero, b, a)
        self.assertEquals(count, 0)
        yield delay(100) # readability in gtkwave

        # forward
        forward_steps = count.max
        print 'forward', forward_steps, 'steps'
        yield quadrature_encode(forward_steps, a, b)
        self.assertEquals(count, count.min) # 'just' overflowed
        yield delay(100) # readability in gtkwave

        # backward
        backward_steps = count.max - count.min + 1
        print 'backward', backward_steps, 'steps'
        yield quadrature_encode(backward_steps, b, a)
        self.assertEquals(count, count.max - 1) # 'just' underflowed
        yield delay(100) # readability in gtkwave

        print 'DONE'

        raise StopSimulation()

    def testOdometerReader(self):
        """ Ensures that count works as espected """
        sim = Simulation(TestBench(self.OdometerTester))
        sim.run()

if __name__ == '__main__':
    unittest.main()
