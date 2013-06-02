from myhdl import ConcatSignal, Signal, always, always_comb, concat, enum, instance, instances, intbv
from Robot.Device.LED import LEDDriver
from Robot.Device.MCP3008 import MCP3008Driver
from Robot.Device.Motor import MotorDriver
from Robot.Device.Odometer import OdometerReader
from Robot.Device.Servo import ServoDriver
from Robot.Utils.Constants import LOW, HIGH

# max length of values read or written by the Gumstix
# (the maximum for this value is 256)
MAX_LENGTH = 8

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
    rc1_speed = Signal(intbv(0, min = -2**31, max = 2**31))
    rc2_count = Signal(intbv(0, min = -2**31, max = 2**31))
    rc2_speed = Signal(intbv(0, min = -2**31, max = 2**31))
    rc3_count = Signal(intbv(0, min = -2**31, max = 2**31))
    rc3_speed = Signal(intbv(0, min = -2**31, max = 2**31))
    rc4_count = Signal(intbv(0, min = -2**31, max = 2**31))
    rc4_speed = Signal(intbv(0, min = -2**31, max = 2**31))
    Odometer1_inst = OdometerReader(rc1_count, rc1_speed, rc1_cha, rc1_chb, clk25, rst_n)
    Odometer2_inst = OdometerReader(rc2_count, rc2_speed, rc2_cha, rc2_chb, clk25, rst_n)
    Odometer3_inst = OdometerReader(rc3_count, rc3_speed, rc3_cha, rc3_chb, clk25, rst_n)
    Odometer4_inst = OdometerReader(rc4_count, rc4_speed, rc4_cha, rc4_chb, clk25, rst_n)

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

    # !MCP3008 A/D Converter
    adc1_ch1 = Signal(intbv(0)[10:])
    adc1_ch2 = Signal(intbv(0)[10:])
    adc1_ch3 = Signal(intbv(0)[10:])
    adc1_ch4 = Signal(intbv(0)[10:])
    adc1_ch5 = Signal(intbv(0)[10:])
    adc1_ch6 = Signal(intbv(0)[10:])
    adc1_ch7 = Signal(intbv(0)[10:])
    adc1_ch8 = Signal(intbv(0)[10:])
    MCP3008Driver_inst = MCP3008Driver(adc1_ch1, adc1_ch2, adc1_ch3, adc1_ch4, adc1_ch5, adc1_ch6, adc1_ch7, adc1_ch8,
                                       adc1_clk, adc1_cs, adc1_miso, adc1_mosi, clk25, rst_n)

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

    # communication with SPI Master

    spi_State = enum('IDLE', 'TRANSFER')
    spi_state = Signal(spi_State.IDLE)
    spi_word_size = 8
    spi_bit_cnt = Signal(intbv(0, min=0, max=spi_word_size))

    protocol_State = enum('READ_KEY', 'GET_READ_LENGTH', 'GET_WRITE_LENGTH', 'MASTER_WRITE', 'MASTER_READ')
    protocol_state = Signal(protocol_State.READ_KEY)

    key = Signal(intbv(0)[8:])
    #length = Signal(intbv(0)[8:])
    txdata = Signal(intbv(0)[8:])

    @instance
    def RX():
        """ Capture on falling edge (mode 1) """
        rxdata = intbv(0)[spi_word_size:]

        value_for_master = intbv(0)[MAX_LENGTH*8:]
        value_from_master = intbv(0)[MAX_LENGTH*8:]

        # Index of the currently read or written value byte
        index = len(value_for_master)

        while True:
            yield sspi_clk.negedge
            if sspi_cs == LOW:
                rxdata[spi_word_size:] = concat(rxdata[spi_word_size-1:], sspi_mosi)

                # Read a whole word
                if spi_bit_cnt == spi_word_size-1:
                    txdata.next = 0

                    # handle the key sent by the master
                    if protocol_state == protocol_State.READ_KEY:
                        # read key sent by master
                        key.next = rxdata

                        # need to read the length now
                        # does the master want to read or write?
                        if rxdata[7] == 0: # master read
                            protocol_state.next = protocol_State.GET_READ_LENGTH
                        else: # master write
                            protocol_state.next = protocol_State.GET_WRITE_LENGTH

                    # handle the length of the value sent by the master
                    elif protocol_state == protocol_State.GET_WRITE_LENGTH:
                        # read length sent by master
                        #length.next = rxdata
                        value_from_master[:] = 0

                        if rxdata > 0: # write some bytes
                            index = 8*(rxdata-1)
                            protocol_state.next = protocol_State.MASTER_WRITE
                        else: # write 0 byte: done
                            protocol_state.next = protocol_State.READ_KEY

                    # handle the length of the value expected by the master
                    elif protocol_state == protocol_State.GET_READ_LENGTH:
                        # read length sent by master
                        #length.next = rxdata
                        value_for_master[:] = 0

                        if rxdata > 0: # read some bytes
                            index = 8*(rxdata-1)
                            protocol_state.next = protocol_State.MASTER_READ

                            # Odometers: use bit slicing to convert signed to unsigned
                            if key == 0x11:
                                value_for_master[len(rc1_count):] = rc1_count[len(rc1_count):]
                            elif key == 0x12:
                                value_for_master[len(rc2_count):] = rc2_count[len(rc2_count):]
                            elif key == 0x13:
                                value_for_master[len(rc3_count):] = rc3_count[len(rc3_count):]
                            elif key == 0x14:
                                value_for_master[len(rc4_count):] = rc4_count[len(rc4_count):]
                            elif key == 0x21:
                                value_for_master[len(rc1_speed):] = rc1_speed[len(rc1_speed):]
                            elif key == 0x22:
                                value_for_master[len(rc2_speed):] = rc2_speed[len(rc2_speed):]
                            elif key == 0x23:
                                value_for_master[len(rc3_speed):] = rc3_speed[len(rc3_speed):]
                            elif key == 0x24:
                                value_for_master[len(rc4_speed):] = rc4_speed[len(rc4_speed):]

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

                            # ADC ports
                            elif key == 0x51:
                                value_for_master[len(adc1_ch1):] = adc1_ch1
                            elif key == 0x52:
                                value_for_master[len(adc1_ch2):] = adc1_ch2
                            elif key == 0x53:
                                value_for_master[len(adc1_ch3):] = adc1_ch3
                            elif key == 0x54:
                                value_for_master[len(adc1_ch4):] = adc1_ch4
                            elif key == 0x55:
                                value_for_master[len(adc1_ch5):] = adc1_ch5
                            elif key == 0x56:
                                value_for_master[len(adc1_ch6):] = adc1_ch6
                            elif key == 0x57:
                                value_for_master[len(adc1_ch7):] = adc1_ch7
                            elif key == 0x58:
                                value_for_master[len(adc1_ch8):] = adc1_ch8

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

                            txdata.next = value_for_master[(index + 8):index]

                        else: # read 0 byte: done
                            protocol_state.next = protocol_State.READ_KEY

                    # handle the value bytes sent by the master
                    elif protocol_state == protocol_State.MASTER_WRITE:
                        # read value byte sent by master and store it
                        value_from_master[(index + 8):index] = rxdata

                        if index >= 8:
                            # Get next byte
                            index -= 8
                        else:
                            # Got everything
                            protocol_state.next = protocol_State.READ_KEY

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
                    elif protocol_state == protocol_State.MASTER_READ:
                        if index >= 8:
                            # Send next byte
                            index -= 8
                            txdata.next = value_for_master[(index + 8):index]
                        else:
                            # Sent everything
                            protocol_state.next = protocol_State.READ_KEY

    @instance
    def TX():
        """ Propagate on rising edge (mode 1) """
        sreg = intbv(0)[spi_word_size:]
        while True:
            yield sspi_clk.posedge
            if sspi_cs == LOW:
                if spi_state == spi_State.IDLE:
                    sreg[:] = txdata
                    spi_state.next = spi_State.TRANSFER
                    spi_bit_cnt.next = 0
                elif spi_state == spi_State.TRANSFER:
                    sreg[spi_word_size:1] = sreg[spi_word_size-1:]
                    if spi_bit_cnt == spi_word_size-2:
                        spi_state.next = spi_State.IDLE
                    spi_bit_cnt.next = spi_bit_cnt + 1
                sspi_miso.next = sreg[spi_word_size-1]
            else:
                spi_state.next = spi_State.IDLE

    return instances()
