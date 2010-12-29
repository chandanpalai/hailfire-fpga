import sys
sys.path.append('../lib')

import unittest

from myhdl import Signal, Simulation, StopSimulation, delay, intbv, join
from random import randrange
from Robot.Device.Motor import MotorDriver
from Robot.Utils.Constants import LOW, HIGH
from TestUtils import ClkGen, count_high

NR_TESTS = 5
NR_PERIODS_PER_TEST = 5

def TestBench(MotorTester):
    """ Instanciate modules and wire things up.
    MotorTester -- test module to instanciate with MotorDriver and ClkGen
    """

    # create signals with default values
    pwm = Signal(LOW)
    dir = Signal(LOW)
    en_n = Signal(HIGH)
    clk = Signal(LOW)
    speed = Signal(intbv(0, min = -2**10, max = 2**10))
    cs_n = Signal(HIGH)
    rst_n = Signal(HIGH)

    # instanciate modules
    MotorDriver_inst = MotorDriver(pwm, dir, en_n, clk, speed, cs_n, rst_n, False)
    MotorTester_inst = MotorTester(pwm, dir, en_n, clk, speed, cs_n, rst_n)
    ClkGen_inst = ClkGen(clk)

    return MotorDriver_inst, MotorTester_inst, ClkGen_inst

class TestMotorDriver(unittest.TestCase):

    def MotorTester(self, pwm, dir, en_n, clk, speed, cs_n, rst_n):
        def stimulus(dcl):
            speed.next = dcl

            # read speed (pull cs_n for 1 clk period)
            yield clk.posedge
            cs_n.next = LOW
            yield clk.posedge
            cs_n.next = HIGH

        def check(dcl):
            count = intbv(0)
            yield count_high(pwm, clk, count)
            self.assertEquals(count, min(abs(speed), speed.max - 1))

        for i in range(NR_TESTS):
            dcl = randrange(-2**10, 2**10)
            print 'ask for a PWM with duty cycle:', dcl, '/ 1024'

            # First period is not correct as the counter had already started
            # before the speed was given. Start testing at the second period
            yield stimulus(dcl) # set speed
            yield pwm.negedge # wait for end of PWM waveform of the first period

            for j in range(NR_PERIODS_PER_TEST - 1):
                yield pwm.posedge # wait for the beginning of the period
                yield check(dcl) # check the number of 'high's in this period

        print 'DONE'

        raise StopSimulation()

    def testMotorDriver(self):
        """ Test MotorDriver """
        sim = Simulation(TestBench(self.MotorTester))
        sim.run()

if __name__ == '__main__':
    unittest.main()
