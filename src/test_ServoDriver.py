import unittest

from myhdl import Signal, intbv, traceSignals, Simulation, delay, always

from ServoDriver import ServoDriver, LOW, HIGH

def ClkGen(clk):
    """ 25 MHz clock generator.
    clk -- clock signal
    """
    @always(delay(1)) # each delay unit simulates 0.02 us (half-period)
    def genClk():
        clk.next = not clk
    return genClk

def TestBench(ServoTester):
    """ Instanciate modules and wire things up.
    ServoTester -- test module to instanciate with ServoDriver and ClkGen
    """

    # create signals with default values
    pwm = Signal(bool(0))
    clk = Signal(bool(0))
    consign = Signal(intbv(0)[16:])
    cs_n = Signal(HIGH)
    rst_n = Signal(HIGH)

    # instanciate modules
    ServoDriver_inst = traceSignals(ServoDriver,
        pwm, clk, consign, cs_n, rst_n)
    ServoTester_inst = ServoTester(
        pwm, clk, consign, cs_n, rst_n)
    ClkGen_inst = ClkGen(clk)

    return ServoDriver_inst, ServoTester_inst, ClkGen_inst

class TestServoDriver(unittest.TestCase):

    def testServoDriver(self):
        def ServoTester(pwm, clk, consign, cs_n, rst_n):
            consign.next = 37500

            # read consign
            cs_n.next = LOW
            yield delay(1)
            cs_n.next = HIGH

        """ Test ServoDriver """
        sim = Simulation(TestBench(ServoTester))
        sim.run(2000000) # 2 PWM periods

if __name__ == '__main__':
    unittest.main()
