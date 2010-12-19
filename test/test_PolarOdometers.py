import sys
sys.path.append('../lib')

import unittest

from myhdl import Signal, Simulation, StopSimulation, intbv, toVHDL
from random import randrange
from Robot.Device.PolarOdometers import PolarOdometers

NR_TESTS = 100

def TestBench(PolarOdometersTester):
    # create 32-bit signed (left, right) input signals
    left_count  = Signal(intbv(0, min = -2**31, max = 2**31))
    left_speed  = Signal(intbv(0, min = -2**31, max = 2**31))
    right_count = Signal(intbv(0, min = -2**31, max = 2**31))
    right_speed = Signal(intbv(0, min = -2**31, max = 2**31))

    # create 32-bit signed (angle, distance) output signals
    angle_count    = Signal(intbv(0, min = -2**31, max = 2**31))
    angle_speed    = Signal(intbv(0, min = -2**31, max = 2**31))
    distance_count = Signal(intbv(0, min = -2**31, max = 2**31))
    distance_speed = Signal(intbv(0, min = -2**31, max = 2**31))

    # instanciate modules
    PolarOdometers_inst = toVHDL(PolarOdometers, left_count, left_speed,
                                                 right_count, right_speed,
                                                 angle_count, angle_speed,
                                                 distance_count, distance_speed)
    PolarOdometersTester_inst = PolarOdometersTester(left_count, left_speed,
                                                     right_count, right_speed,
                                                     angle_count, angle_speed,
                                                     distance_count, distance_speed)

    return PolarOdometers_inst, PolarOdometersTester_inst

class TestPolarOdometers(unittest.TestCase):

    def PolarOdometersTester(self, left_count, left_speed,
                                   right_count, right_speed,
                                   angle_count, angle_speed,
                                   distance_count, distance_speed):

        # initial position
        self.assertEquals(angle_count, 0)
        self.assertEquals(angle_speed, 0)
        self.assertEquals(distance_count, 0)
        self.assertEquals(distance_speed, 0)

        # go forward
        left_count.next = 1;
        left_speed.next = 200;
        right_count.next = 1;
        right_speed.next = 200; # assume 200 Hz (50 ms) for speeds: so 1 / 0.005
        print 'foo'
        yield angle_count, angle_speed, distance_count, distance_speed
        print 'bar'
        self.assertEquals(angle_count, (1 - 1) / 2)
        self.assertEquals(angle_speed, (200 - 200) / 2)
        self.assertEquals(distance_count, (1 + 1) / 2)
        self.assertEquals(distance_speed, (200 + 200) / 2)

        # spin right odometer
        # left_count does not change
        left_speed.next = 0;
        right_count.next = 20;
        right_speed.next = 3800; # (20 - 1) / 0.005)
        yield angle_count, angle_speed, distance_count, distance_speed
        self.assertEquals(angle_count, (20 - 1) / 2)
        self.assertEquals(angle_speed, (3800 - 0) / 2)
        self.assertEquals(distance_count, (20 + 1) / 2)
        self.assertEquals(distance_speed, (3800 + 0) / 2)

        # spin left odometer
        left_count.next = 20;
        left_speed.next = 3800;
        # right_count does not change
        right_speed.next = 0;
        yield angle_count, angle_speed, distance_count, distance_speed
        self.assertEquals(angle_count, (20 - 20) / 2)
        self.assertEquals(angle_speed, (0 - 3800) / 2)
        self.assertEquals(distance_count, (20 + 20) / 2)
        self.assertEquals(distance_speed, (0 + 3800) / 2)

        print 'DONE'

        raise StopSimulation()

    def testPolarOdometers(self):
        """ Ensures that filter works as espected """
        sim = Simulation(TestBench(self.PolarOdometersTester))
        sim.run()

if __name__ == '__main__':
    unittest.main()
