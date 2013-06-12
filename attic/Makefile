.PHONY: test
test:
	(cd test; python test_AngleDistanceToLeftRight.py)
	(cd test; python test_ControlSystemManager.py)
	(cd test; python test_Counter.py)
	(cd test; python test_IdentityFilter.py)
	(cd test; python test_LeftRightToAngleDistance.py)
	(cd test; python test_PIDFilter.py)
	(cd test; python test_PolarMotors.py)
	(cd test; python test_PolarOdometers.py)
	(cd test; python test_RampFilter.py)
	(cd test; python test_KLVSlave.py)
	(cd test; python test_SPISlave.py)
	(cd test; python test_MCP3008.py)

clean:
	find lib test -name "*.pyc" -delete
	find test -name "*.vcd*" -delete
	find test -name "*.vhd*" -delete
