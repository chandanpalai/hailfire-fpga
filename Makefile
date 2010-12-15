build:
	mkdir -p generated
	(cd generated; python ../bin/toVHDL.py)

.PHONY: test
test:
	(cd test; python test_GumstixSPI.py)
	(cd test; python test_MotorDriver.py)
	(cd test; python test_OdometerReader.py)
	(cd test; python test_RobotIO.py)
	(cd test; python test_SPISlave.py)
	echo 'Skipping ServoDriver tests'
	# (cd test; python test_ServoDriver.py)

clean:
	find lib -name "*.pyc" -delete
	find test -name "*.vcd*" -delete
	rm -f *.dpf
	rm -f *.pin
	rm -f *.done
	rm -f *.rpt
	rm -f *.summary
	rm -f undo_redo.txt
	rm -rf db
	rm -rf incremental_db

realclean: clean
	rm -f *.pof
	rm -f *.sof
	rm -f generated/*.vhd
	rmdir generated
