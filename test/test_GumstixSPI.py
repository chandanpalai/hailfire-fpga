import sys
sys.path.append('../lib')

import unittest
from random import randrange

from myhdl import Signal, intbv, traceSignals, Simulation, StopSimulation, join, delay, downrange, concat, always

from Robot.SPI.Protocol.KLVSlave import GumstixSPI
from TestUtils import ClkGen, random_write, random_read, spi_transfer, LOW, HIGH

MAX_LENGTH = 256 # max length of values read or written by the Gumstix

def TestBench(GumstixSPITester):

    miso = Signal(LOW)
    mosi = Signal(LOW)
    sclk = Signal(LOW)
    ss_n = Signal(HIGH)
    key = Signal(intbv(0)[8:])
    length = Signal(intbv(0)[8:])
    master_read_n = Signal(HIGH)
    value_for_master = Signal(intbv(0)[MAX_LENGTH*8:])
    master_write_n = Signal(HIGH)
    value_from_master = Signal(intbv(0)[MAX_LENGTH*8:])
    clk = Signal(bool(0))
    rst_n = Signal(HIGH)

    GumstixSPI_inst = traceSignals(GumstixSPI,
        miso, mosi, sclk, ss_n,
        key, length, master_read_n, value_for_master, master_write_n, value_from_master,
        clk, rst_n)

    GumstixSPITester_inst = GumstixSPITester(
        miso, mosi, sclk, ss_n,
        key, length, master_read_n, value_for_master, master_write_n, value_from_master,
        clk, rst_n)

    ClkGen_inst = ClkGen(clk)

    return GumstixSPI_inst, GumstixSPITester_inst, ClkGen_inst

class TestGumstixSPI(unittest.TestCase):

    def Tester(self, miso, mosi, sclk, ss_n,
                 key, length, master_read_n, value_for_master, master_write_n, value_from_master,
                 clk, rst_n):

        master_to_slave = intbv(0)
        slave_to_master = intbv(0)

        def check_write():
            """ Check that what the SPI slave read corresponds to sent data """
            yield master_write_n.negedge
            n = len(self.master_to_slave)
            print 'master sent', n, 'bytes'
            print 'slave read key:', hex(key)
            self.assertEqual(key, self.master_to_slave[n:n-8])
            print 'slave read length:', hex(length)
            self.assertEqual(length, self.master_to_slave[n-8:n-16])
            if length > 0:
                print 'slave should have read value:', hex(self.master_to_slave[n-16:])
                self.assertEqual(value_from_master[length*8:], self.master_to_slave[n-16:])

        def check_read():
            """ Check that what the SPI slave sent corresponds to expected data """
            yield master_read_n.negedge
            n = len(self.master_to_slave)
            print 'master sent', n, 'bytes'
            print 'slave read key:', hex(key)
            self.assertEqual(key, self.master_to_slave[n:n-8])
            print 'slave read length:', hex(length)
            self.assertEqual(length, self.master_to_slave[n-8:n-16])
            if length > 0:
                print 'slave ask for', length, 'bytes to send them to master'
                value_for_master.next[length*8:] = randrange(256*length)

            # Wait for end of transfer
            yield ss_n.posedge
            if length > 0:
                print 'slave sent value:', hex(value_for_master[length*8:])
                self.assertEqual(value_for_master[length*8:], self.slave_to_master[n-16:])

        # Send write commands with values from 0 to 8 bytes
        for i in range(10):
            self.master_to_slave = random_write(i)
            self.slave_to_master = intbv(0)
            print "\nwrite test", 'master sends:', hex(self.master_to_slave)
            yield join(spi_transfer(miso, mosi, sclk, ss_n, self.master_to_slave, self.slave_to_master), check_write())
            print 'slave responded:', hex(self.slave_to_master)

        # Send write commands with values from 8 to 0 bytes
        for i in downrange(10):
            self.master_to_slave = random_write(i)
            self.slave_to_master = intbv(0)
            print "\nwrite test", 'master sends:', hex(self.master_to_slave)
            yield join(spi_transfer(miso, mosi, sclk, ss_n, self.master_to_slave, self.slave_to_master), check_write())
            print 'slave responded:', hex(self.slave_to_master)

        # Send read commands with values from 0 to 8 bytes
        for i in range(10):
            self.master_to_slave = random_read(i)
            self.slave_to_master = intbv(0)
            print "\nread test", 'master sends:', hex(self.master_to_slave)
            yield join(spi_transfer(miso, mosi, sclk, ss_n, self.master_to_slave, self.slave_to_master), check_read())
            print 'slave responded:', hex(self.slave_to_master)

        # Send read commands with values from 8 to 0 bytes
        for i in downrange(10):
            self.master_to_slave = random_read(i)
            self.slave_to_master = intbv(0)
            print "\nread test", 'master sends:', hex(self.master_to_slave)
            yield join(spi_transfer(miso, mosi, sclk, ss_n, self.master_to_slave, self.slave_to_master), check_read())
            print 'slave responded:', hex(self.slave_to_master)

        raise StopSimulation()

    def testGumstixSPI(self):
        sim = Simulation(TestBench(self.Tester))
        sim.run()

if __name__ == '__main__':
    unittest.main()
