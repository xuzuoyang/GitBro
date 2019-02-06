REPO = 'mypackage'

.PHONY: help venv lint test clean

help:
	@echo "Use 'make target' of which target is from the following:"
	@echo "  venv		to create an virtual environment"
	@echo "  install	to install via requirements.txt"
	@echo "  test 		to test through all test cases"

venv:
	virtualenv --python=$(which python3) --prompt '<venv: $(REPO)>' venv

install:
	venv/bin/pip install --exists-action=w --process-dependency-links -r requirements.txt

clean:
	find . -iname "*__pycache__" | xargs rm -rf
	find . -iname "*.pyc" | xargs rm -rf
	rm -rf .pytest_cache
	rm -rf .tox

lint:
	flake8 --format=pylint --count --exit-zero

test: clean lint
	py.test
