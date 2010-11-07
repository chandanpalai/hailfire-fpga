import unittest

from myhdl import Signal, Simulation, StopSimulation, always, concat, delay, downrange, intbv, join
from random import randrange
from RobotIO import RobotIO
from TestUtils import ClkGen, count_high, quadrature_encode, spi_transfer, LOW, HIGH

def TestBench(RobotIOTester):

    # Create signals with default values
    clk25      = Signal(LOW)

    sspi_clk   = Signal(LOW)
    sspi_cs    = Signal(HIGH)
    sspi_miso  = Signal(LOW)
    sspi_mosi  = Signal(LOW)

    rc1_cha    = Signal(LOW)
    rc1_chb    = Signal(LOW)
    rc2_cha    = Signal(LOW)
    rc2_chb    = Signal(LOW)
    rc3_cha    = Signal(LOW)
    rc3_chb    = Signal(LOW)
    rc4_cha    = Signal(LOW)
    rc4_chb    = Signal(LOW)

    mot1_brake = Signal(LOW)
    mot1_dir   = Signal(LOW)
    mot1_pwm   = Signal(LOW)

    mot2_brake = Signal(LOW)
    mot2_dir   = Signal(LOW)
    mot2_pwm   = Signal(LOW)

    mot3_brake = Signal(LOW)
    mot3_dir   = Signal(LOW)
    mot3_pwm   = Signal(LOW)

    mot4_brake = Signal(LOW)
    mot4_dir   = Signal(LOW)
    mot4_pwm   = Signal(LOW)

    mot5_brake = Signal(LOW)
    mot5_dir   = Signal(LOW)
    mot5_pwm   = Signal(LOW)

    mot6_brake = Signal(LOW)
    mot6_dir   = Signal(LOW)
    mot6_pwm   = Signal(LOW)

    mot7_brake = Signal(LOW)
    mot7_dir   = Signal(LOW)
    mot7_pwm   = Signal(LOW)

    mot8_brake = Signal(LOW)
    mot8_dir   = Signal(LOW)
    mot8_pwm   = Signal(LOW)

    adc1_clk   = Signal(LOW)
    adc1_cs    = Signal(HIGH)
    adc1_miso  = Signal(LOW)
    adc1_mosi  = Signal(LOW)

    pwm1_ch0   = Signal(LOW)
    pwm1_ch1   = Signal(LOW)
    pwm1_ch2   = Signal(LOW)
    pwm1_ch3   = Signal(LOW)
    pwm1_ch4   = Signal(LOW)
    pwm1_ch5   = Signal(LOW)
    pwm1_ch6   = Signal(LOW)
    pwm1_ch7   = Signal(LOW)

    ext1_0     = Signal(LOW)
    ext1_1     = Signal(LOW)
    ext1_2     = Signal(LOW)
    ext1_3     = Signal(LOW)
    ext1_4     = Signal(LOW)
    ext1_5     = Signal(LOW)
    ext1_6     = Signal(LOW)
    ext1_7     = Signal(LOW)

    ext2_0     = Signal(LOW)
    ext2_1     = Signal(LOW)
    ext2_2     = Signal(LOW)
    ext2_3     = Signal(LOW)
    ext2_4     = Signal(LOW)
    ext2_5     = Signal(LOW)
    ext2_6     = Signal(LOW)
    ext2_7     = Signal(LOW)

    ext3_0     = Signal(LOW)
    ext3_1     = Signal(LOW)
    ext3_2     = Signal(LOW)
    ext3_3     = Signal(LOW)
    ext3_4     = Signal(LOW)
    ext3_5     = Signal(LOW)
    ext3_6     = Signal(LOW)
    ext3_7     = Signal(LOW)

    ext4_0     = Signal(LOW)
    ext4_1     = Signal(LOW)
    ext4_2     = Signal(LOW)
    ext4_3     = Signal(LOW)
    ext4_4     = Signal(LOW)
    ext4_5     = Signal(LOW)
    ext4_6     = Signal(LOW)
    ext4_7     = Signal(LOW)

    ext5_0     = Signal(LOW)
    ext5_1     = Signal(LOW)
    ext5_2     = Signal(LOW)
    ext5_3     = Signal(LOW)
    ext5_4     = Signal(LOW)
    ext5_5     = Signal(LOW)
    ext5_6     = Signal(LOW)
    ext5_7     = Signal(LOW)

    ext6_0     = Signal(LOW)
    ext6_1     = Signal(LOW)
    ext6_2     = Signal(LOW)
    ext6_3     = Signal(LOW)
    ext6_4     = Signal(LOW)
    ext6_5     = Signal(LOW)
    ext6_6     = Signal(LOW)
    ext6_7     = Signal(LOW)

    ext7_0     = Signal(LOW)
    ext7_1     = Signal(LOW)
    ext7_2     = Signal(LOW)
    ext7_3     = Signal(LOW)
    ext7_4     = Signal(LOW)
    ext7_5     = Signal(LOW)
    ext7_6     = Signal(LOW)
    ext7_7     = Signal(LOW)

    led_yellow_n = Signal(HIGH)
    led_green_n  = Signal(HIGH)
    led_red_n    = Signal(HIGH)

    # Instanciate module under test
    RobotIO_inst = RobotIO(
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
        False
    )

    # Instanciate tester module
    RobotIOTester_inst = RobotIOTester(
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

    # Clock generator
    ClkGen_inst = ClkGen(clk25)

    return RobotIO_inst, RobotIOTester_inst, ClkGen_inst

class TestRobotIO(unittest.TestCase):

    def RobotIOTester(self,
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
                 led_yellow_n, led_green_n, led_red_n):


        #
        # LED
        #

        def get_write_led_command(color, on_off):
            """ Return an intbv suitable to be sent to the slave to set led[color] on/off """
            keys = {'yellow': 0x82, 'green': 0x83, 'red': 0x84}
            ret = intbv(0)[24:]
            ret[24:16] = keys[color] # set led on/off
            ret[16:8] = 1            # send 1 byte
            ret[8:] = on_off         # the value is the new state
            return ret

        def set_led_on_off(color, on_off):
            """ Set led[color] on/off """
            print 'set', color, 'led:', ('on' if on_off == 1 else 'off'), '...',
            master_to_slave = get_write_led_command(color, on_off)
            slave_to_master = intbv(0)
            yield spi_transfer(sspi_miso, sspi_mosi, sspi_clk, sspi_cs, master_to_slave, slave_to_master)
            print 'done'

        def set_leds_on_offs(on_offs):
            """ Set all leds on/off in one SPI transfer """
            print 'set all leds'
            master_to_slave = get_write_led_command('yellow', on_offs['yellow'])
            master_to_slave = concat(master_to_slave, get_write_led_command('green', on_offs['green']))
            master_to_slave = concat(master_to_slave, get_write_led_command('red', on_offs['red']))
            slave_to_master = intbv(0)
            yield spi_transfer(sspi_miso, sspi_mosi, sspi_clk, sspi_cs, master_to_slave, slave_to_master)
            print 'done'

        def check_led_on_off(color, on_off):
            """ Checks that the duty cycle of the led[color] really corresponds to on_off[10:] """
            print 'check', color, 'led is:', ('on' if on_off == 1 else 'off')
            lines = {
                'yellow': led_yellow_n,
                'green': led_green_n,
                'red': led_red_n
            }

            # LEDs glow when line is low
            self.assertEquals(not lines[color], on_off)

        def test_leds():
            # Generate random on_offs for leds
            on_offs = {
                'yellow': intbv(randrange(2))[8:],
                'green': intbv(randrange(2))[8:],
                'red': intbv(randrange(2))[8:],
            }

            # Set led on_offs one at a time
            for color in ['yellow', 'green', 'red']:
                yield set_led_on_off(color, on_offs[color])
                yield check_led_on_off(color, on_offs[color])

            # Regen random on_offs
            on_offs = {
                'yellow': intbv(randrange(2))[8:],
                'green': intbv(randrange(2))[8:],
                'red': intbv(randrange(2))[8:],
            }

            # Set all led on_offs together
            yield set_leds_on_offs(on_offs)

            # Check actual duty cycles
            for color in ['yellow', 'green', 'red']:
                yield check_led_on_off(color, on_offs[color])


        #
        # Ext ports
        #

        def set_ext_lines(data, l0, l1, l2, l3, l4, l5, l6, l7):
            """ Pull l[0-7] lines high or low to match bits [0-7] of data """
            l0.next = data[0]
            l1.next = data[1]
            l2.next = data[2]
            l3.next = data[3]
            l4.next = data[4]
            l5.next = data[5]
            l6.next = data[6]
            l7.next = data[7]

        def set_ext1_port(data):
            """ Pull ext1_[0-7] lines high or low to match bits [0-7] of data """
            print 'set ext1 port'
            set_ext_lines(data, ext1_0, ext1_1, ext1_2, ext1_3, ext1_4, ext1_5, ext1_6, ext1_7)

        def set_ext2_port(data):
            """ Pull ext2_[0-7] lines high or low to match bits [0-7] of data """
            print 'set ext2 port'
            set_ext_lines(data, ext2_0, ext2_1, ext2_2, ext2_3, ext2_4, ext2_5, ext2_6, ext2_7)

        def set_ext3_port(data):
            """ Pull ext3_[0-7] lines high or low to match bits [0-7] of data """
            print 'set ext3 port'
            set_ext_lines(data, ext3_0, ext3_1, ext3_2, ext3_3, ext3_4, ext3_5, ext3_6, ext3_7)

        def set_ext4_port(data):
            """ Pull ext4_[0-7] lines high or low to match bits [0-7] of data """
            print 'set ext4 port'
            set_ext_lines(data, ext4_0, ext4_1, ext4_2, ext4_3, ext4_4, ext4_5, ext4_6, ext4_7)

        def set_ext5_port(data):
            """ Pull ext5_[0-7] lines high or low to match bits [0-7] of data """
            print 'set ext5 port'
            set_ext_lines(data, ext5_0, ext5_1, ext5_2, ext5_3, ext5_4, ext5_5, ext5_6, ext5_7)

        def set_ext6_port(data):
            """ Pull ext6_[0-7] lines high or low to match bits [0-7] of data """
            print 'set ext6 port'
            set_ext_lines(data, ext6_0, ext6_1, ext6_2, ext6_3, ext6_4, ext6_5, ext6_6, ext6_7)

        def set_ext7_port(data):
            """ Pull ext7_[0-7] lines high or low to match bits [0-7] of data """
            print 'set ext7 port'
            set_ext_lines(data, ext7_0, ext7_1, ext7_2, ext7_3, ext7_4, ext7_5, ext7_6, ext7_7)

        def set_ext_ports(datas):
            """ Pull ext[1-7]_[0-7] lines high or low to match bits [0-7] of datas [1-7] """
            print 'set all ext ports'
            set_ext1_port(datas[1])
            set_ext2_port(datas[2])
            set_ext3_port(datas[3])
            set_ext4_port(datas[4])
            set_ext5_port(datas[5])
            set_ext6_port(datas[6])
            set_ext7_port(datas[7])

        def get_read_ext_port_command(number):
            """ Return an intbv suitable to be sent to the slave to read ext[number] port """
            ret = intbv(0)[24:]
            ret[24:16] = 0x20 + number  # read ext port (1 to 7)
            ret[16:8] = 1               # expect 1 byte
            return ret

        def read_ext_port(number, expected_data):
            """ Read ext[number] port and compare the result byte to expected_data """
            print 'read ext port nb:', number, '...',
            master_to_slave = get_read_ext_port_command(number)
            slave_to_master = intbv(0)
            yield spi_transfer(sspi_miso, sspi_mosi, sspi_clk, sspi_cs, master_to_slave, slave_to_master)
            self.assertEquals(slave_to_master[8:], expected_data)
            print 'done'

        def read_ext_ports(expected_datas):
            """ Read all ext ports in one SPI transfer and compare the result bytes to expected_datas """
            print 'read all ext ports at once...',
            master_to_slave = get_read_ext_port_command(7)
            for i in downrange(7, 1):
                master_to_slave = concat(master_to_slave, get_read_ext_port_command(i))
            slave_to_master = intbv(0)
            yield spi_transfer(sspi_miso, sspi_mosi, sspi_clk, sspi_cs, master_to_slave, slave_to_master)
            for i in downrange(8, 1):
                self.assertEquals(slave_to_master[i*24-16:(i-1)*24], expected_datas[i])
            print 'done'

        def test_ext_ports():
            # Generate random inputs for ext ports
            ext_port_config = [intbv(randrange(0xFF)) for i in range(8) ]

            # Set up ext ports
            set_ext_ports(ext_port_config)

            # Read ext ports separately
            for i in range(1, 8):
                yield read_ext_port(i, ext_port_config[i])

            # Read ext ports together
            yield read_ext_ports(ext_port_config)


        #
        # Odometers
        #

        def set_rc_lines(forward_steps, backward_steps, rc_a, rc_b):
            yield quadrature_encode(forward_steps, rc_a, rc_b)
            yield quadrature_encode(backward_steps, rc_b, rc_a)

        def set_rc1_port(forward_steps, backward_steps):
            """ Make rc1 roll 'forward_steps' forwards and 'backward_steps' backwards """
            print 'roll rc1', forward_steps, 'forwards and', backward_steps, 'backwards'
            yield set_rc_lines(forward_steps, backward_steps, rc1_cha, rc1_chb)

        def set_rc2_port(forward_steps, backward_steps):
            """ Make rc2 roll 'forward_steps' forwards and 'backward_steps' backwards """
            print 'roll rc2', forward_steps, 'forwards and', backward_steps, 'backwards'
            yield set_rc_lines(forward_steps, backward_steps, rc2_cha, rc2_chb)

        def set_rc3_port(forward_steps, backward_steps):
            """ Make rc3 roll 'forward_steps' forwards and 'backward_steps' backwards """
            print 'roll rc3', forward_steps, 'forwards and', backward_steps, 'backwards'
            yield set_rc_lines(forward_steps, backward_steps, rc3_cha, rc3_chb)

        def set_rc4_port(forward_steps, backward_steps):
            """ Make rc4 roll 'forward_steps' forwards and 'backward_steps' backwards """
            print 'roll rc4', forward_steps, 'forwards and', backward_steps, 'backwards'
            yield set_rc_lines(forward_steps, backward_steps, rc4_cha, rc4_chb)

        def set_rc_ports(forward_steps_array, backward_steps_array):
            """ Make all rc roll """
            print 'roll all rc'
            yield join(set_rc1_port(forward_steps_array[1], backward_steps_array[1]),
                       set_rc2_port(forward_steps_array[2], backward_steps_array[2]),
                       set_rc3_port(forward_steps_array[3], backward_steps_array[3]),
                       set_rc4_port(forward_steps_array[4], backward_steps_array[4]))

        def get_read_rc_port_command(number):
            """ Return an intbv suitable to be sent to the slave to read rc[number] port """
            ret = intbv(0)[32:]
            ret[32:24] = 0x10 + number  # read rc port (1 to 4)
            ret[24:16] = 2              # expect 2 bytes
            return ret

        def read_rc_port(number, expected_data):
            """ Read rc[number] port and compare the result byte to expected_data """
            print 'read rc port nb:', number, '...',
            master_to_slave = get_read_rc_port_command(number)
            slave_to_master = intbv(0)
            yield spi_transfer(sspi_miso, sspi_mosi, sspi_clk, sspi_cs, master_to_slave, slave_to_master)
            self.assertEquals(slave_to_master[16:], expected_data)
            print 'done'

        def read_rc_ports(expected_datas):
            """ Read all rc ports in one SPI transfer and compare the result bytes to expected_datas """
            print 'read all rc ports at once...',
            master_to_slave = get_read_rc_port_command(4)
            for i in downrange(4, 1):
                master_to_slave = concat(master_to_slave, get_read_rc_port_command(i))
            slave_to_master = intbv(0)
            yield spi_transfer(sspi_miso, sspi_mosi, sspi_clk, sspi_cs, master_to_slave, slave_to_master)
            for i in downrange(5, 1):
                self.assertEquals(slave_to_master[i*32-16:(i-1)*32], expected_datas[i])
            print 'done'

        def test_rc_ports():
            # Generate random inputs for rc ports
            rc_port_forwards  = [intbv(randrange(0xFF)) for i in range(5)]
            rc_port_backwards = [intbv(randrange(0xFF)) for i in range(5)]

            # Set up rc ports
            yield set_rc_ports(rc_port_forwards, rc_port_backwards)

            # Expected results
            expected_datas = [intbv(rc_port_forwards[i] - rc_port_backwards[i])[16:] for i in range(5)]

            # Read rc ports separately
            for i in range(1, 5):
                yield read_rc_port(i, expected_datas[i])

            # Read rc ports together
            yield read_rc_ports(expected_datas)


        #
        # Motors
        #

        def get_write_motor_command(number, consign):
            """ Return an intbv suitable to be sent to the slave to set motor[number] consign """
            ret = intbv(0)[32:]
            ret[32:24] = 0x90 + number  # set motor consign (1 to 8)
            ret[24:16] = 2              # send 2 bytes
            ret[16:] = consign          # the value is the new consign
            return ret

        def set_motor_consign(number, consign):
            """ Set motor[number] consign """
            print 'set motor:', number, '...',
            master_to_slave = get_write_motor_command(number, consign)
            slave_to_master = intbv(0)
            yield spi_transfer(sspi_miso, sspi_mosi, sspi_clk, sspi_cs, master_to_slave, slave_to_master)
            print 'done'

        def set_motors_consigns(consigns):
            """ Set all motors consigns in one SPI transfer """
            print 'set all motors'
            master_to_slave = get_write_motor_command(8, consigns[8])
            for i in downrange(8, 1):
                master_to_slave = concat(master_to_slave, get_write_motor_command(i, consigns[i]))
            slave_to_master = intbv(0)
            yield spi_transfer(sspi_miso, sspi_mosi, sspi_clk, sspi_cs, master_to_slave, slave_to_master)
            print 'done'

        def check_motor_duty_cycle(number, consign):
            """ Checks that the duty cycle of the motor[number] really corresponds to consign[10:] """
            print 'check motor', number
            lines = [None, mot1_pwm, mot2_pwm, mot3_pwm, mot4_pwm, mot5_pwm, mot6_pwm, mot7_pwm, mot8_pwm]
            count = intbv(0)

            # First period is not correct as the counter had already started
            # before the consign was given. Start testing at the second period
            yield lines[number].negedge # wait for end of PWM waveform of the first period
            yield lines[number].posedge # wait for the beginning of the period

            yield count_high(lines[number], clk25, count)
            self.assertEquals(count, consign[10:])

        def test_motors():
            # Generate random consigns for motors
            consigns = [intbv(randrange(2**10))[16:] for i in range(9)]

            # Set motor consigns one at a time
            for i in range(1, 9):
                yield set_motor_consign(i, consigns[i])

            # Check actual duty cycles
            yield join(check_motor_duty_cycle(1, consigns[1]),
                       check_motor_duty_cycle(2, consigns[2]),
                       check_motor_duty_cycle(3, consigns[3]),
                       check_motor_duty_cycle(4, consigns[4]),
                       check_motor_duty_cycle(5, consigns[5]),
                       check_motor_duty_cycle(6, consigns[6]),
                       check_motor_duty_cycle(7, consigns[7]),
                       check_motor_duty_cycle(8, consigns[8]))

            # Regen random consigns
            consigns = [intbv(randrange(2**10))[16:] for i in range(9)]

            # Set all motor consigns together
            yield set_motors_consigns(consigns)

            # Check actual duty cycles
            yield join(check_motor_duty_cycle(1, consigns[1]),
                       check_motor_duty_cycle(2, consigns[2]),
                       check_motor_duty_cycle(3, consigns[3]),
                       check_motor_duty_cycle(4, consigns[4]),
                       check_motor_duty_cycle(5, consigns[5]),
                       check_motor_duty_cycle(6, consigns[6]),
                       check_motor_duty_cycle(7, consigns[7]),
                       check_motor_duty_cycle(8, consigns[8]))


        #
        # Servos
        #

        def get_write_servo_command(number, consign):
            """ Return an intbv suitable to be sent to the slave to set servo[number] consign """
            ret = intbv(0)[32:]
            ret[32:24] = 0xA0 + number  # set servo consign (1 to 8)
            ret[24:16] = 2              # send 2 bytes
            ret[16:] = consign          # the value is the new consign
            return ret

        def set_servo_consign(number, consign):
            """ Set servo[number] consign """
            print 'set servo:', number, '...',
            master_to_slave = get_write_servo_command(number, consign)
            slave_to_master = intbv(0)
            yield spi_transfer(sspi_miso, sspi_mosi, sspi_clk, sspi_cs, master_to_slave, slave_to_master)
            print 'done'

        def set_servos_consigns(consigns):
            """ Set all servos consigns in one SPI transfer """
            print 'set all servos'
            master_to_slave = get_write_servo_command(8, consigns[8])
            for i in downrange(8, 1):
                master_to_slave = concat(master_to_slave, get_write_servo_command(i, consigns[i]))
            slave_to_master = intbv(0)
            yield spi_transfer(sspi_miso, sspi_mosi, sspi_clk, sspi_cs, master_to_slave, slave_to_master)
            print 'done'

        def check_servo_duty_cycle(number, consign):
            """ Checks that the duty cycle of the servo[number] really corresponds to consign """
            print 'check servo', number, 'beginning'
            lines = [None, pwm1_ch0, pwm1_ch1, pwm1_ch2, pwm1_ch3, pwm1_ch4, pwm1_ch5, pwm1_ch6, pwm1_ch7]
            count = intbv(0)

            # First period is not correct as the counter had already started
            # before the consign was given. Start testing at the second period
            yield lines[number].negedge # wait for end of PWM waveform of the first period
            print 'check servo', number, 'wait for the beginning of the period'
            yield lines[number].posedge # wait for the beginning of the period
            print 'check servo', number, 'count highs'

            yield count_high(lines[number], clk25, count)
            self.assertEquals(count, consign)
            print 'check servo', number, 'done'

        def test_servos():
            # Generate random consigns for servos
            # respect min/max useful consigns
            consigns = [intbv(randrange(12500, 62500))[16:] for i in range(9)]

            # Set servo consigns one at a time
            for i in range(1, 9):
                yield set_servo_consign(i, consigns[i])

            # Check actual duty cycles
            yield join(check_servo_duty_cycle(1, consigns[1]),
                       check_servo_duty_cycle(2, consigns[2]),
                       check_servo_duty_cycle(3, consigns[3]),
                       check_servo_duty_cycle(4, consigns[4]),
                       check_servo_duty_cycle(5, consigns[5]),
                       check_servo_duty_cycle(6, consigns[6]),
                       check_servo_duty_cycle(7, consigns[7]),
                       check_servo_duty_cycle(8, consigns[8]))

            # Regen random consigns
            # respect min/max useful consigns
            consigns = [intbv(randrange(12500, 62500))[16:] for i in range(9)]

            # Set all servo consigns together
            yield set_servos_consigns(consigns)

            # Check actual duty cycles
            yield join(check_servo_duty_cycle(1, consigns[1]),
                       check_servo_duty_cycle(2, consigns[2]),
                       check_servo_duty_cycle(3, consigns[3]),
                       check_servo_duty_cycle(4, consigns[4]),
                       check_servo_duty_cycle(5, consigns[5]),
                       check_servo_duty_cycle(6, consigns[6]),
                       check_servo_duty_cycle(7, consigns[7]),
                       check_servo_duty_cycle(8, consigns[8]))


        #
        # Tests
        #

        yield test_leds()
        yield test_ext_ports()
        yield test_rc_ports()
        yield test_motors()
        if False:
            yield test_servos()
        else:
            print "Skipping servo tests"

        raise StopSimulation();

    def testRobotIO(self):
        """ Test RobotIO """
        sim = Simulation(TestBench(self.RobotIOTester))
        sim.run()

if __name__ == '__main__':
    unittest.main()
