import sys
sys.path.append('../lib')

import unittest
from random import randrange

from myhdl import Signal, Simulation, StopSimulation, intbv, join, toVHDL, traceSignals, downrange

from Robot.Device.MCP3008 import MCP3008Driver
from Robot.Utils.Constants import LOW, HIGH
from TestUtils import ClkGen, spi_transfer

NR_TESTS = 16 # twice each channel

def TestBench(MCP3008Tester):

    ch1 = Signal(intbv(0)[10:])
    ch2 = Signal(intbv(0)[10:])
    ch3 = Signal(intbv(0)[10:])
    ch4 = Signal(intbv(0)[10:])
    ch5 = Signal(intbv(0)[10:])
    ch6 = Signal(intbv(0)[10:])
    ch7 = Signal(intbv(0)[10:])
    ch8 = Signal(intbv(0)[10:])
    spi_clk = Signal(LOW)
    spi_ss_n = Signal(HIGH)
    spi_miso = Signal(LOW)
    spi_mosi = Signal(LOW)
    clk = Signal(LOW)
    rst_n = Signal(HIGH)

    MCP3008Driver_inst = traceSignals(MCP3008Driver,
        ch1, ch2, ch3, ch4, ch5, ch6, ch7, ch8,
        spi_clk, spi_ss_n, spi_miso, spi_mosi, clk, rst_n)

    MCP3008Tester_inst = MCP3008Tester(
        ch1, ch2, ch3, ch4, ch5, ch6, ch7, ch8,
        spi_clk, spi_ss_n, spi_miso, spi_mosi, clk, rst_n)

    ClkGen_inst = ClkGen(clk)

    return MCP3008Driver_inst, MCP3008Tester_inst, ClkGen_inst

class TestMCP3008Driver(unittest.TestCase):

    def MCP3008Tester(self,
                 ch1, ch2, ch3, ch4, ch5, ch6, ch7, ch8,
                 spi_clk, spi_ss_n, spi_miso, spi_mosi, clk, rst_n):

        def spi_slave(channel, values):
            """

            Send data like an MCP3008 would

            CPOL=1 and CPHA=1 here:
             - the base value of the clock is HIGH
             - data is captured on the clock's rising edge and data is
               propagated on a falling edge.

            """
            yield spi_ss_n.negedge

            # wait for start bit: first clock with mosi high
            while spi_mosi == LOW:
                yield spi_clk.posedge
            self.assertEqual(spi_mosi, HIGH)

            # single-ended bit
            yield spi_clk.posedge
            self.assertEqual(spi_mosi, HIGH)

            # channel bits
            for i in downrange(len(channel)):
                yield spi_clk.posedge
                channel[i] = spi_mosi

            print 'master wants channel:', channel

            # one more bit for conversion
            yield spi_clk.posedge

            # then MCP3008 sends a null byte
            yield spi_clk.negedge
            spi_miso.next = LOW

            # and then the 10-bit value
            value = values[channel]
            print 'slave sending:', value
            for i in downrange(len(value)):
                yield spi_clk.negedge
                spi_miso.next = value[i]

            yield spi_ss_n.posedge
            print "slave done"

        def check(channel, channels, values):
            yield spi_ss_n.posedge
            self.assertEqual(channels[channel], values[channel])

        channels = [ch1, ch2, ch3, ch4, ch5, ch6, ch7, ch8]

        for i in range(NR_TESTS):
            channel = intbv(0)[3:]
            values = [intbv(randrange(2**10))[10:] for i in range(9)]
            yield join(spi_slave(channel, values), check(channel, channels, values))

        print 'ch1:', ch1
        print 'ch2:', ch2
        print 'ch3:', ch3
        print 'ch4:', ch4
        print 'ch5:', ch5
        print 'ch6:', ch6
        print 'ch7:', ch7
        print 'ch8:', ch8

        print 'DONE'
        raise StopSimulation()

    def testMCP3008(self):
        """ Test MCP3008Driver """
        sim = Simulation(TestBench(self.MCP3008Tester))
        sim.run()

if __name__ == '__main__':
    unittest.main()
