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
	# If this is here you have to setup.py develop after every clean! :(
	#find . -name '*.egg-info' -exec rm -fr {} +
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

dist/bluebucket-lambda.zip:
	mkdir -p build/lambda
	mkdir -p dist
	pip install -t build/lambda/ .
	rm -rf build/lambda/*.dist-info build/lambda/*.egg-info
	# boto3 is provided by Lambda, so do not package it or its deps
	rm -rf build/lambda/boto3 build/lambda/botocore build/lambda/concurrent build/lambda/jmespath build/lambda/docutils
	# Do not need the CLI
	rm -r build/lambda/webquills build/lambda/docopt.py
	# shaves ~1MB, but how much time cost to recompile?
	find ./build/lambda -name '*.pyc' -exec rm -f {} +
	find . -name '__pycache__' -exec rm -fr {} +
	cd build/lambda/ && zip -r ../../dist/bluebucket-lambda.zip *

lambda: dist/bluebucket-lambda.zip

deploy: lambda
	aws s3 cp dist/bluebucket-lambda.zip s3://dist.webquills.net/alpha/bluebucket-lambda.zip --acl public-read

setup:
	aws cloudformation create-stack --template-body file://cloudformation.json --stack-name WebQuills --capabilities CAPABILITY_IAM
