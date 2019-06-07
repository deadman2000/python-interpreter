publish:
	python setup.py sdist bdist_wheel
	twine upload dist/*
	rm -fr build dist

install:
	pip install -e .
