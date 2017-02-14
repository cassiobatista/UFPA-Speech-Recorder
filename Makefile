target=main.py

all:
	python -B $(target)

clean:
	rm -f *.pyc
	cd src && rm -f *.pyc
