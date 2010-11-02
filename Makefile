build:
	make -C src build

test:
	make -C src test

clean:
	make -C src clean
	rm -f *.pin
	rm -f *.done
	rm -f *.rpt
	rm -f *.summary
	rm -f undo_redo.txt
	rm -rf db
	rm -rf incremental_db

realclean: clean
	make -C src realclean
	rm -f *.pof
	rm -f *.sof
