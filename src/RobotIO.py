from myhdl import Signal, intbv, always, always_comb, instances
from OdometerReader import OdometerReader
from MotorDriver import MotorDriver
from ServoDriver import ServoDriver
from SPISlave import SPISlave

LOW, HIGH = bool(0), bool(1)

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

    """
    pass

    # 16-bit value sent by the Gumstix (speed consign, position consign...)
    # and signal toggling when new gs_rxdata is available.
    gs_rxdata = Signal(intbv(0)[16:])
    gs_rxrdy = Signal(bool(0))

    # 16-bit value to be sent to the Gumstix (odometer count, adc value...)
    # and signal toggling when new gs_txdata can be accepted.
    gs_txdata = Signal(intbv(0)[16:])
    gs_txrdy = Signal(bool(0))

    # chip-wide active low reset signal
    rst_n = Signal(HIGH)

    # Gumstix SPI
    GumstixSPI = SPISlave(sspi_miso, sspi_mosi, sspi_clk, sspi_cs, gs_txdata, gs_txrdy, gs_rxdata, gs_rxrdy, rst_n, 16);

    # Odometers
    rc1_count = Signal(intbv(0)[16:])
    rc2_count = Signal(intbv(0)[16:])
    rc3_count = Signal(intbv(0)[16:])
    rc4_count = Signal(intbv(0)[16:])
    Odometer1_inst = OdometerReader(rc1_count, rc1_cha, rc1_chb, clk25, rst_n)
    Odometer2_inst = OdometerReader(rc2_count, rc2_cha, rc2_chb, clk25, rst_n)
    Odometer3_inst = OdometerReader(rc3_count, rc3_cha, rc3_chb, clk25, rst_n)
    Odometer4_inst = OdometerReader(rc4_count, rc4_cha, rc4_chb, clk25, rst_n)

    # DC Motors
    # FIXME: lines should be inverted because of opto-isolators
    consign_motor_1 = Signal(intbv(0)[12:])
    consign_motor_2 = Signal(intbv(0)[12:])
    consign_motor_3 = Signal(intbv(0)[12:])
    consign_motor_4 = Signal(intbv(0)[12:])
    consign_motor_5 = Signal(intbv(0)[12:])
    consign_motor_6 = Signal(intbv(0)[12:])
    consign_motor_7 = Signal(intbv(0)[12:])
    consign_motor_8 = Signal(intbv(0)[12:])
    Motor1_inst = MotorDriver(mot1_pwm, mot1_dir, mot1_brake, clk25, consign_motor_1, rst_n)
    Motor2_inst = MotorDriver(mot2_pwm, mot2_dir, mot2_brake, clk25, consign_motor_2, rst_n)
    Motor3_inst = MotorDriver(mot3_pwm, mot3_dir, mot3_brake, clk25, consign_motor_3, rst_n)
    Motor4_inst = MotorDriver(mot4_pwm, mot4_dir, mot4_brake, clk25, consign_motor_4, rst_n)
    Motor5_inst = MotorDriver(mot5_pwm, mot5_dir, mot5_brake, clk25, consign_motor_5, rst_n)
    Motor6_inst = MotorDriver(mot6_pwm, mot6_dir, mot6_brake, clk25, consign_motor_6, rst_n)
    Motor7_inst = MotorDriver(mot7_pwm, mot7_dir, mot7_brake, clk25, consign_motor_7, rst_n)
    Motor8_inst = MotorDriver(mot8_pwm, mot8_dir, mot8_brake, clk25, consign_motor_8, rst_n)

    # TODO: ADC SPI

    # Servo motors
    # FIXME: lines should be inverted because of opto-isolators
    consign_servo_1 = Signal(intbv(0)[16:])
    consign_servo_2 = Signal(intbv(0)[16:])
    consign_servo_3 = Signal(intbv(0)[16:])
    consign_servo_4 = Signal(intbv(0)[16:])
    consign_servo_5 = Signal(intbv(0)[16:])
    consign_servo_6 = Signal(intbv(0)[16:])
    consign_servo_7 = Signal(intbv(0)[16:])
    consign_servo_8 = Signal(intbv(0)[16:])
    Servo1_ch0_inst = ServoDriver(pwm1_ch0, clk25, consign_servo_1, rst_n)
    Servo1_ch1_inst = ServoDriver(pwm1_ch1, clk25, consign_servo_2, rst_n)
    Servo1_ch2_inst = ServoDriver(pwm1_ch2, clk25, consign_servo_3, rst_n)
    Servo1_ch3_inst = ServoDriver(pwm1_ch3, clk25, consign_servo_4, rst_n)
    Servo1_ch4_inst = ServoDriver(pwm1_ch4, clk25, consign_servo_5, rst_n)
    Servo1_ch5_inst = ServoDriver(pwm1_ch5, clk25, consign_servo_6, rst_n)
    Servo1_ch6_inst = ServoDriver(pwm1_ch6, clk25, consign_servo_7, rst_n)
    Servo1_ch7_inst = ServoDriver(pwm1_ch7, clk25, consign_servo_8, rst_n)

    @always_comb
    def GumstixRead():
        if gs_rxdata == 31:
            gs_txdata.next = rc1_count
        elif gs_rxdata == 32:
            gs_txdata.next = rc2_count
        elif gs_rxdata == 33:
            gs_txdata.next = rc3_count
        elif gs_rxdata == 34:
            gs_txdata.next = rc4_count
        else:
            gs_txdata.next = 0

    @always_comb
    def GumstixWrite():
        if gs_rxdata == 1:
            rst_n.next = LOW
        elif gs_rxdata == 11:
            consign_motor_1.next = gs_rxdata
        elif gs_rxdata == 12:
            consign_motor_2.next = gs_rxdata
        elif gs_rxdata == 13:
            consign_motor_3.next = gs_rxdata
        elif gs_rxdata == 14:
            consign_motor_4.next = gs_rxdata
        elif gs_rxdata == 15:
            consign_motor_5.next = gs_rxdata
        elif gs_rxdata == 16:
            consign_motor_6.next = gs_rxdata
        elif gs_rxdata == 17:
            consign_motor_7.next = gs_rxdata
        elif gs_rxdata == 18:
            consign_motor_8.next = gs_rxdata
        elif gs_rxdata == 21:
            consign_servo_1.next = gs_rxdata
        elif gs_rxdata == 22:
            consign_servo_2.next = gs_rxdata
        elif gs_rxdata == 23:
            consign_servo_3.next = gs_rxdata
        elif gs_rxdata == 24:
            consign_servo_4.next = gs_rxdata
        elif gs_rxdata == 25:
            consign_servo_5.next = gs_rxdata
        elif gs_rxdata == 26:
            consign_servo_6.next = gs_rxdata
        elif gs_rxdata == 27:
            consign_servo_7.next = gs_rxdata
        elif gs_rxdata == 28:
            consign_servo_8.next = gs_rxdata

    return instances()
