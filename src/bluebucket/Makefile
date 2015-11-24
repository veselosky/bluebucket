.PHONY: clean clean-pyc clean-build docs lambda
define BROWSER_PYSCRIPT
import os, webbrowser, sys
try:
	from urllib import pathname2url
except:
	from urllib.request import pathname2url

webbrowser.open("file://" + pathname2url(os.path.abspath(sys.argv[1])))
endef
export BROWSER_PYSCRIPT
BROWSER := python -c "$$BROWSER_PYSCRIPT"

help:
	@echo "clean - remove all build, test, coverage and Python artifacts"
	@echo "coverage - check code coverage quickly with the default Python"
	@echo "dist - package it up"
	@echo "lambda - generate a zipfile to upload to AWS Lambda"
	@echo "deploy - upload zipfile to AWS Lambda for each registered function"

clean: clean-build clean-pyc clean-test

clean-build:
	rm -fr build/
	rm -fr dist/
	rm -fr .eggs/
	find . -name '*.egg-info' -exec rm -fr {} +
	find . -name '*.egg' -exec rm -f {} +

clean-pyc:
	find . -name '*.pyc' -exec rm -f {} +
	find . -name '*.pyo' -exec rm -f {} +
	find . -name '*~' -exec rm -f {} +
	find . -name '__pycache__' -exec rm -fr {} +

clean-test:
	rm -fr .tox/
	rm -f .coverage
	rm -fr htmlcov/

coverage:
	py.test --cov bluebucket
	coverage report -m
	coverage html
	$(BROWSER) htmlcov/index.html

dist: clean
	python setup.py sdist
	python setup.py bdist_wheel
	ls -l dist

lambda: dist/bluebucket-lambda.zip
	mkdir -p build/lambda
	mkdir -p dist
	pip install -t build/lambda/ .
	rm -rf build/lambda/*.dist-info build/lambda/*.egg-info
	cd build/lambda/ && zip -r ../../dist/bluebucket-lambda.zip *

deploy: lambda
	aws lambda update-function-code --function-name jsonarchetype \
        --zip-file fileb://dist/bluebucket-lambda.zip --publish
	aws lambda update-function-code --function-name markdownsource \
        --zip-file fileb://dist/bluebucket-lambda.zip --publish
	aws lambda update-function-code --function-name yamlsource \
        --zip-file fileb://dist/bluebucket-lambda.zip --publish

