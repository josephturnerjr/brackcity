run: 
	python runserver.py

env: dummy
	env/bin/activate

dummy:

.PHONY: env dummy
