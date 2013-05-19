import sys
sys.path.append('../lib')
sys.path.append('../../lib')

import unittest

from myhdl import Signal, Simulation, toVHDL, StopSimulation, delay, intbv, join, traceSignals
from Attic.ControlSystem.Filter.PID import PIDFilter
from Robot.Utils.Constants import LOW, HIGH

def TestBench(PIDTester):
    # create input and output signals with default values
    input  = Signal(intbv(0, min = -2**31, max = 2**31))
    output = Signal(intbv(0, min = -2**31, max = 250))

    # create coeffs
    gain_P = Signal(intbv(1)[8:])
    gain_I = Signal(intbv(0)[8:])
    gain_D = Signal(intbv(0)[8:])
    out_shift = Signal(intbv(0)[8:])

    # create limits
    max_I = intbv(2**32)
    max_D = intbv(2**32)

    # reset line
    rst_n = Signal(HIGH)

    # instanciate modules
    PIDFilter_inst = toVHDL(PIDFilter, input, output, gain_P, gain_I, gain_D, out_shift, max_I, max_D, rst_n)
    PIDTester_inst = PIDTester(input, output, gain_P, gain_I, gain_D, out_shift, max_I, max_D, rst_n)

    return PIDFilter_inst, PIDTester_inst

class TestPIDFilter(unittest.TestCase):

    def PIDTester(self, input, output, gain_P, gain_I, gain_D, out_shift, max_I, max_D, rst_n):

        def reset_filter():
            input.next = 0
            rst_n.next = LOW
            yield delay(1)
            rst_n.next = HIGH
            yield delay(1)
            self.assertEquals(output, 0)

        self.assertEquals(input, 0)
        self.assertEquals(output, 0)

        # Test a P=1, I=0, D=0 filter

        input.next = 10
        yield output
        self.assertEquals(output, 10)

        input.next = 20
        yield output
        self.assertEquals(output, 20)

        input.next = -20
        yield output
        self.assertEquals(output, -20)

        # Reset filter
        yield reset_filter()


        # Change it to a P=2, I=1, D=0 filter
        gain_P.next = 2
        gain_I.next = 1
        gain_D.next = 0

        input.next = 10
        yield output
        self.assertEquals(output, 2 * 10 + 1 * (0 + 10))

        input.next = 20
        yield output
        self.assertEquals(output, 2 * 20 + 1 * (10 + 20))

        input.next = -20
        yield output
        self.assertEquals(output, 2 * -20 + 1 * (30 - 20))

        # Reset filter
        yield reset_filter()


        # Change it to a P=3, I=2, D=1 filter
        gain_P.next = 3
        gain_I.next = 2
        gain_D.next = 1

        input.next = 10
        yield output
        self.assertEquals(output, 3 * 10 + 2 * (0 + 10) + 1 * (10 - 0))

        input.next = 20
        yield output
        self.assertEquals(output, 3 * 20 + 2 * (10 + 20) + 1 * (20 - 10))

        input.next = -20
        yield output
        self.assertEquals(output, 3 * -20 + 2 * (30 - 20) + 1 * (-20 - 20))

        # Reset filter
        yield reset_filter()


        # Change it to a P=1, I=0, D=0 filter, with an out_shift
        gain_P.next = 1
        gain_I.next = 0
        gain_D.next = 0
        out_shift.next = 1 # divide by 2

        input.next = 10
        yield output
        self.assertEquals(output, 5)

        input.next = 20
        yield output
        self.assertEquals(output, 10)

        input.next = -20
        yield output
        self.assertEquals(output, -10)

        # Reset filter
        yield reset_filter()


        # Test output saturation
        input.next = 500
        yield output
        self.assertEquals(output, 249)

        print 'DONE'

        raise StopSimulation()

    def testPIDFilter(self):
        """ Ensures that filter works as espected """
        sim = Simulation(TestBench(self.PIDTester))
        sim.run()

if __name__ == '__main__':
    unittest.main()
