from myhdl import Signal, enum, intbv, always, instance, instances
from SPISlave import SPISlave

LOW, HIGH = bool(0), bool(1)

t_State = enum('READ_SENT_KEY', 'READ_SENT_LENGTH', 'MASTER_WRITE', 'MASTER_READ')

def GumstixSPI(miso, mosi, sclk, ss_n, key, length, master_read_n, value_for_master, master_write_n, value_from_master, clk25, rst_n):
    """ Protocol driver for SPI slave communication with the Gumstix.

    miso -- master in, slave out serial output
    mosi -- master out, slave in serial input
    sclk -- shift clock input
    ss_n -- active low slave select input
    key -- address sent by the master (8-bit output)
    length -- number of bytes sent or expected by the master for the value (8-bit output)
    master_read_n -- active low when we need to send a value back to the master (output)
    value_for_master -- array of 8-bit values to send to the master when it is reading (input)
    master_write_n -- active low when we need to handle a value sent by the master (output)
    value_from_master -- array of 8-bit values sent by the master when it is writing (output)
    clk25 -- 25 MHz clock input
    rst_n -- active low reset input

    master_read_n is pulled low when the key and length are known and the key corresponds
    to a read operation (first bit is 0).

    master_write_n is pulled low when the key, length and sent value are known and the key
    corresponds to a write operation (first bit is 1).

    """

    # 8-bit value sent by the master (key, length, value bytes)
    # signal toggling when new rxdata is available
    # previous value of that signal to see when it has toggled.
    rxdata = Signal(intbv(0)[8:])
    rxrdy = Signal(LOW)
    previous_rxrdy = Signal(LOW)

    # 8-bit value to send to the master (key, length, value bytes)
    # signal toggling when new txdata can be accepted
    # previous value of that signal to see when it has toggled.
    txdata = Signal(intbv(0)[8:])
    txrdy = Signal(LOW)

    # Controller driver
    SPISlave_inst = SPISlave(miso, mosi, sclk, ss_n, txdata, txrdy, rxdata, rxrdy, rst_n, 8)

    # Our state: where we are in the KLV-encoded pairs sent by the master
    state = Signal(t_State.READ_SENT_KEY)

    # Index of the currently read of written value byte
    index = Signal(intbv(0)[8:])

    @instance
    def HandleProtocol():
        while True:
            yield clk25.posedge, rst_n.negedge
            if rst_n == LOW:
                state.next = t_State.READ_SENT_KEY
            else:
                # handle the key sent by the master
                if state == t_State.READ_SENT_KEY:
                    # reset
                    txdata.next = 0
                    index.next = 0
                    master_write_n.next = HIGH
                    master_read_n.next = HIGH

                    # wait for the key byte to be received
                    while rxrdy == previous_rxrdy: # no change
                        yield rxrdy.posedge, rxrdy.negedge
                    previous_rxrdy.next = rxrdy

                    # read key sent by master
                    key.next = rxdata

                    # need to read the length now
                    state.next = t_State.READ_SENT_LENGTH

                # handle the length of the value sent or expected by the master
                elif state == t_State.READ_SENT_LENGTH:
                    # wait for the length byte to be received
                    while rxrdy == previous_rxrdy: # no change
                        yield rxrdy.posedge, rxrdy.negedge
                    previous_rxrdy.next = rxrdy

                    # read length sent by master
                    length.next = rxdata

                    # might need to read or write
                    if key[7] == 0: # master read
                        master_read_n.next = LOW
                        if rxdata != 0: # read some bytes
                            state.next = t_State.MASTER_READ
                        else: # read 0 byte: done
                            state.next = t_State.READ_SENT_KEY
                    else: # master write
                        if rxdata != 0: # write some bytes
                            state.next = t_State.MASTER_WRITE
                        else: # write 0 byte: done
                            master_write_n.next = LOW
                            state.next = t_State.READ_SENT_KEY

                # handle the value bytes sent by the master
                elif state == t_State.MASTER_WRITE:
                    # wait for the value byte to be received
                    while rxrdy == previous_rxrdy: # no change
                        yield rxrdy.posedge, rxrdy.negedge
                    previous_rxrdy.next = rxrdy

                    # read value byte sent by master and store it
                    value_from_master[int(index)].next = rxdata

                    if index == length - 1:
                        # Got everything
                        master_write_n.next = LOW
                        state.next = t_State.READ_SENT_KEY
                    else:
                        # Get next byte
                        index.next = index + 1

                # send the value bytes expected by the master
                elif state == t_State.MASTER_READ:
                    # reset signal after 1 clk
                    master_read_n.next = HIGH

                    # send value byte to master
                    txdata.next = value_for_master[int(index)]

                    if index == length - 1:
                        # Sent everything
                        state.next = t_State.READ_SENT_KEY
                    else:
                        # Send next byte
                        index.next = index + 1

                    # wait for the value byte to be completely sent, by looking
                    # for the placeholder byte sent by the master to be received.
                    while rxrdy == previous_rxrdy: # no change
                        yield rxrdy.posedge, rxrdy.negedge
                    previous_rxrdy.next = rxrdy

                # should not heppen
                else:
                    raise ValueError("Undefined state")

    return SPISlave_inst, HandleProtocol
