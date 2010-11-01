from myhdl import Signal, intbv, always, always_comb, instances
from OdometerReader import OdometerReader
from MotorDriver import MotorDriver
from ServoDriver import ServoDriver
from GumstixSPI import GumstixSPI

LOW, HIGH = bool(0), bool(1)

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

    # communication with GumstixSPI
    key = Signal(intbv(0)[8:])
    length = Signal(intbv(0)[8:])
    master_read_n = Signal(HIGH)
    value_for_master = Signal(intbv(0)[MAX_LENGTH*8:])
    master_write_n = Signal(HIGH)
    value_from_master = Signal(intbv(0)[MAX_LENGTH*8:])

    # 16-bit value sent by the Gumstix for many things (motor & servo consigns...)
    gs_rxdata = Signal(intbv(0)[16:])

    # chip-wide active low reset signal
    rst_n = Signal(HIGH)

    # chip select signals
    # TODO: assert chip select on address sent by Gumstix
    cs_n = Signal(intbv(0)[32:])

    # These signals and the slice_shadower could be replaced by shadow signals
    # when MyHDL 0.7 is released
    cs_0 = Signal(HIGH)
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
    cs_17 = Signal(HIGH)
    cs_18 = Signal(HIGH)
    cs_19 = Signal(HIGH)
    cs_20 = Signal(HIGH)
    cs_21 = Signal(HIGH)
    cs_22 = Signal(HIGH)
    cs_23 = Signal(HIGH)
    cs_24 = Signal(HIGH)
    cs_25 = Signal(HIGH)
    cs_26 = Signal(HIGH)
    cs_27 = Signal(HIGH)
    cs_28 = Signal(HIGH)
    cs_29 = Signal(HIGH)
    cs_30 = Signal(HIGH)
    cs_31 = Signal(HIGH)

    @always_comb
    def slice_shadower():
        cs_0.next = cs_n[0]
        cs_1.next = cs_n[1]
        cs_2.next = cs_n[2]
        cs_3.next = cs_n[3]
        cs_4.next = cs_n[4]
        cs_5.next = cs_n[5]
        cs_6.next = cs_n[6]
        cs_7.next = cs_n[7]
        cs_8.next = cs_n[8]
        cs_9.next = cs_n[9]
        cs_10.next = cs_n[10]
        cs_11.next = cs_n[11]
        cs_12.next = cs_n[12]
        cs_13.next = cs_n[13]
        cs_14.next = cs_n[14]
        cs_15.next = cs_n[15]
        cs_16.next = cs_n[16]
        cs_17.next = cs_n[17]
        cs_18.next = cs_n[18]
        cs_19.next = cs_n[19]
        cs_20.next = cs_n[20]
        cs_21.next = cs_n[21]
        cs_22.next = cs_n[22]
        cs_23.next = cs_n[23]
        cs_24.next = cs_n[24]
        cs_25.next = cs_n[25]
        cs_26.next = cs_n[26]
        cs_27.next = cs_n[27]
        cs_28.next = cs_n[28]
        cs_29.next = cs_n[29]
        cs_30.next = cs_n[30]
        cs_31.next = cs_n[31]

    # Chip-wide reset
    @always_comb
    def driveReset():
        rst_n.next = cs_0

    # Gumstix SPI
    GumstixSPI_inst = GumstixSPI(sspi_miso, sspi_mosi, sspi_clk, sspi_cs,
                                 key, length, master_read_n, value_for_master, master_write_n, value_from_master,
                                 clk25, rst_n)

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
    Motor1_inst = MotorDriver(mot1_pwm, mot1_dir, mot1_brake, clk25, gs_rxdata, cs_11, rst_n)
    Motor2_inst = MotorDriver(mot2_pwm, mot2_dir, mot2_brake, clk25, gs_rxdata, cs_12, rst_n)
    Motor3_inst = MotorDriver(mot3_pwm, mot3_dir, mot3_brake, clk25, gs_rxdata, cs_13, rst_n)
    Motor4_inst = MotorDriver(mot4_pwm, mot4_dir, mot4_brake, clk25, gs_rxdata, cs_14, rst_n)
    Motor5_inst = MotorDriver(mot5_pwm, mot5_dir, mot5_brake, clk25, gs_rxdata, cs_15, rst_n)
    Motor6_inst = MotorDriver(mot6_pwm, mot6_dir, mot6_brake, clk25, gs_rxdata, cs_16, rst_n)
    Motor7_inst = MotorDriver(mot7_pwm, mot7_dir, mot7_brake, clk25, gs_rxdata, cs_17, rst_n)
    Motor8_inst = MotorDriver(mot8_pwm, mot8_dir, mot8_brake, clk25, gs_rxdata, cs_18, rst_n)

    # TODO: ADC SPI

    # Servo motors
    # FIXME: lines should be inverted because of opto-isolators
    Servo1_ch0_inst = ServoDriver(pwm1_ch0, clk25, gs_rxdata, cs_21, rst_n)
    Servo1_ch1_inst = ServoDriver(pwm1_ch1, clk25, gs_rxdata, cs_22, rst_n)
    Servo1_ch2_inst = ServoDriver(pwm1_ch2, clk25, gs_rxdata, cs_23, rst_n)
    Servo1_ch3_inst = ServoDriver(pwm1_ch3, clk25, gs_rxdata, cs_24, rst_n)
    Servo1_ch4_inst = ServoDriver(pwm1_ch4, clk25, gs_rxdata, cs_25, rst_n)
    Servo1_ch5_inst = ServoDriver(pwm1_ch5, clk25, gs_rxdata, cs_26, rst_n)
    Servo1_ch6_inst = ServoDriver(pwm1_ch6, clk25, gs_rxdata, cs_27, rst_n)
    Servo1_ch7_inst = ServoDriver(pwm1_ch7, clk25, gs_rxdata, cs_28, rst_n)

    # Master reads: 0x01 <= key <= 0x7F
    @always(master_read_n.negedge, rst_n.negedge)
    def GumstixRead():
        if rst_n == LOW:
            value_for_master.next[MAX_LENGTH*8:] = 0
        else:
            if key == 0x11:
                value_for_master.next[16:] = rc1_count
            elif key == 0x12:
                value_for_master.next[16:] = rc2_count
            elif key == 0x13:
                value_for_master.next[16:] = rc3_count
            elif key == 0x14:
                value_for_master.next[16:] = rc4_count
            elif key == 0x21:
                value_for_master.next[0] = ext1_0
                value_for_master.next[1] = ext1_1
                value_for_master.next[2] = ext1_2
                value_for_master.next[3] = ext1_3
                value_for_master.next[4] = ext1_4
                value_for_master.next[5] = ext1_5
                value_for_master.next[6] = ext1_6
                value_for_master.next[7] = ext1_7
            elif key == 0x22:
                value_for_master.next[0] = ext2_0
                value_for_master.next[1] = ext2_1
                value_for_master.next[2] = ext2_2
                value_for_master.next[3] = ext2_3
                value_for_master.next[4] = ext2_4
                value_for_master.next[5] = ext2_5
                value_for_master.next[6] = ext2_6
                value_for_master.next[7] = ext2_7
            elif key == 0x23:
                value_for_master.next[0] = ext3_0
                value_for_master.next[1] = ext3_1
                value_for_master.next[2] = ext3_2
                value_for_master.next[3] = ext3_3
                value_for_master.next[4] = ext3_4
                value_for_master.next[5] = ext3_5
                value_for_master.next[6] = ext3_6
                value_for_master.next[7] = ext3_7
            elif key == 0x24:
                value_for_master.next[0] = ext4_0
                value_for_master.next[1] = ext4_1
                value_for_master.next[2] = ext4_2
                value_for_master.next[3] = ext4_3
                value_for_master.next[4] = ext4_4
                value_for_master.next[5] = ext4_5
                value_for_master.next[6] = ext4_6
                value_for_master.next[7] = ext4_7
            elif key == 0x25:
                value_for_master.next[0] = ext5_0
                value_for_master.next[1] = ext5_1
                value_for_master.next[2] = ext5_2
                value_for_master.next[3] = ext5_3
                value_for_master.next[4] = ext5_4
                value_for_master.next[5] = ext5_5
                value_for_master.next[6] = ext5_6
                value_for_master.next[7] = ext5_7
            elif key == 0x26:
                value_for_master.next[0] = ext6_0
                value_for_master.next[1] = ext6_1
                value_for_master.next[2] = ext6_2
                value_for_master.next[3] = ext6_3
                value_for_master.next[4] = ext6_4
                value_for_master.next[5] = ext6_5
                value_for_master.next[6] = ext6_6
                value_for_master.next[7] = ext6_7
            elif key == 0x27:
                value_for_master.next[0] = ext7_0
                value_for_master.next[1] = ext7_1
                value_for_master.next[2] = ext7_2
                value_for_master.next[3] = ext7_3
                value_for_master.next[4] = ext7_4
                value_for_master.next[5] = ext7_5
                value_for_master.next[6] = ext7_6
                value_for_master.next[7] = ext7_7
            else:
                # Dummy value sent when key is unknown.
                # The value is fixed. The master read 'length'
                # bytes from it.
                value_for_master.next[64:] = 0xDEADBEEFBAADF00D

    # Master writes: 0x81 <= key <= 0xFF
    @always(master_write_n.negedge, rst_n.negedge)
    def GumstixWrite():
        if rst_n == LOW:
            cs_n.next = intbv(0xFFFFFFFF)[32:]
        else:
            # Reset
            if key == 0x81:
                cs_n.next = intbv(0xFFFFFFFF)[32:]
                cs_n[0].next = 0

            # Motors                
            elif 0x91 <= key and key <= 0x98:
                gs_rxdata.next[16:] = value_from_master[16:]

                cs_n.next = intbv(0xFFFFFFFF)[32:]
                cs_n[int(key) - 0x80].next = 0

            # Servos
            elif 0xA1 <= key and key <= 0xA8:
                gs_rxdata.next[16:] = value_from_master[16:]

                cs_n.next = intbv(0xFFFFFFFF)[32:]
                cs_n[int(key) - 0x80].next = 0

    return instances()
