from myhdl import ConcatSignal, Signal, always, always_comb, concat, enum, instance, instances, intbv
from Robot.Device.LED import LEDDriver
from Robot.Device.Motor import MotorDriver
from Robot.Device.Odometer import OdometerReader
from Robot.Device.Servo import ServoDriver
from Robot.Utils.Constants import LOW, HIGH

# max length of values read or written by the Gumstix
# (the maximum for this value is 256)
MAX_LENGTH = 8
SPI_State = enum('IDLE', 'TRANSFER')
KLV_State = enum('READ_KEY', 'GET_READ_LENGTH', 'GET_WRITE_LENGTH', 'MASTER_WRITE', 'MASTER_READ', 'MASTER_ADC')

def RobotIO(
    clk25,
    sspi_clk, sspi_cs, sspi_miso, sspi_mosi,
    rc1_cha, rc1_chb,
    rc2_cha, rc2_chb,
    rc3_cha, rc3_chb,
    rc4_cha, rc4_chb,
    mot1_brake, mot1_dir, mot1_pwm,
    mot2_brake, mot2_dir, mot2_pwm,
    mot3_brake, mot3_dir, mot3_pwm,
    mot4_brake, mot4_dir, mot4_pwm,
    mot5_brake, mot5_dir, mot5_pwm,
    mot6_brake, mot6_dir, mot6_pwm,
    mot7_brake, mot7_dir, mot7_pwm,
    mot8_brake, mot8_dir, mot8_pwm,
    adc1_clk, adc1_cs, adc1_miso, adc1_mosi,
    pwm1_ch0, pwm1_ch1, pwm1_ch2, pwm1_ch3, pwm1_ch4, pwm1_ch5, pwm1_ch6, pwm1_ch7,
    ext1_0, ext1_1, ext1_2, ext1_3, ext1_4, ext1_5, ext1_6, ext1_7,
    ext2_0, ext2_1, ext2_2, ext2_3, ext2_4, ext2_5, ext2_6, ext2_7,
    ext3_0, ext3_1, ext3_2, ext3_3, ext3_4, ext3_5, ext3_6, ext3_7,
    ext4_0, ext4_1, ext4_2, ext4_3, ext4_4, ext4_5, ext4_6, ext4_7,
    ext5_0, ext5_1, ext5_2, ext5_3, ext5_4, ext5_5, ext5_6, ext5_7,
    ext6_0, ext6_1, ext6_2, ext6_3, ext6_4, ext6_5, ext6_6, ext6_7,
    ext7_0, ext7_1, ext7_2, ext7_3, ext7_4, ext7_5, ext7_6, ext7_7,
    led_yellow_n, led_green_n, led_red_n,
    optocoupled
    ):
    """

    Main module for robot IO stack

    Instanciates and wires up all necessary modules.

    clk25 -- 25 MHz clock input
    sspi_* -- Gumstix SPI signals (Gumstix is master, FPGA is slave)
    rcX_ch* -- Quadrature encoder X signals (channels A and B)
    motX_* -- pwm, dir and brake signals for DC motor X
    adc1_* -- SPI signals to ADC board 1 (FPGA is master, ADC chip is slave)
    pwm1_* -- PWM signals to PWM board 1 (for servo motors)
    ext1_* -- Extension port 1 signals
    ext2_* -- Extension port 2 signals
    ext3_* -- Extension port 3 signals
    ext4_* -- Extension port 4 signals
    ext5_* -- Extension port 5 signals
    ext6_* -- Extension port 6 signals
    ext7_* -- Extension port 7 signals
    led_*_n -- Active-low LED signal
    optocoupled -- motors and servos drivers account for optocouplers if this is set to True

    """

    # chip-wide active low reset signal
    # brought low for 1 clk25 period when rst_n_consign changes
    rst_n, rst_n_consign, rst_n_consign_prev = Signal(HIGH), Signal(HIGH), Signal(HIGH)
    @always(clk25.posedge)
    def DriveReset():
        if rst_n_consign != rst_n_consign_prev:
            rst_n.next = LOW
            rst_n_consign_prev.next = rst_n_consign
        else:
            rst_n.next = HIGH

    # Green LED should be off by default
    led_green_consign = Signal(LOW)
    @always_comb
    def drive_led_green():
        led_green_n.next = not led_green_consign

    # Yellow LED should be off by default
    led_yellow_consign = Signal(LOW)
    @always_comb
    def drive_led_yellow():
        led_yellow_n.next = not led_yellow_consign

    # Toggle led every second
    Led1_inst = LEDDriver(led_red_n, clk25, rst_n)

    # !Odometers (rc1-4)
    rc1_count = Signal(intbv(0, min = -2**31, max = 2**31))
    rc2_count = Signal(intbv(0, min = -2**31, max = 2**31))
    rc3_count = Signal(intbv(0, min = -2**31, max = 2**31))
    rc4_count = Signal(intbv(0, min = -2**31, max = 2**31))
    Odometer1_inst = OdometerReader(rc1_count, rc1_cha, rc1_chb, clk25, rst_n)
    Odometer2_inst = OdometerReader(rc2_count, rc2_cha, rc2_chb, clk25, rst_n)
    Odometer3_inst = OdometerReader(rc3_count, rc3_cha, rc3_chb, clk25, rst_n)
    Odometer4_inst = OdometerReader(rc4_count, rc4_cha, rc4_chb, clk25, rst_n)

    # !Motors (mot1-8)
    motor1_speed = Signal(intbv(0, min = -2**10, max = 2**10))
    motor2_speed = Signal(intbv(0, min = -2**10, max = 2**10))
    motor3_speed = Signal(intbv(0, min = -2**10, max = 2**10))
    motor4_speed = Signal(intbv(0, min = -2**10, max = 2**10))
    motor5_speed = Signal(intbv(0, min = -2**10, max = 2**10))
    motor6_speed = Signal(intbv(0, min = -2**10, max = 2**10))
    motor7_speed = Signal(intbv(0, min = -2**10, max = 2**10))
    motor8_speed = Signal(intbv(0, min = -2**10, max = 2**10))
    Motor1_inst = MotorDriver(mot1_pwm, mot1_dir, mot1_brake, clk25, motor1_speed, rst_n, optocoupled)
    Motor2_inst = MotorDriver(mot2_pwm, mot2_dir, mot2_brake, clk25, motor2_speed, rst_n, optocoupled)
    Motor3_inst = MotorDriver(mot3_pwm, mot3_dir, mot3_brake, clk25, motor3_speed, rst_n, optocoupled)
    Motor4_inst = MotorDriver(mot4_pwm, mot4_dir, mot4_brake, clk25, motor4_speed, rst_n, optocoupled)
    Motor5_inst = MotorDriver(mot5_pwm, mot5_dir, mot5_brake, clk25, motor5_speed, rst_n, optocoupled)
    Motor6_inst = MotorDriver(mot6_pwm, mot6_dir, mot6_brake, clk25, motor6_speed, rst_n, optocoupled)
    Motor7_inst = MotorDriver(mot7_pwm, mot7_dir, mot7_brake, clk25, motor7_speed, rst_n, optocoupled)
    Motor8_inst = MotorDriver(mot8_pwm, mot8_dir, mot8_brake, clk25, motor8_speed, rst_n, optocoupled)

    # !Servo motors
    servo1_consign = Signal(intbv(0)[16:])
    servo2_consign = Signal(intbv(0)[16:])
    servo3_consign = Signal(intbv(0)[16:])
    servo4_consign = Signal(intbv(0)[16:])
    servo5_consign = Signal(intbv(0)[16:])
    servo6_consign = Signal(intbv(0)[16:])
    servo7_consign = Signal(intbv(0)[16:])
    servo8_consign = Signal(intbv(0)[16:])
    Servo1_ch0_inst = ServoDriver(pwm1_ch0, clk25, servo1_consign, rst_n, optocoupled)
    Servo1_ch1_inst = ServoDriver(pwm1_ch1, clk25, servo2_consign, rst_n, optocoupled)
    Servo1_ch2_inst = ServoDriver(pwm1_ch2, clk25, servo3_consign, rst_n, optocoupled)
    Servo1_ch3_inst = ServoDriver(pwm1_ch3, clk25, servo4_consign, rst_n, optocoupled)
    Servo1_ch4_inst = ServoDriver(pwm1_ch4, clk25, servo5_consign, rst_n, optocoupled)
    Servo1_ch5_inst = ServoDriver(pwm1_ch5, clk25, servo6_consign, rst_n, optocoupled)
    Servo1_ch6_inst = ServoDriver(pwm1_ch6, clk25, servo7_consign, rst_n, optocoupled)
    Servo1_ch7_inst = ServoDriver(pwm1_ch7, clk25, servo8_consign, rst_n, optocoupled)

    # !EXT ports
    ext1_port = ConcatSignal(ext1_7, ext1_6, ext1_5, ext1_4, ext1_3, ext1_2, ext1_1, ext1_0)
    ext2_port = ConcatSignal(ext2_7, ext2_6, ext2_5, ext2_4, ext2_3, ext2_2, ext2_1, ext2_0)
    ext3_port = ConcatSignal(ext3_7, ext3_6, ext3_5, ext3_4, ext3_3, ext3_2, ext3_1, ext3_0)
    ext4_port = ConcatSignal(ext4_7, ext4_6, ext4_5, ext4_4, ext4_3, ext4_2, ext4_1, ext4_0)
    ext5_port = ConcatSignal(ext5_7, ext5_6, ext5_5, ext5_4, ext5_3, ext5_2, ext5_1, ext5_0)
    ext6_port = ConcatSignal(ext6_7, ext6_6, ext6_5, ext6_4, ext6_3, ext6_2, ext6_1, ext6_0)
    ext7_port = ConcatSignal(ext7_7, ext7_6, ext7_5, ext7_4, ext7_3, ext7_2, ext7_1, ext7_0)

    # Registers for SPI read/write tests
    stored_uint8  = Signal(intbv(0)[8:])
    stored_uint16 = Signal(intbv(0)[16:])
    stored_uint32 = Signal(intbv(0)[32:])
    stored_int8   = Signal(intbv(0, min = -2**7,  max = 2**7))
    stored_int16  = Signal(intbv(0, min = -2**15, max = 2**15))
    stored_int32  = Signal(intbv(0, min = -2**31, max = 2**31))



    # Communication with Microchip MCP3008 8-Channel 10-Bit A/D Converter
    #
    # The slave needs either SPI Mode 0 or 3.
    #
    # The SPI clock generated by our SPI Master (the Gumstix) is forwarded
    # to the MCP3008. It is inverted to use SPI Mode 3.
    #
    # The 17-bit data we send:
    # - start bit (a 1)
    # - single-ended bit (a 1)
    # - 3 bits for the channel (most significant bit first)
    # - 12 padding bits (we send zeros)
    #
    # The 17-bit data we get back
    # - 6 padding bits
    # - a null byte
    # - the 10-bit value
    #
    # Communication with MCP3008 during a KLV exchange
    #
    # The 17-bit exchange starts when the 7th bit of the key is received.
    # If the 7 first bits of the key correspond to one of the channel keys,
    # the start bit is sent. Thus, the remaining 16 bits are aligned with
    # the length byte and the first value byte. Bits 2 to 9 are received
    # during the length byte, and sent as the first value byte. Bits 10 to 17
    # are received during the first value byte, and sent as the second value
    # byte.

    # bit counter (0 to 16, 17 when done)
    adc1_ws = 17
    adc1_cnt = Signal(intbv(adc1_ws, min=0, max=adc1_ws+1))

    # 3-bit channel number
    adc1_channel = Signal(intbv(0)[3:])

    @always_comb
    def ADCClock():
        """

        Drives adc1_clk.

        """
        adc1_clk.next = not sspi_clk

    @instance
    def ADCTX():
        """

        MCP3008 SPI transmission: drives adc1_mosi.

        """
        while True:
            # Propagate on adc1_clk falling edge (mode 3)
            # == sspi_clk rising edge
            yield sspi_clk.posedge
            if adc1_cnt < adc1_ws:
                # Start bit
                if adc1_cnt == 0:
                    adc1_mosi.next = HIGH
                # Single ended / differential bit
                elif adc1_cnt == 1:
                    adc1_mosi.next = HIGH
                # 3-bit channel
                elif adc1_cnt >= 2 and adc1_cnt <= 4:
                    adc1_mosi.next = adc1_channel[4-adc1_cnt]
                # 12-bit padding
                else:
                    adc1_mosi.next = LOW


    # Communication with SPI Master.
    #
    # The master sends a stream of KLV (Key byte, Length byte, Value bytes)
    # encoded commands. Keys upto 0x7F are read commands. Keys from 0x80 are
    # write commands.
    #
    # SPI mode 1 (cpol = 0, cpha = 1) is used:
    # - the base value of the clock is LOW
    # - data is captured on the clock's falling edge and data is propagated
    #   on a rising edge.
    #
    # To use mode 3 (cpol = 1, cpha = 1), switch the edges of sspi_clk in
    # TX() and RX().

    # word size: 8 bits
    ws = 8

    # next word to send
    txdata = Signal(intbv(0)[ws:])

    # number of bits sent in txdata (sort of)
    spi_cnt = Signal(intbv(0, min=0, max=ws))

    @instance
    def TX():
        """

        Low level SPI transmission: drives sspi_miso.

        Reacts on rising edges of the SPI clock to send txdata bit per bit.
        Drives spi_cnt for use by RX() to detect end of word.

        """

        # shift register with bits to send to master
        txsreg = intbv(0)[ws:]

        # state in the SPI "protocol"
        state = SPI_State.IDLE

        while True:
            # Propagate on rising edge (mode 1)
            yield sspi_clk.posedge
            if sspi_cs == LOW:
                if state == SPI_State.IDLE:
                    txsreg[:] = txdata
                    state = SPI_State.TRANSFER
                    spi_cnt.next = 0
                elif state == SPI_State.TRANSFER:
                    txsreg[ws:1] = txsreg[ws-1:]
                    # ws-2 because 1st bit was sent without cnt++
                    if spi_cnt == ws-2:
                        state = SPI_State.IDLE
                    spi_cnt.next = spi_cnt + 1
                sspi_miso.next = txsreg[ws-1]
            else:
                state = SPI_State.IDLE

    @instance
    def RX():
        """

        Low level SPI reception and higher level word handling.

        Reacts on falling edges of the SPI clock to store the received bits.

        When a word is received, RX() interprets it as the key, length, or one
        of the value bytes, depending on the current state in the KLV decoding.

        RX() drives txdata to send the value bytes one by one when the master
        is reading, or else to send null bytes.

        """

        # shift register with bits received from MCP3008
        adc1_rxsreg = intbv(0)[ws:]

        # shift register with bits received from master
        rxsreg = intbv(0)[ws:]

        # address sent by the master
        key = intbv(0)[ws:]

        # length of the value sent or expected by the master
        length = intbv(0)[ws:]

        # big intbv whose lower bytes are sent to the master when it is reading
        value_for_master = intbv(0)[MAX_LENGTH*ws:]

        # big intbv whose lower bytes are set by the master when it is writing
        value_from_master = intbv(0)[MAX_LENGTH*ws:]

        # index of the currently read or written value byte
        index = MAX_LENGTH*ws

        # state in the KLV protocol
        state = KLV_State.READ_KEY

        while True:
            # Capture on falling edge (mode 1)
            yield sspi_clk.negedge

            # ADC special: handle ADC RX
            if adc1_cnt < adc1_ws:
                if adc1_cnt >= 7:
                    # shift in new bit
                    adc1_rxsreg[ws:] = concat(adc1_rxsreg[ws-1:], adc1_miso)
                else:
                    # ignore all but bits 7-16
                    adc1_rxsreg[ws:] = concat(adc1_rxsreg[ws-1:], LOW)
                if adc1_cnt + 1 == adc1_ws:
                    adc1_cs.next = HIGH
                adc1_cnt.next = adc1_cnt + 1

            if sspi_cs == LOW:
                # shift in new bit
                rxsreg[ws:] = concat(rxsreg[ws-1:], sspi_mosi)

                # ADC special: detect ADC keys early to send start bit
                if spi_cnt == ws-2:
                    if state == KLV_State.READ_KEY:
                        key[:] = concat(rxsreg[ws-1:], LOW)
                        if key >= 0x50 and key <= 0x57:
                            adc1_cs.next = LOW
                            adc1_cnt.next = 0

                # Read a whole word
                if spi_cnt == ws-1:
                    txdata.next = 0

                    # handle the key sent by the master
                    if state == KLV_State.READ_KEY:
                        # read key sent by master
                        key[:] = rxsreg

                        # ADC Special: set channel, go to special state
                        if key >= 0x50 and key <= 0x57:
                            adc1_channel.next = key - 0x50
                            length[:] = 3 # length + 2 value bytes
                            index = ws*(length-1)
                            state = KLV_State.MASTER_ADC
                        # Master reads
                        elif key[ws-1] == 0:
                            state = KLV_State.GET_READ_LENGTH
                        # Master writes
                        else:
                            state = KLV_State.GET_WRITE_LENGTH

                    # handle the length of the value sent by the master
                    elif state == KLV_State.GET_WRITE_LENGTH:
                        # read length sent by master
                        length[:] = rxsreg
                        value_from_master[:] = 0

                        if length > 0: # write some bytes
                            index = ws*(length-1)
                            state = KLV_State.MASTER_WRITE
                        else: # write 0 byte: done
                            state = KLV_State.READ_KEY

                    # handle the length of the value expected by the master
                    elif state == KLV_State.GET_READ_LENGTH:
                        # read length sent by master
                        length[:] = rxsreg
                        value_for_master[:] = 0

                        if length > 0: # read some bytes
                            index = ws*(length-1)
                            state = KLV_State.MASTER_READ

                            # Odometers: use bit slicing to convert signed to unsigned
                            if key == 0x11:
                                value_for_master[len(rc1_count):] = rc1_count[len(rc1_count):]
                            elif key == 0x12:
                                value_for_master[len(rc2_count):] = rc2_count[len(rc2_count):]
                            elif key == 0x13:
                                value_for_master[len(rc3_count):] = rc3_count[len(rc3_count):]
                            elif key == 0x14:
                                value_for_master[len(rc4_count):] = rc4_count[len(rc4_count):]

                            # EXT ports
                            elif key == 0x31:
                                value_for_master[len(ext1_port):] = ext1_port
                            elif key == 0x32:
                                value_for_master[len(ext2_port):] = ext2_port
                            elif key == 0x33:
                                value_for_master[len(ext3_port):] = ext3_port
                            elif key == 0x34:
                                value_for_master[len(ext4_port):] = ext4_port
                            elif key == 0x35:
                                value_for_master[len(ext5_port):] = ext5_port
                            elif key == 0x36:
                                value_for_master[len(ext6_port):] = ext6_port
                            elif key == 0x37:
                                value_for_master[len(ext7_port):] = ext7_port

                            # Fixed value for testing
                            elif key == 0x42:
                                value_for_master[32:] = 0xDEADC0DE

                            # Read stored values for testing
                            elif key == 0x71:
                                value_for_master[len(stored_uint8):] = stored_uint8
                            elif key == 0x72:
                                value_for_master[len(stored_uint16):] = stored_uint16
                            elif key == 0x73:
                                value_for_master[len(stored_uint32):] = stored_uint32
                            # use bit slicing to convert signed to unsigned
                            elif key == 0x74:
                                value_for_master[len(stored_int8):] = stored_int8[len(stored_int8):]
                            elif key == 0x75:
                                value_for_master[len(stored_int16):] = stored_int16[len(stored_int16):]
                            elif key == 0x76:
                                value_for_master[len(stored_int32):] = stored_int32[len(stored_int32):]
                            else:
                                # Dummy value sent when key is unknown.
                                # The value is fixed. The master read 'length'
                                # bytes from it.
                                value_for_master[:] = 0xDEADBEEFBAADF00D

                            # send first byte immediately
                            txdata.next = value_for_master[(index + ws):index]

                        else: # read 0 byte: done
                            state = KLV_State.READ_KEY

                    # handle the value bytes sent by the master
                    elif state == KLV_State.MASTER_WRITE:
                        # read value byte sent by master and store it
                        value_from_master[(index + ws):index] = rxsreg

                        if index >= ws:
                            # Get next byte
                            index -= ws
                        else:
                            # Got everything
                            state = KLV_State.READ_KEY

                            # Reset
                            if key == 0x81:
                                rst_n_consign.next = not rst_n_consign

                            # Green LED
                            elif key == 0x82:
                                led_green_consign.next = value_from_master[0]

                            # Yellow LED
                            elif key == 0x83:
                                led_yellow_consign.next = value_from_master[0]

                            # Motors
                            elif key == 0x91:
                                motor1_speed.next = value_from_master[len(motor1_speed):].signed()
                            elif key == 0x92:
                                motor2_speed.next = value_from_master[len(motor2_speed):].signed()
                            elif key == 0x93:
                                motor3_speed.next = value_from_master[len(motor3_speed):].signed()
                            elif key == 0x94:
                                motor4_speed.next = value_from_master[len(motor4_speed):].signed()
                            elif key == 0x95:
                                motor5_speed.next = value_from_master[len(motor5_speed):].signed()
                            elif key == 0x96:
                                motor6_speed.next = value_from_master[len(motor6_speed):].signed()
                            elif key == 0x97:
                                motor7_speed.next = value_from_master[len(motor7_speed):].signed()
                            elif key == 0x98:
                                motor8_speed.next = value_from_master[len(motor8_speed):].signed()

                            # Servos
                            elif key == 0xA1:
                                servo1_consign.next = value_from_master[len(servo1_consign):]
                            elif key == 0xA2:
                                servo2_consign.next = value_from_master[len(servo2_consign):]
                            elif key == 0xA3:
                                servo3_consign.next = value_from_master[len(servo3_consign):]
                            elif key == 0xA4:
                                servo4_consign.next = value_from_master[len(servo4_consign):]
                            elif key == 0xA5:
                                servo5_consign.next = value_from_master[len(servo5_consign):]
                            elif key == 0xA6:
                                servo6_consign.next = value_from_master[len(servo6_consign):]
                            elif key == 0xA7:
                                servo7_consign.next = value_from_master[len(servo7_consign):]
                            elif key == 0xA8:
                                servo8_consign.next = value_from_master[len(servo8_consign):]

                            # Store values for testing
                            elif key == 0xF1:
                                stored_uint8.next = value_from_master[len(stored_uint8):]
                            elif key == 0xF2:
                                stored_uint16.next = value_from_master[len(stored_uint16):]
                            elif key == 0xF3:
                                stored_uint32.next = value_from_master[len(stored_uint32):]
                            elif key == 0xF4:
                                stored_int8.next = value_from_master[len(stored_int8):].signed()
                            elif key == 0xF5:
                                stored_int16.next = value_from_master[len(stored_int16):].signed()
                            elif key == 0xF6:
                                stored_int32.next = value_from_master[len(stored_int32):].signed()

                            # Convert to case block
                            else:
                                pass

                    # decrement index when each value byte expected by the master has been sent
                    elif state == KLV_State.MASTER_READ:
                        if index >= ws:
                            # Send next byte
                            index -= ws
                            txdata.next = value_for_master[(index + ws):index]
                        else:
                            # Sent everything
                            state = KLV_State.READ_KEY

                    # send adc bytes
                    elif state == KLV_State.MASTER_ADC:
                        if index >= ws:
                            # Send next byte
                            index -= ws
                            txdata.next = adc1_rxsreg
                        else:
                            # Sent everything
                            state = KLV_State.READ_KEY

            # Deselected
            else:
                state = KLV_State.READ_KEY
                txdata.next = 0

    return instances()
