import sys
sys.path.append('../lib')

import unittest

from myhdl import Signal, Simulation, StopSimulation, intbv, join, toVHDL
from random import randrange
from Robot.Utils.Polar import LeftRightToAngleDistance

NR_TESTS = 100

def TestBench(LeftRightToAngleDistanceTester):
    # create 32-bit signed (left, right) input signals
    left_val  = Signal(intbv(0, min = -2**31, max = 2**31))
    right_val = Signal(intbv(0, min = -2**31, max = 2**31))

    # create 32-bit signed (angle, distance) output signals
    angle_val    = Signal(intbv(0, min = -2**31, max = 2**31))
    distance_val = Signal(intbv(0, min = -2**31, max = 2**31))

    # instanciate modules
    LeftRightToAngleDistance_inst = toVHDL(LeftRightToAngleDistance, left_val, right_val, angle_val, distance_val)
    LeftRightToAngleDistanceTester_inst = LeftRightToAngleDistanceTester(left_val, right_val, angle_val, distance_val)

    return LeftRightToAngleDistance_inst, LeftRightToAngleDistanceTester_inst

class TestLeftRightToAngleDistance(unittest.TestCase):

    def LeftRightToAngleDistanceTester(self, left_val, right_val, angle_val, distance_val):

        self.assertEquals(left_val,  0)
        self.assertEquals(right_val, 0)
        self.assertEquals(angle_val,    0)
        self.assertEquals(distance_val, 0)

        def stimulus(left_rand, right_rand):
            # print 'set angle to:', left_rand
            left_val.next = left_rand

            # print 'set distance to:', right_rand
            right_val.next = right_rand            

        def check(left_rand, right_rand):
            # print 'waiting for angle_val and distance_val'
            yield join(angle_val, distance_val)

            # print 'left should be:', right_rand - left_rand
            self.assertEquals(angle_val, (right_rand - left_rand) / 2)

            # print 'right should be:', right_rand + left_rand
            self.assertEquals(distance_val, (right_rand + left_rand) / 2)

        for i in range(NR_TESTS):
            left_rand  = randrange(left_val.min,  left_val.max)
            right_rand = randrange(right_val.min, right_val.max)

            yield join(stimulus(left_rand, right_rand), check(left_rand, right_rand))

        print 'DONE'

        raise StopSimulation()

    def testLeftRightToAngleDistance(self):
        """ Ensures that filter works as espected """
        sim = Simulation(TestBench(self.LeftRightToAngleDistanceTester))
        sim.run()

if __name__ == '__main__':
    unittest.main()
