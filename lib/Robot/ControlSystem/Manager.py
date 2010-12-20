from myhdl import Signal, always_comb, instances, intbv

def ControlSystemManager(consign_filter_input, consign_filter_output,
                         correct_filter_input, correct_filter_output,
                         feedback_filter_input, feedback_filter_output,
                         process_input, process_output, consign):
    """

    Control System Manager

    This module implements a classic closed loop control system to regulate
    the output of a process via a set of filters.

        consign
        |  ------------------         ------------------   -----------
        ---| consign_filter |---[X]---| correct_filter |---| process |----
           ------------------    |    ------------------   -----------   |
                                 |    -------------------                |
                                 -----| feedback_filter |-----------------
                                      -------------------

    consign_filter_input, consign_filter_output

        The input and output of the consign filter process.

    correct_filter_input, correct_filter_output

        The input and output of the error correction filter process.

    feedback_filter_input, feedback_filter_output

        The input and output of the feedback filter process.

    process_input, process_output

        The input and output of the controlled process.

    consign

        The input of the control system.

    """

    # Filter the consign
    assert consign_filter_input.min <= consign.min, 'insufficient consign_filter_input.min'
    assert consign_filter_input.max >= consign.max, 'insufficient consign_filter_input.max'
    @always_comb
    def feed_consign_filter():
        consign_filter_input.next = consign

    # Filter the feedback
    assert feedback_filter_input.min <= process_output.min, 'insufficient feedback_filter_input.min'
    assert feedback_filter_input.max >= process_output.max, 'insufficient feedback_filter_input.max'
    @always_comb
    def feed_feedback_filter():
        feedback_filter_input.next = process_output

    # Compute the error
    error = Signal(intbv(0,
        min = consign_filter_output.min - feedback_filter_output.max,
        max = consign_filter_output.max - feedback_filter_output.min))
    @always_comb
    def compute_error():
        error.next = consign_filter_output - feedback_filter_output

    # Correct the error
    assert correct_filter_input.min <= error.min, 'insufficient correct_filter_input.min'
    assert correct_filter_input.max >= error.max, 'insufficient correct_filter_input.max'
    @always_comb
    def feed_correct_filter():
        correct_filter_input.next = error

    # Feed the process
    assert process_input.min <= correct_filter_output.min, 'insufficient process_input.min'
    assert process_input.max >= correct_filter_output.max, 'insufficient process_input.max'
    @always_comb
    def feed_process():
        process_input.next = correct_filter_output

    return instances()
