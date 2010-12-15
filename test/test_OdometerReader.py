import sys
sys.path.append('../lib')

import unittest

from myhdl import Signal, Simulation, StopSimulation, delay, intbv, join, traceSignals
from Robot.Device.Odometer import OdometerReader
from random import randrange
from TestUtils import ClkGen, quadrature_encode, LOW, HIGH

def TestBench(OdometerTester):
    """ Instanciate modules and wire things up.
    OdometerTester -- test module to instanciate with OdometerReader and ClkGen
    """

    # create signals with default values
    count = Signal(intbv(0)[16:])
    a = Signal(LOW)
    b = Signal(LOW)
    clk = Signal(LOW)
    rst_n = Signal(HIGH)

    # instanciate modules
    OdometerReader_inst = traceSignals(OdometerReader, count, a, b, clk, rst_n)
    OdometerTester_inst = OdometerTester(count, a, b, clk, rst_n)
    ClkGen_inst = ClkGen(clk)

    return OdometerReader_inst, OdometerTester_inst, ClkGen_inst

class TestOdometerReader(unittest.TestCase):

    def OdometerTester(self, count, a, b, clk, rst_n):

        self.assertEquals(count, 0)
        yield delay(100) # readability in gtkwave

        # forward
        forward_steps = intbv(randrange(0xFF))
        print 'forward', forward_steps, 'steps'
        yield quadrature_encode(forward_steps, a, b)
        self.assertEquals(count, forward_steps)
        yield delay(100) # readability in gtkwave

        # backward
        backward_steps = intbv(randrange(0xFF))
        print 'backward', backward_steps, 'steps'
        yield quadrature_encode(backward_steps, b, a)
        self.assertEquals(count, intbv(forward_steps - backward_steps)[16:])
        yield delay(100) # readability in gtkwave

        # to 0
        steps_to_zero = intbv(backward_steps - forward_steps)
        if steps_to_zero >= 0:
            # forwards to 0
            print 'forward', steps_to_zero, 'steps'
            yield quadrature_encode(steps_to_zero, a, b)
        else:
            # backwards to 0
            steps_to_zero = intbv(-steps_to_zero)
            print 'backward', steps_to_zero, 'steps'
            yield quadrature_encode(steps_to_zero, b, a)
        self.assertEquals(count, 0)
        yield delay(100) # readability in gtkwave

        # backward
        backward_steps = intbv(randrange(0xFF))
        print 'backward', backward_steps, 'steps'
        yield quadrature_encode(backward_steps, b, a)
        self.assertEquals(count, intbv(-backward_steps)[16:])
        yield delay(100) # readability in gtkwave

        # forward
        forward_steps = intbv(randrange(0xFF))
        print 'forward', forward_steps, 'steps'
        yield quadrature_encode(forward_steps, a, b)
        self.assertEquals(count, intbv(forward_steps - backward_steps)[16:])
        yield delay(100) # readability in gtkwave

        # to 0
        steps_to_zero = intbv(backward_steps - forward_steps)
        if steps_to_zero >= 0:
            # forwards to 0
            print 'forward', steps_to_zero, 'steps'
            yield quadrature_encode(steps_to_zero, a, b)
        else:
            # backwards to 0
            steps_to_zero = intbv(-steps_to_zero)
            print 'backward', steps_to_zero, 'steps'
            yield quadrature_encode(steps_to_zero, b, a)
        self.assertEquals(count, 0)
        yield delay(100) # readability in gtkwave

        raise StopSimulation()

    def testOdometerReader(self):
        """ Ensures that count works as espected """
        sim = Simulation(TestBench(self.OdometerTester))
        sim.run()

if __name__ == '__main__':
    unittest.main()
