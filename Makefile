install:
	echo 'export PYTHONPATH=$$PYTHONPATH:'$(CURDIR) >> $(HOME)/.bashrc
	source $(HOME)/.bashrc

clean:
	rm -fv test/w???_*.in
	rm -fv test/w???_*.out
	rm -fv test/water_*.mol