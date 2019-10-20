REPO = 'mypackage'

.PHONY: help venv lint test clean

help:
	@echo "Use 'make target' of which target is from the following:"
	@echo "  venv		to create an virtual environment."
	@echo "  install	to install via requirements.txt."
	@echo "  lint 		to check code formatting and style."
	@echo "  format 	to format code in required style."
	@echo "  test 		to test through all test cases."

venv:
	virtualenv --python=$(which python3) --prompt '<venv: $(REPO)>' venv

install:
	venv/bin/pip install --exists-action=w --process-dependency-links -r requirements.txt

clean:
	@rm -rf dist *.egg-info .coverage .pytest_cache cobertura.xml testresult.xml
	@find . -iname "*__pycache__" | xargs rm -rf
	@find . -iname "*.pyc" | xargs rm -rf
	@rm -rf .pytest_cache
	@rm -rf .tox

deps:
	@pip3 install -r requirements.txt

lint:
	@flake8 --format=pylint --count --exit-zero

test: clean deps lint
	@pytest -s -v --cov bro --cov-report term-missing --cov-report xml:cobertura.xml --junitxml=testresult.xml tests

format:
	yapf -i --recursive .
	isort -rc .
