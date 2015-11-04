
.PHONY: build clean deploy deps test

build: ../markdownsource.zip

../markdownsource.zip: markdownsource.py bluebucket.py six.py dateutil markdown pytz
	-rm ../markdownsource.zip
	zip -r $@ $^

deploy: build
	aws lambda update-function-code --function-name markdownsource \
        --zip-file fileb://../markdownsource.zip --publish

deps:
	pip install -t ./ -r requirements.txt

clean:
	find . -name '*.pyc' -exec rm -f {} +
	find . -name '*.pyo' -exec rm -f {} +
	find . -name '*~' -exec rm -f {} +
	find . -name '__pycache__' -exec rm -fr {} +
	-rm ../markdownsource.zip

test:
	py.test

