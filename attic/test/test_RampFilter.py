import sys
sys.path.append('../lib')
sys.path.append('../../lib')

import unittest

from myhdl import Signal, Simulation, toVHDL, StopSimulation, delay, intbv, join, traceSignals
from Attic.ControlSystem.Filter.Ramp import RampFilter

def TestBench(RampTester):
    # create input and output 32-bit signals with default values
    input  = Signal(intbv(0, min = -2**31, max = 2**31))
    output = Signal(intbv(0, min = -2**31, max = 2**31))

    # create max acceleration and deceleration signals with custom values
    var_1st_ord_pos = Signal(intbv(13)[32:])
    var_1st_ord_neg = Signal(intbv(42)[32:])

    # instanciate modules
    RampFilter_inst = toVHDL(RampFilter, input, output, var_1st_ord_pos, var_1st_ord_neg)
    RampTester_inst = RampTester(input, output, var_1st_ord_pos, var_1st_ord_neg)

    return RampFilter_inst, RampTester_inst

class TestRampFilter(unittest.TestCase):

    def RampTester(self, input, output, var_1st_ord_pos, var_1st_ord_neg):

        self.assertEquals(input, 0)
        self.assertEquals(output, 0)

        # acceleration

        # 0 to 10: acceleration within limit
        input.next = 10
        yield output
        self.assertEquals(output, 10)

        # 10 to 23: acceleration within limit
        input.next = 23
        yield output
        self.assertEquals(output, 23)

        # 23 to 50: acceleration over limit: filtered to 23 -> 36
        input.next = 50
        yield output
        self.assertEquals(output, 36)

        # 23 to 50: acceleration over limit: filtered to 36 -> 49
        input.next = 50
        yield output
        self.assertEquals(output, 49)

        # 23 to 50: now within limit: 49 -> 50
        input.next = 50
        yield output
        self.assertEquals(output, 50)
        
        # deceleration

        # 50 to 10: deceleration within limit
        input.next = 10
        yield output
        self.assertEquals(output, 10)

        # 10 to -116: deceleration over limit: filtered to 10 -> -32
        input.next = -116
        yield output
        self.assertEquals(output, -32)

        # 10 to -116: deceleration within limit: filtered to -32 -> -74
        input.next = -116
        yield output
        self.assertEquals(output, -74)

        # 10 to -116: now within limit: -74 -> -116
        input.next = -116
        yield output
        self.assertEquals(output, -116)

        print 'DONE'

        raise StopSimulation()

    def testRampFilter(self):
        """ Ensures that filter works as espected """
        sim = Simulation(TestBench(self.RampTester))
        sim.run()

if __name__ == '__main__':
    unittest.main()
