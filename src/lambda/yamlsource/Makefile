
.PHONY: build deploy

build:
	-rm ../yamlsource.zip
	zip -r ../yamlsource.zip yaml yamlsource.py

deploy: build
	aws lambda update-function-code --function-name yamlsource \
        --zip-file fileb://../yamlsource.zip --publish

clean:
	find . -name '*.pyc' -exec rm -f {} +
	find . -name '*.pyo' -exec rm -f {} +
	find . -name '*~' -exec rm -f {} +
	find . -name '__pycache__' -exec rm -fr {} +

