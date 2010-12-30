from myhdl import ConcatSignal, Signal, intbv, always, always_comb, instances
from Robot.ControlSystem.Filter.PID import PIDFilter
from Robot.ControlSystem.Filter.Ramp import RampFilter
from Robot.ControlSystem.Manager import ControlSystemManager
from Robot.Device.Motor import MotorDriver
from Robot.Device.Odometer import OdometerReader
from Robot.Device.PolarMotors import PolarMotors
from Robot.Device.PolarOdometers import PolarOdometers
from Robot.Device.Servo import ServoDriver
from Robot.SPI.Protocol.KLVSlave import GumstixSPI
from Robot.Utils.Constants import LOW, HIGH

# max length of values read or written by the Gumstix
# (the maximum for this value is 256)
MAX_LENGTH = 8

MIN_ODOMETER_SPEED = -2**30
MAX_ODOMETER_SPEED = +2**30

MIN_MOTOR_SPEED = -2**10
MAX_MOTOR_SPEED = +2**10

MIN_ANGLE_SPEED = MIN_ODOMETER_SPEED
MAX_ANGLE_SPEED = MAX_ODOMETER_SPEED
MAX_ANGLE_ACCELERATION = 2**15
MAX_ANGLE_DECELERATION = 2**15

MIN_DISTANCE_SPEED = MIN_ODOMETER_SPEED
MAX_DISTANCE_SPEED = MAX_ODOMETER_SPEED
MAX_DISTANCE_ACCELERATION = 2**15
MAX_DISTANCE_DECELERATION = 2**15

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
    """ Main module for robot IO stack

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

    # communication with GumstixSPI
    key = Signal(intbv(0)[8:])
    length = Signal(intbv(0)[8:])
    master_read_n = Signal(HIGH)
    value_for_master = Signal(intbv(0)[MAX_LENGTH*8:])
    master_write_n = Signal(HIGH)
    value_from_master = Signal(intbv(0)[MAX_LENGTH*8:])

    # chip-wide active low reset signal
    rst_n = Signal(HIGH)

    # Gumstix SPI
    GumstixSPI_inst = GumstixSPI(sspi_miso, sspi_mosi, sspi_clk, sspi_cs,
                                 key, length, master_read_n, value_for_master, master_write_n, value_from_master,
                                 clk25, rst_n)

    # !Left/Right odometers (rc3 & rc4)
    left_odometer_count  = Signal(intbv(0, min = -2**15, max = 2**15))
    left_odometer_speed  = Signal(intbv(0, min = MIN_ODOMETER_SPEED, max = MAX_ODOMETER_SPEED))
    right_odometer_count = Signal(intbv(0, min = -2**15, max = 2**15))
    right_odometer_speed = Signal(intbv(0, min = MIN_ODOMETER_SPEED, max = MAX_ODOMETER_SPEED))
    LeftOdometer_inst    = OdometerReader(left_odometer_count, left_odometer_speed,
                                          rc3_cha, rc3_chb, clk25, rst_n)
    RightOdometer_inst   = OdometerReader(right_odometer_count, right_odometer_speed,
                                          rc4_cha, rc4_chb, clk25, rst_n)

    # !Polar odometers
    angle_odometer_count    = Signal(intbv(0, min = -2**15, max = 2**15))
    angle_odometer_speed    = Signal(intbv(0, min = MIN_ANGLE_SPEED, max = MAX_ANGLE_SPEED))
    distance_odometer_count = Signal(intbv(0, min = -2**15, max = 2**15))
    distance_odometer_speed = Signal(intbv(0, min = MIN_DISTANCE_SPEED, max = MAX_DISTANCE_SPEED))
    PolarOdometers_inst     = PolarOdometers(left_odometer_count, left_odometer_speed,
                                             right_odometer_count, right_odometer_speed,
                                             angle_odometer_count, angle_odometer_speed,
                                             distance_odometer_count, distance_odometer_speed)

    # !Other odometers (rc1 & rc2)
    rc1_count = Signal(intbv(0, min = -2**15, max = 2**15))
    rc1_speed = Signal(intbv(0, min = -2**31, max = 2**31))
    rc2_count = Signal(intbv(0, min = -2**15, max = 2**15))
    rc2_speed = Signal(intbv(0, min = -2**31, max = 2**31))
    Odometer1_inst = OdometerReader(rc1_count, rc1_speed, rc1_cha, rc1_chb, clk25, rst_n)
    Odometer2_inst = OdometerReader(rc2_count, rc2_speed, rc2_cha, rc2_chb, clk25, rst_n)

    # !Left/Right motors (mot7 & mot8)
    left_motor_speed  = Signal(intbv(0, min = MIN_MOTOR_SPEED, max = MAX_MOTOR_SPEED))
    right_motor_speed = Signal(intbv(0, min = MIN_MOTOR_SPEED, max = MAX_MOTOR_SPEED))
    LeftMotor_inst    = MotorDriver(mot7_pwm, mot7_dir, mot7_brake,
                                    clk25, left_motor_speed, rst_n, optocoupled)
    RightMotor_inst   = MotorDriver(mot8_pwm, mot8_dir, mot8_brake,
                                    clk25, right_motor_speed, rst_n, optocoupled)

    # !Polar motors
    angle_motor_speed    = Signal(intbv(0, min = -2**9, max = 2**9)) # FIXME: 10-bit signed int
    distance_motor_speed = Signal(intbv(0, min = -2**9, max = 2**9)) # FIXME: 10-bit signed int
    PolarMotors_inst     = PolarMotors(angle_motor_speed, distance_motor_speed,
                                       left_motor_speed, right_motor_speed)

    # !Other motors (mot1-6)
    motor1_speed = Signal(intbv(0, min = MIN_MOTOR_SPEED, max = MAX_MOTOR_SPEED))
    motor2_speed = Signal(intbv(0, min = MIN_MOTOR_SPEED, max = MAX_MOTOR_SPEED))
    motor3_speed = Signal(intbv(0, min = MIN_MOTOR_SPEED, max = MAX_MOTOR_SPEED))
    motor4_speed = Signal(intbv(0, min = MIN_MOTOR_SPEED, max = MAX_MOTOR_SPEED))
    motor5_speed = Signal(intbv(0, min = MIN_MOTOR_SPEED, max = MAX_MOTOR_SPEED))
    motor6_speed = Signal(intbv(0, min = MIN_MOTOR_SPEED, max = MAX_MOTOR_SPEED))
    Motor1_inst = MotorDriver(mot1_pwm, mot1_dir, mot1_brake, clk25, motor1_speed, rst_n, optocoupled)
    Motor2_inst = MotorDriver(mot2_pwm, mot2_dir, mot2_brake, clk25, motor2_speed, rst_n, optocoupled)
    Motor3_inst = MotorDriver(mot3_pwm, mot3_dir, mot3_brake, clk25, motor3_speed, rst_n, optocoupled)
    Motor4_inst = MotorDriver(mot4_pwm, mot4_dir, mot4_brake, clk25, motor4_speed, rst_n, optocoupled)
    Motor5_inst = MotorDriver(mot5_pwm, mot5_dir, mot5_brake, clk25, motor5_speed, rst_n, optocoupled)
    Motor6_inst = MotorDriver(mot6_pwm, mot6_dir, mot6_brake, clk25, motor6_speed, rst_n, optocoupled)

    # TODO: ADC SPI

    # Servo motors
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

    # Angle control system

    ## Ramp consign filter
    angle_consign_filter_input  = Signal(intbv(0, min = MIN_ANGLE_SPEED, max = MAX_ANGLE_SPEED))
    angle_consign_filter_output = Signal(intbv(0, min = MIN_ANGLE_SPEED, max = MAX_ANGLE_SPEED))
    angle_max_acceleration      = Signal(intbv(0, min = 0, max = MAX_ANGLE_ACCELERATION))
    angle_max_deceleration      = Signal(intbv(0, min = 0, max = MAX_ANGLE_DECELERATION))
    AngleRamp = RampFilter(angle_consign_filter_input,
                           angle_consign_filter_output,
                           angle_max_acceleration,
                           angle_max_deceleration)

    ## Fake filter on the feedback
    angle_feedback_filter_input  = Signal(intbv(0, min = angle_odometer_speed.min,
                                                   max = angle_odometer_speed.max))
    angle_feedback_filter_output = Signal(intbv(0, min = angle_odometer_speed.min,
                                                   max = angle_odometer_speed.max))
    @always_comb
    def fake_angle_feedback_filter():
        angle_feedback_filter_output.next = angle_feedback_filter_input

    ## PID correct filter
    angle_correct_filter_input  = Signal(intbv(0, min = angle_consign_filter_output.min - angle_feedback_filter_output.max,
                                                  max = angle_consign_filter_output.max - angle_feedback_filter_output.min))
    angle_correct_filter_output = Signal(intbv(0, min = angle_motor_speed.min,
                                                  max = angle_motor_speed.max))
    angle_correct_filter_gain_P    = Signal(intbv(0)[8:]) # FIXME: bit width
    angle_correct_filter_gain_I    = Signal(intbv(0)[8:]) # FIXME: bit width
    angle_correct_filter_gain_D    = Signal(intbv(0)[8:]) # FIXME: bit width
    angle_correct_filter_out_shift = Signal(intbv(0)[8:]) # FIXME: bit width
    angle_correct_filter_max_I     = intbv(2**31) # FIXME: value
    angle_correct_filter_max_D     = intbv(2**31) # FIXME: value
    AnglePID = PIDFilter(angle_correct_filter_input,
                         angle_correct_filter_output,
                         angle_correct_filter_gain_P,
                         angle_correct_filter_gain_I,
                         angle_correct_filter_gain_D,
                         angle_correct_filter_out_shift,
                         angle_correct_filter_max_I,
                         angle_correct_filter_max_D,
                         rst_n)

    ## Control system manager
    angle_consign = Signal(intbv(0, min = MIN_ODOMETER_SPEED, max = MAX_ODOMETER_SPEED))
    AngleManager = ControlSystemManager(angle_consign_filter_input,
                                        angle_consign_filter_output,
                                        angle_correct_filter_input,
                                        angle_correct_filter_output,
                                        angle_feedback_filter_input,
                                        angle_feedback_filter_output,
                                        angle_motor_speed,
                                        angle_odometer_speed,
                                        angle_consign)

    # EXT ports
    ext1_port = ConcatSignal(ext1_7, ext1_6, ext1_5, ext1_4, ext1_3, ext1_2, ext1_1, ext1_0)
    ext2_port = ConcatSignal(ext2_7, ext2_6, ext2_5, ext2_4, ext2_3, ext2_2, ext2_1, ext2_0)
    ext3_port = ConcatSignal(ext3_7, ext3_6, ext3_5, ext3_4, ext3_3, ext3_2, ext3_1, ext3_0)
    ext4_port = ConcatSignal(ext4_7, ext4_6, ext4_5, ext4_4, ext4_3, ext4_2, ext4_1, ext4_0)
    ext5_port = ConcatSignal(ext5_7, ext5_6, ext5_5, ext5_4, ext5_3, ext5_2, ext5_1, ext5_0)
    ext6_port = ConcatSignal(ext6_7, ext6_6, ext6_5, ext6_4, ext6_3, ext6_2, ext6_1, ext6_0)
    ext7_port = ConcatSignal(ext7_7, ext7_6, ext7_5, ext7_4, ext7_3, ext7_2, ext7_1, ext7_0)

    # Master reads: 0x01 <= key <= 0x7F
    @always(clk25.posedge, rst_n.negedge)
    def GumstixRead():
        if rst_n == LOW:
            value_for_master.next[:] = 0
        else:
            if master_read_n == LOW:
                value_for_master.next[:] = 0
                if key == 0x11:
                    value_for_master.next = rc1_count[len(rc1_count):]
                elif key == 0x12:
                    value_for_master.next = rc2_count[len(rc2_count):]
                elif key == 0x13:
                    value_for_master.next = left_odometer_count[len(left_odometer_count):]
                elif key == 0x14:
                    value_for_master.next = right_odometer_count[len(right_odometer_count):]
                elif key == 0x15:
                    value_for_master.next = angle_odometer_count[len(angle_odometer_count):]
                elif key == 0x16:
                    value_for_master.next = distance_odometer_count[len(distance_odometer_count):]
                elif key == 0x21:
                    value_for_master.next = rc1_speed[len(rc1_speed):]
                elif key == 0x22:
                    value_for_master.next = rc2_speed[len(rc2_speed):]
                elif key == 0x23:
                    value_for_master.next = left_odometer_speed[len(left_odometer_speed):]
                elif key == 0x24:
                    value_for_master.next = right_odometer_speed[len(right_odometer_speed):]
                elif key == 0x25:
                    value_for_master.next = angle_odometer_speed[len(angle_odometer_speed):]
                elif key == 0x26:
                    value_for_master.next = distance_odometer_speed[len(distance_odometer_speed):]
                elif key == 0x31:
                    value_for_master.next = ext1_port
                elif key == 0x32:
                    value_for_master.next = ext2_port
                elif key == 0x33:
                    value_for_master.next = ext3_port
                elif key == 0x34:
                    value_for_master.next = ext4_port
                elif key == 0x35:
                    value_for_master.next = ext5_port
                elif key == 0x36:
                    value_for_master.next = ext6_port
                elif key == 0x37:
                    value_for_master.next = ext7_port
                else:
                    # Dummy value sent when key is unknown.
                    # The value is fixed. The master read 'length'
                    # bytes from it.
                    value_for_master.next[64:] = 0xDEADBEEFBAADF00D

    # Master writes: 0x81 <= key <= 0xFF
    # Not sensitive to rst_n as it is driven therein.
    @always(clk25.posedge)
    def GumstixWrite():
        rst_n.next = HIGH

        if master_write_n == LOW:
            # Reset
            if key == 0x81:
                rst_n.next = LOW

            # Yellow LED
            elif key == 0x82:
                led_yellow_n.next = not value_from_master[0]

            # Green LED
            elif key == 0x83:
                led_green_n.next = not value_from_master[0]

            # Red LED
            elif key == 0x84:
                led_red_n.next = not value_from_master[0]

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

            # Angle control system
            elif key == 0xB1:
                angle_consign.next = value_from_master[len(angle_consign):].signed()
            elif key == 0xB2:
                angle_max_acceleration.next = value_from_master[len(angle_max_deceleration):]
            elif key == 0xB3:
                angle_max_deceleration.next = value_from_master[len(angle_max_deceleration):]
            elif key == 0xB4:
                angle_correct_filter_gain_P.next = value_from_master[len(angle_correct_filter_gain_P):]
            elif key == 0xB5:
                angle_correct_filter_gain_I.next = value_from_master[len(angle_correct_filter_gain_I):]
            elif key == 0xB6:
                angle_correct_filter_gain_D.next = value_from_master[len(angle_correct_filter_gain_D):]
            elif key == 0xB7:
                angle_correct_filter_out_shift.next = value_from_master[len(angle_correct_filter_out_shift):]

            # Complete if-elif-else to have it converted to a case block
            else:
                pass

    return instances()
