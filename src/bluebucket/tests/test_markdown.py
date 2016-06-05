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
import mock
import pytz

from bluebucket.archivist import S3archivist
import bluebucket.markdown as mark

testbucket = 'bluebucket.mindvessel.net'

doc = """Title: Test Markdown Document
Date: 2015-11-03

¿Dónde esta el baño?
"""

out = b'{"body": "<p>\u00bfD\u00f3nde esta el ba\u00f1o?</p>", "date": "2015-11-03T00:00:00Z", "title": "Test Markdown Document"}'  # noqa


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
                            siteconfig={'timezone': pytz.utc})
    asset = archivist.new_asset(key='index.md',
                                contenttype='text/markdown',
                                content=doc.encode('utf-8'))
    rval = mark.on_save(archivist, asset)

    assert len(rval) == 1
    archetype = rval[0]

    print(archetype.content)
    print(out)
    assert archetype.content == out
    assert archetype.contenttype.startswith('application/json')
    assert archetype.resourcetype == 'archetype'
    assert archetype.key.endswith('index.json')


# Given a key representing a markdown file
# When on_delete(key) is called
# Then on_delete returns a list of one asset
# And the asset has deleted flag set
# And the asset has a key ending in .json
def test_on_delete():
    archivist = S3archivist(testbucket,
                            s3=mock.Mock(),
                            siteconfig={'timezone': pytz.utc})
    rval = mark.on_delete(archivist, 'index.markdown')

    assert len(rval) == 1
    archetype = rval[0]
    assert archetype.key == 'index.json'
    assert archetype.deleted

