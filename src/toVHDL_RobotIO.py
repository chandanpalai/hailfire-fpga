from myhdl import Signal, toVHDL

from RobotIO import RobotIO

clk25      = Signal(bool(0))

sspi_clk   = Signal(bool(0))
sspi_cs    = Signal(bool(0))
sspi_miso  = Signal(bool(0))
sspi_mosi  = Signal(bool(0))

rc1_cha    = Signal(bool(0))
rc1_chb    = Signal(bool(0))
rc2_cha    = Signal(bool(0))
rc2_chb    = Signal(bool(0))
rc3_cha    = Signal(bool(0))
rc3_chb    = Signal(bool(0))
rc4_cha    = Signal(bool(0))
rc4_chb    = Signal(bool(0))

mot1_brake = Signal(bool(0))
mot1_dir   = Signal(bool(0))
mot1_pwm   = Signal(bool(0))

mot2_brake = Signal(bool(0))
mot2_dir   = Signal(bool(0))
mot2_pwm   = Signal(bool(0))

mot3_brake = Signal(bool(0))
mot3_dir   = Signal(bool(0))
mot3_pwm   = Signal(bool(0))

mot4_brake = Signal(bool(0))
mot4_dir   = Signal(bool(0))
mot4_pwm   = Signal(bool(0))

mot5_brake = Signal(bool(0))
mot5_dir   = Signal(bool(0))
mot5_pwm   = Signal(bool(0))

mot6_brake = Signal(bool(0))
mot6_dir   = Signal(bool(0))
mot6_pwm   = Signal(bool(0))

mot7_brake = Signal(bool(0))
mot7_dir   = Signal(bool(0))
mot7_pwm   = Signal(bool(0))

mot8_brake = Signal(bool(0))
mot8_dir   = Signal(bool(0))
mot8_pwm   = Signal(bool(0))

adc1_clk   = Signal(bool(0))
adc1_cs    = Signal(bool(0))
adc1_miso  = Signal(bool(0))
adc1_mosi  = Signal(bool(0))

pwm1_ch0   = Signal(bool(0))
pwm1_ch1   = Signal(bool(0))
pwm1_ch2   = Signal(bool(0))
pwm1_ch3   = Signal(bool(0))
pwm1_ch4   = Signal(bool(0))
pwm1_ch5   = Signal(bool(0))
pwm1_ch6   = Signal(bool(0))
pwm1_ch7   = Signal(bool(0))

ext1_0     = Signal(bool(0))
ext1_1     = Signal(bool(0))
ext1_2     = Signal(bool(0))
ext1_3     = Signal(bool(0))
ext1_4     = Signal(bool(0))
ext1_5     = Signal(bool(0))
ext1_6     = Signal(bool(0))
ext1_7     = Signal(bool(0))

ext2_0     = Signal(bool(0))
ext2_1     = Signal(bool(0))
ext2_2     = Signal(bool(0))
ext2_3     = Signal(bool(0))
ext2_4     = Signal(bool(0))
ext2_5     = Signal(bool(0))
ext2_6     = Signal(bool(0))
ext2_7     = Signal(bool(0))

ext3_0     = Signal(bool(0))
ext3_1     = Signal(bool(0))
ext3_2     = Signal(bool(0))
ext3_3     = Signal(bool(0))
ext3_4     = Signal(bool(0))
ext3_5     = Signal(bool(0))
ext3_6     = Signal(bool(0))
ext3_7     = Signal(bool(0))

ext4_0     = Signal(bool(0))
ext4_1     = Signal(bool(0))
ext4_2     = Signal(bool(0))
ext4_3     = Signal(bool(0))
ext4_4     = Signal(bool(0))
ext4_5     = Signal(bool(0))
ext4_6     = Signal(bool(0))
ext4_7     = Signal(bool(0))

ext5_0     = Signal(bool(0))
ext5_1     = Signal(bool(0))
ext5_2     = Signal(bool(0))
ext5_3     = Signal(bool(0))
ext5_4     = Signal(bool(0))
ext5_5     = Signal(bool(0))
ext5_6     = Signal(bool(0))
ext5_7     = Signal(bool(0))

ext6_0     = Signal(bool(0))
ext6_1     = Signal(bool(0))
ext6_2     = Signal(bool(0))
ext6_3     = Signal(bool(0))
ext6_4     = Signal(bool(0))
ext6_5     = Signal(bool(0))
ext6_6     = Signal(bool(0))
ext6_7     = Signal(bool(0))

ext7_0     = Signal(bool(0))
ext7_1     = Signal(bool(0))
ext7_2     = Signal(bool(0))
ext7_3     = Signal(bool(0))
ext7_4     = Signal(bool(0))
ext7_5     = Signal(bool(0))
ext7_6     = Signal(bool(0))
ext7_7     = Signal(bool(0))

led_yellow_n = Signal(bool(0))
led_green_n  = Signal(bool(0))
led_red_n    = Signal(bool(0))

RobotIO_inst = toVHDL(RobotIO,
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
    led_yellow_n, led_green_n, led_red_n
)
