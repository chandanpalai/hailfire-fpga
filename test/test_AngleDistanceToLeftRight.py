import sys
sys.path.append('../lib')

import unittest

from myhdl import Signal, Simulation, StopSimulation, intbv, join, toVHDL
from random import randrange
from Robot.Utils.Polar import AngleDistanceToLeftRight

NR_TESTS = 100

def TestBench(AngleDistanceToLeftRightTester):
    # create 31-bit signed (angle, distance) input signals
    angle_val    = Signal(intbv(0, min = -2**30, max = 2**30))
    distance_val = Signal(intbv(0, min = -2**30, max = 2**30))

    # create 32-bit signed (left, right) output signals
    left_val  = Signal(intbv(0, min = -2**31, max = 2**31))
    right_val = Signal(intbv(0, min = -2**31, max = 2**31))

    # instanciate modules
    AngleDistanceToLeftRight_inst = toVHDL(AngleDistanceToLeftRight, angle_val, distance_val, left_val, right_val)
    AngleDistanceToLeftRightTester_inst = AngleDistanceToLeftRightTester(angle_val, distance_val, left_val, right_val)

    return AngleDistanceToLeftRight_inst, AngleDistanceToLeftRightTester_inst

class TestAngleDistanceToLeftRight(unittest.TestCase):

    def AngleDistanceToLeftRightTester(self, angle_val, distance_val, left_val, right_val):

        self.assertEquals(angle_val,    0)
        self.assertEquals(distance_val, 0)
        self.assertEquals(left_val,  0)
        self.assertEquals(right_val, 0)

        def stimulus(angle_rand, distance_rand):
            # print 'set angle to:', angle_rand
            angle_val.next = angle_rand

            # print 'set distance to:', distance_rand
            distance_val.next = distance_rand            

        def check(angle_rand, distance_rand):
            # print 'waiting for left_val and right_val'
            yield join(left_val, right_val)

            # print 'left should be:', distance_rand - angle_rand
            self.assertEquals(left_val, distance_rand - angle_rand)

            # print 'right should be:', distance_rand + angle_rand
            self.assertEquals(right_val, distance_rand + angle_rand)

        for i in range(NR_TESTS):
            angle_rand    = randrange(angle_val.min, angle_val.max)
            distance_rand = randrange(distance_val.min, distance_val.max)

            yield join(stimulus(angle_rand, distance_rand), check(angle_rand, distance_rand))

        print 'DONE'

        raise StopSimulation()

    def testAngleDistanceToLeftRight(self):
        """ Ensures that filter works as espected """
        sim = Simulation(TestBench(self.AngleDistanceToLeftRightTester))
        sim.run()

if __name__ == '__main__':
    unittest.main()
