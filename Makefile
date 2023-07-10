install:
	echo 'export PYTHONPATH=$$PYTHONPATH:'$(CURDIR) >> $(HOME)/.bashrc
	source $(HOME)/.bashrc