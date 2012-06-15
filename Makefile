run: 
	python runserver.py

db:
	python create_db.py

test:
	python -m unittest discover tests/

dummy:

.PHONY: env dummy
