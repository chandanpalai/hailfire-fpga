import sys
sys.path.append('../lib')
sys.path.append('../../lib')

import unittest

from myhdl import Signal, Simulation, toVHDL, StopSimulation, intbv
from random import randrange
from Attic.ControlSystem.Filter.Identity import IdentityFilter

def TestBench(IdentityTester):
    # create input and output 32-bit signals with default values
    input  = Signal(intbv(0, min = -2**31, max = 2**31))
    output = Signal(intbv(0, min = -2**31, max = 2**31))

    # instanciate modules
    IdentityFilter_inst = toVHDL(IdentityFilter, input, output)
    IdentityTester_inst = IdentityTester(input, output)

    return IdentityFilter_inst, IdentityTester_inst

class TestIdentityFilter(unittest.TestCase):

    def IdentityTester(self, input, output):

        self.assertEquals(input, 0)
        self.assertEquals(output, 0)

        for i in range(10):
            tmp = randrange(input.min, input.max)
            input.next = tmp
            yield output
            self.assertEquals(output, tmp)

        print 'DONE'

        raise StopSimulation()

    def testIdentityFilter(self):
        """ Ensures that filter works as espected """
        sim = Simulation(TestBench(self.IdentityTester))
        sim.run()

if __name__ == '__main__':
    unittest.main()
