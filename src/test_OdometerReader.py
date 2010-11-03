import unittest

from myhdl import Signal, Simulation, delay, intbv, join
from OdometerReader import OdometerReader
from TestUtils import ClkGen, LOW, HIGH

def TestBench(OdometerTester):
    """ Instanciate modules and wire things up.
    OdometerTester -- test module to instanciate with OdometerReader and ClkGen
    """

    # create signals with default values
    count = Signal(intbv(0)[16:])
    a = Signal(LOW)
    b = Signal(LOW)
    clk = Signal(LOW)
    rst_n = Signal(HIGH)

    # instanciate modules
    OdometerReader_inst = OdometerReader(count, a, b, clk, rst_n)
    OdometerTester_inst = OdometerTester(count, a, b, clk, rst_n)
    ClkGen_inst = ClkGen(clk)

    return OdometerReader_inst, OdometerTester_inst, ClkGen_inst

class TestOdometerReader(unittest.TestCase):

    def OdometerTester(self, count, a, b, clk, rst_n):
        def moveForward(count, a, b, clk, rst_n):
            for i in range(4):
                a.next = not a
                yield delay(10)
                b.next = not b
                yield delay(10)

        def keepStill(count, a, b, clk, rst_n):
            for i in range(80):
                yield delay(1)

        def moveBackward(count, a, b, clk, rst_n):
            for i in range(4):
                b.next = not b
                yield delay(10)
                a.next = not a
                yield delay(10)

        self.assertEquals(count, 0)

        yield moveForward(count, a, b, clk, rst_n)  # 0 to 8
        self.assertEquals(count, 8)

        yield keepStill(count, a, b, clk, rst_n)    # 8
        self.assertEquals(count, 8)

        yield moveBackward(count, a, b, clk, rst_n) # 8 to 0
        self.assertEquals(count, 0)

        yield moveBackward(count, a, b, clk, rst_n) # 0 to -8 = 0xFFF8
        self.assertEquals(count, 0xFFF8)

        yield keepStill(count, a, b, clk, rst_n)    # 0xFFF8
        self.assertEquals(count, 0xFFF8)

        yield moveForward(count, a, b, clk, rst_n)  # 0xFFF8 to 0
        self.assertEquals(count, 0)

    def testOdometerReader(self):
        """ Ensures that count works as espected """
        sim = Simulation(TestBench(self.OdometerTester))
        sim.run(500)

if __name__ == '__main__':
    unittest.main()
