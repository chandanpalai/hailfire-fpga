import sys
sys.path.append('../lib')

import unittest
from random import randrange

from myhdl import Signal, Simulation, intbv, join

from Robot.SPI.Slave import SPISlave
from Robot.Utils.Constants import LOW, HIGH
from TestUtils import spi_transfer

n = 8
NR_TESTS = 10

def TestBench(SPITester, n):

    miso = Signal(LOW)
    mosi = Signal(LOW)
    sclk = Signal(LOW)
    ss_n = Signal(HIGH)
    txrdy = Signal(LOW)
    rxrdy = Signal(LOW)
    rst_n = Signal(HIGH)
    txdata = Signal(intbv(0)[n:])
    rxdata = Signal(intbv(0)[n:])

    SPISlave_inst = SPISlave(
        miso, mosi, sclk, ss_n,
        txdata, txrdy, rxdata, rxrdy, rst_n, n=n, cpol=0, cpha=1)

    SPITester_inst = SPITester(
        miso, mosi, sclk, ss_n,
        txdata, txrdy, rxdata, rxrdy, rst_n, n=n)

    return SPISlave_inst, SPITester_inst

class TestSPISlave(unittest.TestCase):

    def RXTester(self, miso, mosi, sclk, ss_n,
                 txdata, txrdy, rxdata, rxrdy,
                 rst_n, n):

        def check():
            yield rxrdy
            print 'master sent:', hex(self.master_to_slave)
            print 'slave read:', hex(rxdata)
            self.assertEqual(rxdata, self.master_to_slave)

        for i in range(NR_TESTS):
            print "\nmaster write test"
            self.master_to_slave = intbv(randrange(2**n))[n:]
            self.slave_to_master = intbv(0)[n:]
            yield join(spi_transfer(miso, mosi, sclk, ss_n, self.master_to_slave, self.slave_to_master), check())

    def TXTester(self, miso, mosi, sclk, ss_n,
                 txdata, txrdy, rxdata, rxrdy,
                 rst_n, n):

        def check():
            yield rxrdy
            print 'slave sent:', hex(txdata)
            print 'master read:', hex(self.slave_to_master)
            self.assertEqual(self.slave_to_master, txdata)

        for i in range(NR_TESTS):
            print "\nmaster read test"
            txdata.next = intbv(randrange(2**n))
            self.master_to_slave = intbv(0)[n:]
            self.slave_to_master = intbv(0)[n:]
            yield join(spi_transfer(miso, mosi, sclk, ss_n, self.master_to_slave, self.slave_to_master), check())

    def testRX(self):
        """ Test RX path of SPI Slave """
        sim = Simulation(TestBench(self.RXTester, n))
        sim.run()

    def testTX(self):
        """ Test TX path of SPI Slave """
        sim = Simulation(TestBench(self.TXTester, n))
        sim.run()

if __name__ == '__main__':
    unittest.main()
