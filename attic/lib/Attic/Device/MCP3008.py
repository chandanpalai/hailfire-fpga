from myhdl import Signal, always, always_comb, enum, instance, instances, intbv, concat
from Attic.SPI.Slave import SPISlave
from Robot.Utils.Constants import LOW, HIGH, CLK_FREQ

t_State = enum('IDLE', 'READING')

def MCP3008Driver(
    ch1, ch2, ch3, ch4, ch5, ch6, ch7, ch8,
    spi_clk, spi_ss_n, spi_miso, spi_mosi,
    clk25, rst_n):
    """

    Driver for Microchip MCP3008 8-Channel 10-Bit A/D Converter

    ch[1-8]

        Output 10-bit unsigned value for each A/D channel.

    spi_clk, spi_ss_n, spi_miso, spi_mosi

        SPI signals for communication with MCP3008

    clk25

        25 MHz clock input.

    rst_n

        Active low reset input.

    """

    # Internal SPI signals
    i_clk = Signal(HIGH) # cpol=1
    i_ss_n = Signal(HIGH)
    i_rx = Signal(LOW)
    i_tx = Signal(LOW)

    # Use 17-bit words: we send the start bit (a 1), then the single-ended bit
    # (another 1), then 3 bits for the channel number, then 12 zeros. In the
    # response, only the 10 lower bits matter.
    word_size = 17

    # The 17-bit data to send:
    # - start bit (a 1)
    # - single-ended bit (a 1)
    # - 3 bits for the channel (most significant bit first)
    # - 12 padding bits (we send zeros)
    txdata = Signal(intbv(0)[word_size:])
    # and signal toggling when new txdata can be accepted
    txrdy = Signal(LOW)

    # The 17-bit data we get back
    # - 6 padding bits
    # - a null byte
    # - the 10-bit value
    rxdata = Signal(intbv(0)[word_size:])
    # and signal toggling when new rxdata is available
    rxrdy = Signal(LOW)

    # Controller driver
    SPISlave_inst = SPISlave(i_tx, i_rx, i_clk, i_ss_n,
                             txdata, txrdy, rxdata, rxrdy,
                             rst_n, n=word_size, cpol=1, cpha=1)

    @always_comb
    def CombinatorialLogic():
        """ Combinatorial logic """
        spi_clk.next = i_clk
        spi_ss_n.next = i_ss_n
        spi_mosi.next = i_tx
        i_rx.next = spi_miso.next

    # Counter for 100kHz clock (counter must overflow twice per period)
    SPI_FREQ = 100000
    SPI_CNT_MAX = int(CLK_FREQ/(SPI_FREQ*2) - 1)

    # Counter for 30Hz read of each channel (so x8)
    READ_FREQ = 30
    READ_CNT_MAX = int(SPI_FREQ/(READ_FREQ*8) - 1)

    @instance
    def ADCProcess():
        state = t_State.IDLE
        channel = intbv(0)[3:]
        i_clk_cnt = intbv(0, min = 0, max = SPI_CNT_MAX + 1)
        read_cnt = intbv(0, min = 0, max = READ_CNT_MAX + 1)
        previous_rxrdy = LOW
        while True:
            yield clk25.posedge, rst_n.negedge
            if rst_n == LOW:
                state = t_State.IDLE
                read_cnt[:] = 0
                channel[:] = 0
                i_clk_cnt[:] = 0
                i_clk.next = HIGH
                i_ss_n.next = HIGH
            else:
                if state == t_State.IDLE:
                    i_ss_n.next = HIGH
                    i_clk.next = HIGH
                    if read_cnt == READ_CNT_MAX:
                        # Prepare command to read channel
                        state = t_State.READING
                        txdata.next = concat(HIGH, HIGH, channel, intbv(0)[12:])
                        read_cnt[:] = 0
                    else:
                        # Wait before next read
                        read_cnt += 1
                elif state == t_State.READING:
                    # Select slave
                    i_ss_n.next = LOW

                    # Generate SPI clock
                    if i_clk_cnt == SPI_CNT_MAX:
                        i_clk_cnt[:] = 0
                        i_clk.next = not i_clk
                    else:
                        i_clk_cnt += 1

                    # When done
                    if rxrdy != previous_rxrdy:
                        # Set output
                        if channel == 0:
                            ch1.next = rxdata[10:]
                        elif channel == 1:
                            ch2.next = rxdata[10:]
                        elif channel == 2:
                            ch3.next = rxdata[10:]
                        elif channel == 3:
                            ch4.next = rxdata[10:]
                        elif channel == 4:
                            ch5.next = rxdata[10:]
                        elif channel == 5:
                            ch6.next = rxdata[10:]
                        elif channel == 6:
                            ch7.next = rxdata[10:]
                        elif channel == 7:
                            ch8.next = rxdata[10:]

                        # Next time read next channel
                        if channel == 7:
                            channel[:] = 0
                        else:
                            channel += 1

                        # Back to waiting
                        state = t_State.IDLE
                        previous_rxrdy = rxrdy.val

    return instances()
