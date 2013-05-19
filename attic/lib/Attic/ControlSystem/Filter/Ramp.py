from myhdl import Signal, intbv, instance, always_comb, instances

def RampFilter(input, output, var_1st_ord_pos, var_1st_ord_neg):
    """

    Ramp filter module

    This filter ensures that its output is continuous and respects maximum rise
    and fall coefficients.

    This is useful to ensure that a speed consign is continuous, even if the input
    speed consign changes dramatically, while respecting maximum acceleration and
    deceleration values.

    The input is a speed consign. The filter is configured with acceleration
    limits. Those limits determine the shape of the output (rise and fall
    coefficients). The output is a filtered speed consign that can be applied
    to a PID filter in a speed control system, for example.

    For example, if the input changes suddenly from 0 to 100, then the output
    will vary from 0 to 100 while respecting the maximum acceleration.

    input

        Input of the filter.

    output

        Filtered output.

    var_1st_ord_pos

        Maximum positive value of the first order derivate of the output
        If the output is a speed, then this is the maximum acceleration.

    var_1st_ord_neg

        ABS(maximum negative value of the first order derivate of the output).
        If the output is a speed, then this is the maximum deceleration.

    """

    # _output is an internal read/write equivalent of output.
    int_output = Signal(intbv(output.val, min = output.min, max = output.max))

    # This does a @always_comb. Doing it like this allows inout internal signals.
    @instance
    def do_filter():
        while True:
            yield input, int_output, var_1st_ord_pos, var_1st_ord_neg
            if input > int_output:
                if (input - int_output) < var_1st_ord_pos:
                    int_output.next = input
                else:
                    int_output.next = int_output + var_1st_ord_pos
            else:
                if (int_output - input) < var_1st_ord_neg:
                    int_output.next = input
                else:
                    int_output.next = int_output - var_1st_ord_neg

    # Copies the internal output to the actual output
    @always_comb
    def drive_output():
        output.next = int_output

    return instances()
