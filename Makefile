build:
	make -C src build

test:
	make -C src test

clean:
	make -C src clean
	rm -f *.done
	rm -f *.rpt
	rm -f *.summary
	rm -f undo_redo.txt

realclean: clean
	make -C src realclean
	rm -rf db
	rm -rf incremental_db
