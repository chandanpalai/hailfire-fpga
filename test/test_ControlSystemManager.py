import sys
sys.path.append('../lib')

import unittest

from myhdl import Signal, Simulation, toVHDL, StopSimulation, always_comb, intbv, join, traceSignals
from Robot.ControlSystem.Manager import ControlSystemManager
from Robot.Utils.Constants import LOW, HIGH

def TestBench(ControlSystemManagerTester):
    # create fake consign filter
    consign_filter_input   = Signal(intbv(0, min = -2**30, max = 2**30)) # 31-bit
    consign_filter_output  = Signal(intbv(0, min = -2**30, max = 2**30)) # 31-bit
    @always_comb
    def fake_consign_filter():
        consign_filter_output.next = consign_filter_input

    # create fake correct filter
    correct_filter_input   = Signal(intbv(0, min = -2**31, max = 2**31)) # 32-bit
    correct_filter_output  = Signal(intbv(0, min = -2**31, max = 2**31)) # 32-bit
    @always_comb
    def fake_correct_filter():
        correct_filter_output.next = correct_filter_input

    # create fake feedback filter
    feedback_filter_input  = Signal(intbv(0, min = -2**30, max = 2**30)) # 31-bit
    feedback_filter_output = Signal(intbv(0, min = -2**30, max = 2**30)) # 31-bit
    @always_comb
    def fake_feedback_filter():
        feedback_filter_output.next = feedback_filter_input

    # create fake process
    process_input  = Signal(intbv(0, min = -2**31, max = 2**31)) # 32-bit
    process_output = Signal(intbv(0, min = -2**30, max = 2**30)) # 31-bit
    @always_comb
    def fake_process():
        process_output.next = process_input

    # control system inputs
    consign = Signal(intbv(0, min = -2**30, max = 2**30)) # 31-bit
    enable  = Signal(LOW)

    # instanciate modules
    ControlSystemManager_inst = toVHDL(
        ControlSystemManager,
        consign_filter_input, consign_filter_output,
        correct_filter_input, correct_filter_output,
        feedback_filter_input, feedback_filter_output,
        process_input, process_output, consign, enable)
    ControlSystemManagerTester_inst = ControlSystemManagerTester(
        consign_filter_input, consign_filter_output,
        correct_filter_input, correct_filter_output,
        feedback_filter_input, feedback_filter_output,
        process_input, process_output, consign, enable)

    return (fake_consign_filter,
            fake_correct_filter,
            fake_feedback_filter,
            fake_process,
            ControlSystemManager_inst,
            ControlSystemManagerTester_inst)

class TestControlSystemManager(unittest.TestCase):

    def ControlSystemManagerTester(self,
        consign_filter_input, consign_filter_output,
        correct_filter_input, correct_filter_output,
        feedback_filter_input, feedback_filter_output,
        process_input, process_output, consign, enable):

        self.assertEquals(process_input, 0)
        self.assertEquals(process_output, 0)

        # enable the control system
        enable.next = HIGH

        # consign: 0 to 42, process_output: 0 to 42
        consign.next = 42
        yield process_input
        self.assertEquals(consign_filter_input, 42)
        self.assertEquals(consign_filter_output, 42)
        self.assertEquals(feedback_filter_input, 0)
        self.assertEquals(feedback_filter_output, 0)
        self.assertEquals(correct_filter_input, 42)
        self.assertEquals(correct_filter_output, 42)
        self.assertEquals(process_input, 42)

        # consign: 42 to 50, process_output: 42 to (51-42)=9
        consign.next = 51
        yield process_input
        self.assertEquals(consign_filter_input, 51)
        self.assertEquals(consign_filter_output, 51)
        self.assertEquals(feedback_filter_input, 42)
        self.assertEquals(feedback_filter_output, 42)
        self.assertEquals(correct_filter_input, 9)
        self.assertEquals(correct_filter_output, 9)
        self.assertEquals(process_input, 9)

        # don't change the consign
        # system will oscillate between 9 and 42
        yield process_input
        self.assertEquals(consign_filter_input, 51)
        self.assertEquals(consign_filter_output, 51)
        self.assertEquals(feedback_filter_input, 9)
        self.assertEquals(feedback_filter_output, 9)
        self.assertEquals(correct_filter_input, 42)
        self.assertEquals(correct_filter_output, 42)
        self.assertEquals(process_input, 42)

        print 'DONE'

        raise StopSimulation()

    def testControlSystemManager(self):
        """ Ensures that filter works as espected """
        sim = Simulation(TestBench(self.ControlSystemManagerTester))
        sim.run()

if __name__ == '__main__':
    unittest.main()
