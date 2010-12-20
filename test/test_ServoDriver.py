import sys
sys.path.append('../lib')

import unittest

from myhdl import Signal, Simulation, StopSimulation, delay, intbv, join
from random import randrange
from Robot.Device.Servo import ServoDriver
from Robot.Utils.Constants import LOW, HIGH
from TestUtils import ClkGen, count_high

NR_TESTS = 2
NR_PERIODS_PER_TEST = 2

def TestBench(ServoTester):
    """ Instanciate modules and wire things up.
    ServoTester -- test module to instanciate with ServoDriver and ClkGen
    """

    # create signals with default values
    pwm = Signal(LOW)
    clk = Signal(LOW)
    consign = Signal(intbv(0)[16:])
    cs_n = Signal(HIGH)
    rst_n = Signal(HIGH)

    # instanciate modules
    ServoDriver_inst = ServoDriver(pwm, clk, consign, cs_n, rst_n, False)
    ServoTester_inst = ServoTester(pwm, clk, consign, cs_n, rst_n)
    ClkGen_inst = ClkGen(clk)

    return ServoDriver_inst, ServoTester_inst, ClkGen_inst

class TestServoDriver(unittest.TestCase):

    def ServoTester(self, pwm, clk, consign, cs_n, rst_n):
        def stimulus(dcl):
            consign.next = intbv(dcl)[16:] # duty cycle

            # read consign (pull cs_n for 1 clk period)
            yield clk.posedge
            cs_n.next = LOW
            yield clk.posedge
            cs_n.next = HIGH

        def check(dcl):
            count = intbv(0)
            yield count_high(pwm, clk, count)
            self.assertEquals(count, dcl)

        for i in range(NR_TESTS):
            dcl = randrange(12500, 62500) # min/max useful consigns
            print 'ask for a PWM with duty cycle:', dcl, '/ 500000'

            # First period is not correct as the counter had already started
            # before the consign was given. Start testing at the second period
            yield stimulus(dcl) # set consign
            yield pwm.negedge # wait for end of PWM waveform of the first period

            for j in range(NR_PERIODS_PER_TEST - 1):
                yield pwm.posedge # wait for the beginning of the period
                yield check(dcl) # check the number of 'high's in this period

        print 'DONE'

        raise StopSimulation()

    def testServoDriver(self):
        """ Test ServoDriver """
        sim = Simulation(TestBench(self.ServoTester))
        sim.run()

if __name__ == '__main__':
    unittest.main()
