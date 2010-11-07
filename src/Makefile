build:
	python toVHDL_RobotIO.py

test:
	python test_GumstixSPI.py
	python test_MotorDriver.py
	python test_OdometerReader.py
	python test_RobotIO.py
	python test_SPISlave.py
	echo 'Skipping ServoDriver tests'
	# python test_ServoDriver.py

clean:
	rm -f *.vcd*
	rm -f *.pyc

realclean: clean
	rm -f *.vhd
