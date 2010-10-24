from myhdl import Signal, intbv, instance

ACTIVE_n, INACTIVE_n = bool(0), bool(1)
IDLE, TRANSFER = bool(0), bool(1)

def SPISlave(miso, mosi, sclk, ss_n, txdata, txrdy, rxdata, rxrdy, rst_n, n=8):
    """ SPI Slave model.

    miso -- master in, slave out serial output
    mosi -- master out, slave in serial input
    sclk -- shift clock input
    ss_n -- active low slave select input
    txdata -- n-bit input with data to be transmitted
    txrdy -- toggles when new txdata can be accepted
    rxdata -- n-bit output with data received
    rxrdy -- toggles when new rxdata is available
    rst_n -- active low reset input
    n -- data width parameter

    """

    cnt = Signal(intbv(0, min=0, max=n))

    @instance
    def RX():
        sreg = intbv(0)[n:]
        while True:
            yield sclk.negedge
            if ss_n == ACTIVE_n:
                sreg[n:1] = sreg[n-1:]
                sreg[0] = mosi
                if cnt == n-1:
                    rxdata.next = sreg
                    rxrdy.next = not rxrdy

    @instance
    def TX():
        sreg = intbv(0)[n:]
        state = IDLE
        while True:
            yield sclk.posedge, rst_n.negedge
            if rst_n == ACTIVE_n:
                state = IDLE
                cnt.next = 0
            else:
                if state == IDLE:
                    if ss_n == ACTIVE_n:
                        sreg[:] = txdata
                        txrdy.next = not txrdy
                        state = TRANSFER
                        cnt.next = 0
                else: # TRANSFER
                    sreg[n:1] = sreg[n-1:]
                    if cnt == n-2:
                        state = IDLE
                    cnt.next = (cnt + 1) % n
                miso.next = sreg[n-1]

    return RX, TX
