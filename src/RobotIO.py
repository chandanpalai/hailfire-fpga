from myhdl import Signal, intbv, instances
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

    # chip select signals
    # TODO: assert chip select on address sent by Gumstix
    cs_1 = Signal(HIGH)
    cs_2 = Signal(HIGH)
    cs_3 = Signal(HIGH)
    cs_4 = Signal(HIGH)
    cs_5 = Signal(HIGH)
    cs_6 = Signal(HIGH)
    cs_7 = Signal(HIGH)
    cs_8 = Signal(HIGH)
    cs_9 = Signal(HIGH)
    cs_10 = Signal(HIGH)
    cs_11 = Signal(HIGH)
    cs_12 = Signal(HIGH)
    cs_13 = Signal(HIGH)
    cs_14 = Signal(HIGH)
    cs_15 = Signal(HIGH)
    cs_16 = Signal(HIGH)

    # Gumstix SPI
    GumstixSPI = SPISlave(sspi_miso, sspi_mosi, sspi_clk, sspi_cs, gs_txdata, gs_txrdy, gs_rxdata, gs_rxrdy, rst_n, 16);

    # Odometers
    rc1_count = Signal(intbv(0)[16:])
    Odometer1_inst = OdometerReader(rc1_count, rc1_cha, rc1_chb, clk25, rst_n)
    rc2_count = Signal(intbv(0)[16:])
    Odometer2_inst = OdometerReader(rc2_count, rc2_cha, rc2_chb, clk25, rst_n)
    rc3_count = Signal(intbv(0)[16:])
    Odometer3_inst = OdometerReader(rc3_count, rc3_cha, rc3_chb, clk25, rst_n)
    rc4_count = Signal(intbv(0)[16:])
    Odometer4_inst = OdometerReader(rc4_count, rc4_cha, rc4_chb, clk25, rst_n)

    # DC Motors
    # FIXME: lines should be inverted because of opto-isolators
    Motor1_inst = MotorDriver(mot1_pwm, mot1_dir, mot1_brake, clk25, gs_rxdata, cs_1, rst_n)
    Motor2_inst = MotorDriver(mot2_pwm, mot2_dir, mot2_brake, clk25, gs_rxdata, cs_2, rst_n)
    Motor3_inst = MotorDriver(mot3_pwm, mot3_dir, mot3_brake, clk25, gs_rxdata, cs_3, rst_n)
    Motor4_inst = MotorDriver(mot4_pwm, mot4_dir, mot4_brake, clk25, gs_rxdata, cs_4, rst_n)
    Motor5_inst = MotorDriver(mot5_pwm, mot5_dir, mot5_brake, clk25, gs_rxdata, cs_5, rst_n)
    Motor6_inst = MotorDriver(mot6_pwm, mot6_dir, mot6_brake, clk25, gs_rxdata, cs_6, rst_n)
    Motor7_inst = MotorDriver(mot7_pwm, mot7_dir, mot7_brake, clk25, gs_rxdata, cs_7, rst_n)
    Motor8_inst = MotorDriver(mot8_pwm, mot8_dir, mot8_brake, clk25, gs_rxdata, cs_8, rst_n)

    # TODO: ADC SPI

    # Servo motors
    # FIXME: lines should be inverted because of opto-isolators
    Servo1_ch0_inst = ServoDriver(pwm1_ch0, clk25, gs_rxdata, cs_9, rst_n)
    Servo1_ch1_inst = ServoDriver(pwm1_ch1, clk25, gs_rxdata, cs_10, rst_n)
    Servo1_ch2_inst = ServoDriver(pwm1_ch2, clk25, gs_rxdata, cs_11, rst_n)
    Servo1_ch3_inst = ServoDriver(pwm1_ch3, clk25, gs_rxdata, cs_12, rst_n)
    Servo1_ch4_inst = ServoDriver(pwm1_ch4, clk25, gs_rxdata, cs_13, rst_n)
    Servo1_ch5_inst = ServoDriver(pwm1_ch5, clk25, gs_rxdata, cs_14, rst_n)
    Servo1_ch6_inst = ServoDriver(pwm1_ch6, clk25, gs_rxdata, cs_15, rst_n)
    Servo1_ch7_inst = ServoDriver(pwm1_ch7, clk25, gs_rxdata, cs_16, rst_n)

    return instances()
