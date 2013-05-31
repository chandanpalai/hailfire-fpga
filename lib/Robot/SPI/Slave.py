from myhdl import Signal, enum, intbv, always_comb, instance, instances
from Robot.Utils.Constants import LOW, HIGH

t_State = enum('IDLE', 'TRANSFER')

def SPISlave(spi_tx, spi_rx, spi_clk, spi_ss_n, txdata, txrdy, rxdata, rxrdy, rst_n, n=8, cpol=0, cpha=1):
    """

    SPI Generic Driver

    spi_rx

        SPI input signal:
         - MISO when this module acts as the master
         - MOSI when this module acts as a slave

    spi_tx

        SPI output signal:
         - MOSI when this module acts as the master
         - MISO when this module acts as a slave

    spi_clk

        SPI clock signal

        This is always an input. This module is master or slave depending on
        the source of the clock:
         - outside of the FPGA: it acts as a slave
         - generated inside the FPGA: it acts as a master

        The spi_clk signal must be transmitted to the slave, too, when this
        module is master, and that must be handled outside this module.

    spi_ss_n

        SPI active low slave select signal

        Like the SPI clock signal, this is always an input:
         - a signal that there is something to transmit (master)
         - a true slave select when this module acts as a slave

        The spi_ss_n signal must be transmitted to the slave, too, when this
        module is master, and that must be handled outside this module.

    txdata

        n-bit internal input with data to be transmitted.

    txrdy

        Toggles when new txdata can be accepted.

    rxdata

        n-bit internal output with data received.

    rxrdy

        Toggles when new rxdata is available.

    rst_n

        Active low reset input.

    n

        Data width parameter. Defaults to 8-bit words.

    cpol

        Clock Polarity:
         - if cpol = 0, the base value of the clock is LOW
         - if cpol = 1, the vase value of the clock is HIGH

    cpha

        Clock Phase:
         - if cpol = 0:
            - if cpha = 0, data is captured on the clock's rising edge and data is propagated on a falling edge.
            - if cpha = 1, data is captured on the clock's falling edge and data is propagated on a rising edge.
         - if cpol = 1:
            - if cpha = 0, data is captured on the clock's falling edge and data is propagated on a rising edge.
            - if cpha = 1, data is captured on the clock's rising edge and data is propagated on a falling edge.

        Note that with cpha = 0, the data must be stable for a half cycle before the first clock cycle.

        For all CPOL and CPHA modes, the initial clock value must be stable before the chip select line goes active.

    """

    assert cpha == 1, 'Unimplemented CPHA mode'

    cnt = Signal(intbv(0, min=0, max=n))

    # Copies of external signals
    i_tx = Signal(LOW)
    i_rx = Signal(LOW)
    i_clk = Signal(LOW)
    i_ss_n = Signal(HIGH)

    @always_comb
    def CombinatorialLogic():
        """ Combinatorial logic """
        spi_tx.next = i_tx
        i_rx.next = spi_rx
        # invert clock if necessary to only deal with CPOL=0 internally
        i_clk.next = spi_clk if cpol == 0 else not spi_clk
        i_ss_n.next = spi_ss_n

    @instance
    def RX():
        """ Capture on falling (mode 1) or rising (mode 3) edge """
        sreg = intbv(0)[n:]
        while True:
            yield i_clk.negedge
            if i_ss_n == LOW:
                sreg[n:1] = sreg[n-1:]
                sreg[0] = i_rx
                if cnt == n-1:
                    rxdata.next = sreg
                    rxrdy.next = not rxrdy

    @instance
    def TX():
        """ Propagate on rising (mode 1) or falling (mode 3) edge """
        sreg = intbv(0)[n:]
        state = t_State.IDLE
        while True:
            yield i_clk.posedge, rst_n.negedge
            if rst_n == LOW:
                state = t_State.IDLE
                cnt.next = 0
            else:
                if state == t_State.IDLE:
                    if i_ss_n == LOW:
                        sreg[:] = txdata
                        txrdy.next = not txrdy
                        state = t_State.TRANSFER
                        cnt.next = 0
                elif state == t_State.TRANSFER:
                    sreg[n:1] = sreg[n-1:]
                    if cnt == n-2:
                        state = t_State.IDLE
                    cnt.next = cnt + 1
                i_tx.next = sreg[n-1]

    return instances()
