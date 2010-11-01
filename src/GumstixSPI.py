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
    value_for_master -- big intbv whose lower bytes are sent to the master when it is reading (input)
    master_write_n -- active low when we need to handle a value sent by the master (output)
    value_from_master -- big intbv whose lower bytes are set by the master when it is writing (output)
    clk25 -- 25 MHz clock input
    rst_n -- active low reset input

    master_read_n is pulled low when the key and length are known and the key corresponds
    to a read operation (first bit is 0).

    master_write_n is pulled low when the key, length and sent value are known and the key
    corresponds to a write operation (first bit is 1).

    """

    # 8-bit value sent by the master (key, length, value bytes)
    # and signal toggling when new rxdata is available
    rxdata = Signal(intbv(0)[8:])
    rxrdy = Signal(LOW)

    # 8-bit value to send to the master (key, length, value bytes)
    # and signal toggling when new txdata can be accepted
    txdata = Signal(intbv(0)[8:])
    txrdy = Signal(LOW)

    # Controller driver
    SPISlave_inst = SPISlave(miso, mosi, sclk, ss_n, txdata, txrdy, rxdata, rxrdy, rst_n, 8)

    # Pulled low for 1 clock cycle when a new byte is received
    byte_received_n = Signal(HIGH)

    # Monitor rxrdy to pull byte_received_n low when needed
    @instance
    def PulsifyTogglingRxrdy():
        # previous value of the rxrdy signal to see when it has toggled.
        previous_rxrdy = LOW
        while True:
            yield clk25.posedge, rst_n.negedge
            if rst_n == LOW:
                byte_received_n.next = HIGH
                previous_rxrdy = rxrdy.val
            else:
                if rxrdy != previous_rxrdy: # changed
                    byte_received_n.next = LOW
                else:
                    byte_received_n.next = HIGH
                previous_rxrdy = rxrdy.val

    @instance
    def HandleProtocol():
        # Index of the currently read or written value byte
        index = len(value_for_master)

        # Our state in the KLV SPI protocol
        state = t_State.READ_SENT_KEY

        while True:
            yield clk25.posedge, rst_n.negedge

            if rst_n == LOW:
                state = t_State.READ_SENT_KEY

            # received byte
            elif byte_received_n == LOW:

                # handle the key sent by the master
                if state == t_State.READ_SENT_KEY:
                    # read key sent by master
                    key.next = rxdata

                    # need to read the length now
                    state = t_State.READ_SENT_LENGTH

                # handle the length of the value sent or expected by the master
                elif state == t_State.READ_SENT_LENGTH:
                    # read length sent by master
                    length.next = rxdata
                    index = 8 * (rxdata - 1)

                    # might need to read or write
                    if key[7] == 0: # master read
                        master_read_n.next = LOW
                        if rxdata != 0: # read some bytes
                            state = t_State.MASTER_READ
                        else: # read 0 byte: done
                            state = t_State.READ_SENT_KEY
                    else: # master write
                        if rxdata != 0: # write some bytes
                            state = t_State.MASTER_WRITE
                        else: # write 0 byte: done
                            master_write_n.next = LOW
                            state = t_State.READ_SENT_KEY

                # handle the value bytes sent by the master
                elif state == t_State.MASTER_WRITE:
                    # read value byte sent by master and store it
                    value_from_master.next[int(index) + 8:int(index)] = rxdata

                    if index >= 8:
                        # Get next byte
                        index -= 8
                    else:
                        # Got everything
                        master_write_n.next = LOW
                        state = t_State.READ_SENT_KEY
                        index = len(value_from_master)

                # decrement index when each value byte expected by the master has been sent
                elif state == t_State.MASTER_READ:
                    if index >= 8:
                        # Send next byte
                        index -= 8
                    else:
                        # Sent everything
                        state = t_State.READ_SENT_KEY
                        txdata.next = 0
                        index = len(value_for_master)

            # normal clock tick
            else:
                if state == t_State.READ_SENT_KEY:
                    master_write_n.next = HIGH
                    master_read_n.next = HIGH

                elif state == t_State.READ_SENT_LENGTH:
                    pass

                elif state == t_State.MASTER_WRITE:
                    pass

                # send the value bytes expected by the master
                elif state == t_State.MASTER_READ:
                    # reset signal after 1 clk
                    master_read_n.next = HIGH

                    # send next value byte to master
                    txdata.next = value_for_master[int(index) + 8:int(index)]

    return instances()
