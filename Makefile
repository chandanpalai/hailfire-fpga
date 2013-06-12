build:
	mkdir -p generated
	(cd generated; python ../bin/toVHDL.py)

.PHONY: test
test:
	(cd test; python test_MotorDriver.py)
	(cd test; python test_OdometerReader.py)
	(cd test; python test_RobotIO.py)
	echo 'Skipping ServoDriver tests: run make longtest'

longtest: test
	(cd test; python test_ServoDriver.py)

clean:
	find lib test attic -name "*.pyc" -delete
	find test attic/test -name "*.vcd*" -delete
	find test attic/test -name "*.vhd*" -delete
	rm -f *.cdf
	rm -f *.jdi
	rm -f *.dpf
	rm -f *.pin
	rm -f *.done
	rm -f *.rpt
	rm -f *.summary
	rm -f *.qdf
	rm -f *.qws
	rm -f *.map
	rm -f *.fit.smsg
	rm -f undo_redo.txt
	rm -rf db
	rm -rf incremental_db

realclean: clean
	rm -f *.pof
	rm -f *.sof
	rm -f *.jic
	rm -f generated/*.vhd
	if [ -d generated ]; then rmdir generated; fi
