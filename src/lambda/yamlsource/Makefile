
.PHONY: build clean deploy deps test

build: ../yamlsource.zip

../yamlsource.zip: yaml yamlsource.py bluebucket.py
	-rm ../yamlsource.zip
	zip -r $@ $^

deploy: build
	aws lambda update-function-code --function-name yamlsource \
        --zip-file fileb://../yamlsource.zip --publish

deps:
	pip install -t ./ -r requirements.txt

clean:
	find . -name '*.pyc' -exec rm -f {} +
	find . -name '*.pyo' -exec rm -f {} +
	find . -name '*~' -exec rm -f {} +
	find . -name '__pycache__' -exec rm -fr {} +
	-rm ../yamlsource.zip

test:
	py.test

