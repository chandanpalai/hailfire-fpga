from myhdl import Signal, always_comb, intbv, instance, instances
from Robot.Utils.Constants import LOW, HIGH

def PIDFilter(input, output, gain_P, gain_I, gain_D, out_shift, max_I, max_D, rst_n):
    """

    PID filter module

    This is a classic PID filter. Its output is the sum of three separate
    terms:
    - proportional: this is directly related to the input of the filter.
    - integral: this is the sum of all inputs since the last reset of the filter.
    - derivate: this term is computed from the difference between the previous
      and the current input.

    A gain is configurable for each term.

    input

        Input of the filter.

    output

        Filtered output.

    gain_P

        Proportional gain.

    gain_I

        Integral gain.

    gain_D

        Derivate gain.

    out_shift

        Common divisor for output. The division is done by shifting the output
        by the specified number of bits.

    max_I

        Integral term saturation level.

    max_D

        Derivate term saturation level.

    rst_n

        active low reset input (internal variables are reset when active)

    """

    # int_output is an internal read/write equivalent of output.
    int_output = Signal(intbv(output.val, min = output.min, max = output.max))

    # compute and saturate output
    @instance
    def do_filter():
        previous_in = intbv(0, min = input.min, max = input.max)
        integral = intbv(0, min = -max_I, max = max_I)
        derivate = intbv(0, min = -max_D, max = max_D)
        while True:
            yield input, rst_n
            if rst_n == LOW:
                integral[:] = 0
                derivate[:] = 0
                previous_in[:] = 0
            else:
                # compute and saturate integral term
                tmp = input + integral
                if tmp >= integral.max:
                    integral[:] = intbv(integral.max - 1)
                elif tmp < integral.min:
                    integral[:] = intbv(integral.min)
                else:
                    integral[:] = tmp

                # compute and saturate derivate term
                tmp = input - previous_in
                if tmp >= derivate.max:
                    derivate[:] = intbv(derivate.max - 1)
                elif tmp < derivate.min:
                    derivate[:] = intbv(derivate.min)
                else:
                    derivate[:] = tmp

                # keep input for next derivate computation
                previous_in[:] = input

                # compute, saturate and drive int_output
                tmp = (input * gain_P + integral * gain_I + derivate * gain_D) >> out_shift
                if tmp >= int_output.max:
                    int_output.next = intbv(int_output.max - 1)
                elif tmp < int_output.min:
                    int_output.next = intbv(int_output.min)
                else:
                    int_output.next = tmp

    # Copies the internal output to the actual output
    @always_comb
    def drive_output():
        output.next = int_output

    return instances()
