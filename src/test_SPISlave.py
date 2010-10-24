import unittest
from random import randrange

from myhdl import Signal, intbv, traceSignals, Simulation, join, delay, downrange

from SPISlave import SPISlave, ACTIVE_n, INACTIVE_n

n = 16
NR_TESTS = 100

def TestBench(SPITester, n):

    miso = Signal(bool(0))
    mosi = Signal(bool(0))
    sclk = Signal(bool(0))
    ss_n = Signal(INACTIVE_n)
    txrdy = Signal(bool(0))
    rxrdy = Signal(bool(0))
    rst_n = Signal(INACTIVE_n)
    txdata = Signal(intbv(0)[n:])
    rxdata = Signal(intbv(0)[n:])

    SPISlave_inst = traceSignals(SPISlave,
        miso, mosi, sclk, ss_n,
        txdata, txrdy, rxdata, rxrdy, rst_n, n=n)

    SPITester_inst = SPITester(
        miso, mosi, sclk, ss_n,
        txdata, txrdy, rxdata, rxrdy, rst_n, n=n)

    return SPISlave_inst, SPITester_inst

class TestSPISlave(unittest.TestCase):

    def RXTester(self, miso, mosi, sclk, ss_n,
                 txdata, txrdy, rxdata, rxrdy,
                 rst_n, n):

        def stimulus(data):
            yield delay(50)
            ss_n.next = ACTIVE_n
            yield delay(10)
            for i in downrange(n):
                sclk.next = 1
                mosi.next = data[i]
                yield delay(10)
                sclk.next = 0
                yield delay(10)
            ss_n.next = INACTIVE_n

        def check(data):
            yield rxrdy
            self.assertEqual(rxdata, data)

        for i in range(NR_TESTS):
            data = intbv(randrange(2**n))
            yield join(stimulus(data), check(data))

    def testRX(self):
        """ Test RX path of SPI Slave """
        sim = Simulation(TestBench(self.RXTester, n))
        sim.run(quiet=1)

if __name__ == '__main__':
    unittest.main()
