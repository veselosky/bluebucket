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
import mock
import pkg_resources
import pytz

from bluebucket.archivist import S3archivist
import webquills.scribe.markdown as mark

testbucket = 'bluebucket.mindvessel.net'

#: Test document with special cases. Cases are:
#: - all attributes given in title case
#: - dates have no time component
#: - itemtype is given as lower case (should be title case)
#: - author is given instead of attribution
#: - category is given as a simple string
#: - slug is missing
#: - body contains unicode characters
doc1 = """Published: 2015-11-03
Updated: 2015-11-03
Created: 2015-11-03
Guid: f57beeec-9958-45bb-911e-df5a95064523
Itemtype: item/page/article
Description: A test document.You know, for testing.
Author: Vinnie "the Rueben" Veselosky
Category: test/category
Title: Spanish Lesson

¿Dónde esta el baño?
"""

#: Test document with special cases. Cases are:
#: - updated has a timezone
#: - attribution not provided (should fall back to site config)
doc2 = """itemtype: Item/Page/Article
guid: 02eb3153-6d45-4c96-8bcb-f7da85e69624
updated: 2016-06-24T07:56:00-0400
category: fake/content
slug: test-article-one
title: Test article one

# The Test Article

A test article serves the purpose of checking what happens when something gets
saved into the bucket.

I wrote this test article as a test, with some text and some metadata. Not much
metadata, mind you. Just barely enough to test out some things.
"""

schemafile = pkg_resources.resource_filename('bluebucket.schemas', 'Item.json')
with open(schemafile, encoding="utf-8") as f:
    schema = json.load(f)

out = b'{"body": "<p>\u00bfD\u00f3nde esta el ba\u00f1o?</p>", "guid": "f57beeec-9958-45bb-911e-df5a95064523", "itemtype": "Item/Page/Article", "published": "2015-11-03T00:00:00Z", "title": "Test Markdown Document"}'  # noqa

# attribution and rights are fallbacks for items with missing metadata
siteconfig = {
    "timezone": pytz.utc,
    "attribution": [{"role": "author", "name": "Vince Veselosky"}],
    "rights": {"copyright_notice": "Copyright 2016 by Vince Veselosky"}
}


def test_to_archetype1():
    archivist = S3archivist(testbucket,
                            s3=mock.Mock(),
                            siteconfig=siteconfig)
    rval = mark.to_archetype(archivist, doc1)
    jsonschema.validate(rval, schema)
    assert rval['Item']['category']['name'] == "test/category"
    assert rval['Item']['attribution'][0]['name'] ==\
        'Vinnie "the Rueben" Veselosky'


def test_to_archetype2():
    archivist = S3archivist(testbucket,
                            s3=mock.Mock(),
                            siteconfig=siteconfig)
    rval = mark.to_archetype(archivist, doc2)
    print(json.dumps(rval))
    jsonschema.validate(rval, schema)
    assert rval['Item']['category']['name'] == "fake/content"
    assert rval['Item']['attribution'][0]['name'] == "Vince Veselosky"


# Given an asset representing a markdown file
# When on_save(asset) is called
# Then on_save returns a list of one asset
# And the asset has a key ending in .json
# And the asset has a contenttype of application/json
# And the asset has correct json (with HTML content)
# And the asset has resourcetype of "archetype"
def test_transform_on_save():
    archivist = S3archivist(testbucket,
                            s3=mock.Mock(),
                            siteconfig=siteconfig)
    asset = archivist.new_resource(key='index.md',
                                   contenttype='text/markdown',
                                   content=doc1.encode('utf-8'))
    rval = mark.on_save(archivist, asset)

    assert len(rval) == 1
    archetype = rval[0]

    # print(archetype.content)
    # print(out)
    # assert archetype.content == out  # Not anymore
    assert archetype.acl == 'public-read'
    assert archetype.contenttype.startswith('application/json')
    assert archetype.resourcetype == 'archetype'
    assert archetype.key.endswith('.json')

