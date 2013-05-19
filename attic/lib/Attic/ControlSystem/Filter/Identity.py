from myhdl import always_comb, instances

def IdentityFilter(input, output):
    """

    Identity filter module

    This filter copies its input onto its output.

    This is useful to respect the control system manager interface when one of
    the filters is not needed (such as the feedback filter, for example).

    input

        Input of the filter.

    output

        Filtered output.

    """

    @always_comb
    def drive_output():
        """ Copies the input onto the output """
        output.next = input

    return instances()
