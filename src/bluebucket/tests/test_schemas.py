# vim: set fileencoding=utf-8 :
#
#   Copyright 2016 Vince Veselosky and contributors
#
#   Licensed under the Apache License, Version 2.0 (the "License");
#   you may not use this file except in compliance with the License.
#   You may obtain a copy of the License at
#
#       http://www.apache.org/licenses/LICENSE-2.0
#
#   Unless required by applicable law or agreed to in writing, software
#   distributed under the License is distributed on an "AS IS" BASIS,
#   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#   See the License for the specific language governing permissions and
#   limitations under the License.
#
from __future__ import absolute_import, print_function, unicode_literals
from io import open
import json
import jsonschema
import pkg_resources
import stubs


def test_item_schema_is_valid():
    schemafile = pkg_resources.resource_filename('bluebucket.schemas',
                                                 'metaschema.json')
    with open(schemafile, encoding="utf-8") as f:
        schema = json.load(f)

    testfile = pkg_resources.resource_filename('bluebucket.schemas',
                                               'Item.json')
    with open(testfile, encoding='utf-8') as f:
        testjson = json.load(f)

    # raises ValidationError if not valid
    jsonschema.validate(testjson, schema)


def test_page_schema_is_valid():
    schemafile = pkg_resources.resource_filename('bluebucket.schemas',
                                                 'metaschema.json')
    with open(schemafile, encoding="utf-8") as f:
        schema = json.load(f)

    testfile = pkg_resources.resource_filename('bluebucket.schemas',
                                               'Page.json')
    with open(testfile, encoding='utf-8') as f:
        testjson = json.load(f)

    # raises ValidationError if not valid
    jsonschema.validate(testjson, schema)


def test_article_schema_is_valid():
    schemafile = pkg_resources.resource_filename('bluebucket.schemas',
                                                 'metaschema.json')
    with open(schemafile, encoding="utf-8") as f:
        schema = json.load(f)

    testfile = pkg_resources.resource_filename('bluebucket.schemas',
                                               'Article.json')
    with open(testfile, encoding='utf-8') as f:
        testjson = json.load(f)

    # raises ValidationError if not valid
    jsonschema.validate(testjson, schema)


def test_catalog_schema_is_valid():
    schemafile = pkg_resources.resource_filename('bluebucket.schemas',
                                                 'metaschema.json')
    with open(schemafile, encoding="utf-8") as f:
        schema = json.load(f)

    testfile = pkg_resources.resource_filename('bluebucket.schemas',
                                               'Catalog.json')
    with open(testfile, encoding='utf-8') as f:
        testjson = json.load(f)

    # raises ValidationError if not valid
    jsonschema.validate(testjson, schema)


def test_event_s3_schema_is_valid():
    schemafile = pkg_resources.resource_filename('bluebucket.schemas',
                                                 'metaschema.json')
    with open(schemafile, encoding="utf-8") as f:
        schema = json.load(f)

    testfile = pkg_resources.resource_filename('bluebucket.schemas',
                                               'event_s3.json')
    with open(testfile, encoding='utf-8') as f:
        testjson = json.load(f)

    # raises ValidationError if not valid
    jsonschema.validate(testjson, schema)


def test_event_s3_schema_validates_sample():
    schemafile = pkg_resources.resource_filename('bluebucket.schemas',
                                                 'event_s3.json')
    with open(schemafile, encoding="utf-8") as f:
        schema = json.load(f)

    testjson = stubs.s3eventsource

    # raises ValidationError if not valid
    jsonschema.validate(testjson, schema)

