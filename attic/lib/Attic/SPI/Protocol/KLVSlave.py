from myhdl import Signal, enum, intbv, always, instance, instances
from Attic.SPI.Slave import SPISlave
from Robot.Utils.Constants import LOW, HIGH

t_State = enum('READ_KEY', 'GET_READ_LENGTH', 'GET_WRITE_LENGTH', 'MASTER_WRITE', 'MASTER_READ')

def KLVSlave(miso, mosi, sclk, ss_n, key, length, master_read_n, value_for_master, master_write_n, value_from_master, clk25, rst_n):
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
    SPISlave_inst = SPISlave(miso, mosi, sclk, ss_n, txdata, txrdy, rxdata, rxrdy, rst_n, n=8, cpol=0, cpha=1)

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
        state = t_State.READ_KEY

        while True:
            yield clk25.posedge, rst_n.negedge
            if rst_n == LOW:
                state = t_State.READ_KEY
            else:
                # reset signals after 1 clk
                master_write_n.next = HIGH
                master_read_n.next = HIGH

                # do stuff at clock tick
                if state == t_State.READ_KEY:
                    pass
                elif state == t_State.GET_READ_LENGTH:
                    pass
                elif state == t_State.GET_WRITE_LENGTH:
                    pass
                elif state == t_State.MASTER_WRITE:
                    pass
                elif state == t_State.MASTER_READ:
                    # send next value byte to master
                    txdata.next = value_for_master[(index + 8):index]

                # do stuff at clock tick when a byte has been received
                if byte_received_n == LOW:

                    # handle the key sent by the master
                    if state == t_State.READ_KEY:
                        # read key sent by master
                        key.next = rxdata

                        # need to read the length now
                        # does the master want to read or write?
                        if rxdata[7] == 0: # master read
                            state = t_State.GET_READ_LENGTH
                        else: # master write
                            state = t_State.GET_WRITE_LENGTH

                    # handle the length of the value sent by the master
                    elif state == t_State.GET_WRITE_LENGTH:
                        # read length sent by master
                        length.next = rxdata
                        index = 8 * (rxdata - 1)

                        if rxdata != 0: # write some bytes
                            state = t_State.MASTER_WRITE
                        else: # write 0 byte: done
                            master_write_n.next = LOW
                            state = t_State.READ_KEY

                    # handle the length of the value expected by the master
                    elif state == t_State.GET_READ_LENGTH:
                        # read length sent by master
                        length.next = rxdata
                        index = 8 * (rxdata - 1)

                        master_read_n.next = LOW

                        if rxdata != 0: # read some bytes
                            state = t_State.MASTER_READ
                        else: # read 0 byte: done
                            state = t_State.READ_KEY

                    # handle the value bytes sent by the master
                    elif state == t_State.MASTER_WRITE:
                        # read value byte sent by master and store it
                        value_from_master.next[(index + 8):index] = rxdata

                        if index >= 8:
                            # Get next byte
                            index -= 8
                        else:
                            # Got everything
                            master_write_n.next = LOW
                            state = t_State.READ_KEY
                            index = len(value_from_master)

                    # decrement index when each value byte expected by the master has been sent
                    elif state == t_State.MASTER_READ:
                        if index >= 8:
                            # Send next byte
                            index -= 8
                        else:
                            # Sent everything
                            state = t_State.READ_KEY
                            txdata.next = 0
                            index = len(value_for_master)

    return instances()
