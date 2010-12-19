import sys
sys.path.append('../lib')

import unittest

from myhdl import Signal, Simulation, StopSimulation, intbv, toVHDL
from random import randrange
from Robot.Device.PolarMotors import PolarMotors

NR_TESTS = 100

def TestBench(PolarMotorsTester):
    # create 31-bit signed (angle, distance) input signals
    angle_speed    = Signal(intbv(0, min = -2**30, max = 2**30))
    distance_speed = Signal(intbv(0, min = -2**30, max = 2**30))

    # create 32-bit signed (left, right) output signals
    left_speed  = Signal(intbv(0, min = -2**31, max = 2**31))
    right_speed = Signal(intbv(0, min = -2**31, max = 2**31))

    # instanciate modules
    PolarMotors_inst = toVHDL(PolarMotors, angle_speed, distance_speed,
                                           left_speed, right_speed)
    PolarMotorsTester_inst = PolarMotorsTester(angle_speed, distance_speed,
                                               left_speed, right_speed)

    return PolarMotors_inst, PolarMotorsTester_inst

class TestPolarMotors(unittest.TestCase):

    def PolarMotorsTester(self, angle_speed, distance_speed, left_speed, right_speed):

        # initial position
        self.assertEquals(right_speed, 0)
        self.assertEquals(left_speed, 0)

        # go forward
        distance_speed.next = 20
        yield left_speed, right_speed
        self.assertEquals(right_speed, 20)
        self.assertEquals(left_speed, 20)

        # turn right
        angle_speed.next = 30
        yield left_speed, right_speed
        self.assertEquals(right_speed, 20 + 30)
        self.assertEquals(left_speed, 20 - 30)

        # turn left
        angle_speed.next = -30
        yield left_speed, right_speed
        self.assertEquals(right_speed, 20 + (-30))
        self.assertEquals(left_speed, 20 - (-30))

        print 'DONE'

        raise StopSimulation()

    def testPolarMotors(self):
        """ Ensures that filter works as espected """
        sim = Simulation(TestBench(self.PolarMotorsTester))
        sim.run()

if __name__ == '__main__':
    unittest.main()
