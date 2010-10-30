import unittest
from random import randrange

from myhdl import Signal, intbv, traceSignals, Simulation, join, delay, downrange, concat, always

from GumstixSPI import GumstixSPI, LOW, HIGH

def ClkGen(clk):
    """ 25 MHz clock generator.
    clk -- clock signal
    """
    @always(delay(1)) # each delay unit simulates 0.02 us (half-period)
    def genClk():
        clk.next = not clk
    return genClk

def TestBench(GumstixSPITester):

    miso = Signal(LOW)
    mosi = Signal(LOW)
    sclk = Signal(LOW)
    ss_n = Signal(HIGH)
    key = Signal(intbv(0)[8:])
    length = Signal(intbv(0)[8:])
    master_read_n = Signal(HIGH)
    value_for_master = [Signal(intbv(0)[8:]) for i in range(256)]
    master_write_n = Signal(HIGH)
    value_from_master = [Signal(intbv(0)[8:]) for i in range(256)]
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

        def random_write(n):
            """ Generate and return a random intbv suitable for a write operation """
            data = intbv(randrange(0xFF))[8:] # key
            data[7] = 1 # write
            data = concat(data, intbv(n)[8:]) # length
            for j in range(n):
                data = concat(data, intbv(randrange(0xFF))[8:]) # value bytes
            return data

        def random_read(n):
            """ Generate and return a random intbv suitable for a read operation """
            data = intbv(randrange(0xFF))[8:] # key
            data[7] = 0 # read
            data = concat(data, intbv(n)[8:]) # length
            for j in range(n):
                data = concat(data, intbv(0)[8:]) # placeholder bytes for value
            return data

        def stimulus():
            """ Send data like an SPI master would """
            yield delay(50)
            ss_n.next = LOW
            yield delay(10)
            for i in downrange(len(self.master_to_slave)):
                sclk.next = 1
                mosi.next = self.master_to_slave[i]
                yield delay(10)
                sclk.next = 0
                self.slave_to_master[i] = miso
                yield delay(10)
            ss_n.next = HIGH

        def check_write():
            """ Check that what the SPI slave read corresponds to sent data """
            yield master_write_n.negedge
            n = len(self.master_to_slave)
            print 'master sent', n, 'bytes'
            print 'slave read key:', hex(key)
            self.assertEqual(key, self.master_to_slave[n:n-8])
            print 'slave read length:', hex(length)
            self.assertEqual(length, self.master_to_slave[n-8:n-16])
            for j in range((n-16)/8):
                print 'slave read value byte', j, ':', hex(value_from_master[j])
                self.assertEqual(value_from_master[j], self.master_to_slave[n-16-8*j:n-16-8*(j+1)])

        def check_read():
            """ Check that what the SPI slave sent corresponds to expected data """
            yield master_read_n.negedge
            n = len(self.master_to_slave)
            print 'master sent', n, 'bytes'
            print 'slave read key:', hex(key)
            self.assertEqual(key, self.master_to_slave[n:n-8])
            print 'slave read length:', hex(length)
            self.assertEqual(length, self.master_to_slave[n-8:n-16])
            print 'slave ask for', length, 'bytes to send them to master'
            for j in range(length):
                value_for_master[j].next = key + j
            # Wait for end of transfer
            yield ss_n.posedge
            for j in range((n-16)/8):
                print 'slave sent value byte', j, ':', hex(value_for_master[j])
                self.assertEqual(value_for_master[j], self.slave_to_master[n-16-8*j:n-16-8*(j+1)])

        # Send write commands with values from 0 to 8 bytes
        for i in range(10):
            self.master_to_slave = random_write(i)
            self.slave_to_master = intbv(0)
            print "\nwrite test", 'master sends:', hex(self.master_to_slave)
            yield join(stimulus(), check_write())
            print 'slave responded:', hex(self.slave_to_master)

        # Send write commands with values from 8 to 0 bytes
        for i in downrange(10):
            self.master_to_slave = random_write(i)
            self.slave_to_master = intbv(0)
            print "\nwrite test", 'master sends:', hex(self.master_to_slave)
            yield join(stimulus(), check_write())
            print 'slave responded:', hex(self.slave_to_master)

        # Send read commands with values from 0 to 8 bytes
        for i in range(10):
            self.master_to_slave = random_read(i)
            self.slave_to_master = intbv(0)
            print "\nread test", 'master sends:', hex(self.master_to_slave)
            yield join(stimulus(), check_read())
            print 'slave responded:', hex(self.slave_to_master)

        # Send read commands with values from 8 to 0 bytes
        for i in downrange(10):
            self.master_to_slave = random_read(i)
            self.slave_to_master = intbv(0)
            print "\nread test", 'master sends:', hex(self.master_to_slave)
            yield join(stimulus(), check_read())
            print 'slave responded:', hex(self.slave_to_master)

    def testGumstixSPI(self):
        sim = Simulation(TestBench(self.Tester))
        sim.run(45000) # used Gtkwave

if __name__ == '__main__':
    unittest.main()
