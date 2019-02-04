clean:
	find . -iname "*__pycache__" | xargs rm -rf
	find . -iname "*.pyc" | xargs rm -rf
	rm -rf .pytest_cache


lint:
	flake8 --format=pylint --count --exit-zero


test: clean lint
	py.test
