from myhdl import Signal, always_comb, intbv, instance, instances

LOW, HIGH = bool(0), bool(1)

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

    # _output is an internal read/write equivalent of output.
    _output = Signal(intbv(output.val, min = output.min, max = output.max))

    # compute and saturate output
    @instance
    def do_filter():
        _previous_in = intbv(0, min = input.min, max = input.max)
        _integral = intbv(0, min = -max_I, max = max_I)
        _derivate = intbv(0, min = -max_D, max = max_D)
        while True:
            yield input, rst_n
            if rst_n == LOW:
                _integral[:] = 0
                _derivate[:] = 0
                _previous_in[:] = 0
            else:
                # compute and saturate integral term
                _tmp = input + _integral
                if _tmp >= _integral.max:
                    _integral[:] = _integral.max - 1
                elif _tmp < _integral.min:
                    _integral[:] = _integral.min
                else:
                    _integral[:] = _tmp

                # compute and saturate derivate term
                _tmp = input - _previous_in
                if _tmp >= _derivate.max:
                    _derivate[:] = _derivate.max - 1
                elif _tmp < _derivate.min:
                    _derivate[:] = _derivate.min
                else:
                    _derivate[:] = _tmp

                # keep input for next derivate computation
                _previous_in[:] = input

                # compute, saturate and drive _output
                _tmp = (input * gain_P + _integral * gain_I + _derivate * gain_D) >> out_shift
                if _tmp >= _output.max:
                    _output.next = _output.max - 1
                elif _tmp < _output.min:
                    _output.next = _output.min
                else:
                    _output.next = _tmp

    # Copies the internal output to the actual output
    @always_comb
    def drive_output():
        output.next = _output

    return instances()
