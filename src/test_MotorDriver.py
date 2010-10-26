import unittest

from myhdl import Signal, intbv, traceSignals, Simulation, delay, always

from MotorDriver import MotorDriver, LOW, HIGH

def ClkGen(clk):
    """ 25 MHz clock generator.
    clk -- clock signal
    """
    @always(delay(1)) # each delay unit simulates 0.02 us (half-period)
    def genClk():
        clk.next = not clk
    return genClk

def TestBench(MotorTester):
    """ Instanciate modules and wire things up.
    MotorTester -- test module to instanciate with MotorDriver and ClkGen
    """

    # create signals with default values
    pwm = Signal(LOW)
    dir = Signal(LOW)
    en_n = Signal(HIGH)
    clk = Signal(bool(0))
    consign = Signal(intbv(0)[12:])
    rst_n = Signal(HIGH)

    # instanciate modules
    MotorDriver_inst = traceSignals(MotorDriver,
        pwm, dir, en_n, clk, consign, rst_n)
    MotorTester_inst = MotorTester(
        pwm, dir, en_n, clk, consign, rst_n)
    ClkGen_inst = ClkGen(clk)

    return MotorDriver_inst, MotorTester_inst, ClkGen_inst

class TestMotorDriver(unittest.TestCase):

    def testMotorDriver(self):
        def MotorTester(pwm, dir, en_n, clk, consign, rst_n):
            val = intbv(128)[12:] # 1/8 max speed
            val[10] = HIGH       # whatever
            val[11] = LOW        # enable
            consign.next = val
            yield delay(1)

        """ Test MotorDriver """
        sim = Simulation(TestBench(MotorTester))
        sim.run(4096) # 2 PWM periods

if __name__ == '__main__':
    unittest.main()
