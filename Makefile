run: 
	python runserver.py

env: dummy
	env/bin/activate

test:
	python -m unittest discover tests/

dummy:

.PHONY: env dummy
