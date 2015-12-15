# vim: set fileencoding=utf-8 :
#
#   Copyright 2015 Vince Veselosky and contributors
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

from bluebucket.archivist import S3asset, S3archivist
from bluebucket.markdownsource import MarkdownSource


doc = b"""Title: Test Markdown Document
Date: 2015-11-03

This is a test of the emergency markdown system.
If this were an actual markdown,
it would be more interesting.
"""

postdoc = u'''<p>This is a test of the emergency markdown system.
If this were an actual markdown,
it would be more interesting.</p>'''

out = u'{"content_src": {"bucket": "bluebucket.mindvessel.net", "href": "http://bluebucket.mindvessel.net/index.htm", "key": "index.htm", "type": "text/html; charset=utf-8"}, "date": "2015-11-03T00:00:00Z", "title": "Test Markdown Document"}'  # noqa


# Given an asset representing a markdown file
# When on_save(asset) is called
# Then on_save returns a list of two assets
# And the first asset has a key ending in .htm
# And the first asset has correctly transformed content
# And the first asset has artifact of "curio"
# And the second asset has a key ending in .json
# And the second asset has correct json
# And the second asset has artifact of "archetype"
@mock.patch.object(S3archivist, 's3')
def test_transform_on_save(mocks3):
    archivist = S3archivist('bluebucket.mindvessel.net')
    md = MarkdownSource(archivist=archivist, siteconfig={'timezone': pytz.utc})
    asset = S3asset(key='index.md',
                    contenttype='text/markdown',
                    content=doc)

    rval = md.on_save(asset)

    assert len(rval) == 2

    html, archetype = rval
    assert html.content == postdoc
    assert html.contenttype.startswith('text/html')
    assert html.key == 'index.htm'
    assert html.artifact == 'curio'

    assert archetype.content == out
    assert archetype.contenttype.startswith('application/json')
    assert archetype.key == 'index.json'
    assert archetype.artifact == 'archetype'


# Given an asset representing a non-markdown file
# When on_save(asset) is called
# Then on_save returns an empty list
@mock.patch.object(S3archivist, 's3')
def test_on_save_cannot_handle(mocks3):
    archivist = S3archivist('testbucket1')
    md = MarkdownSource(archivist=archivist)
    asset = S3asset(key='index.txt',
                    contenttype='text/plain',
                    content=doc)

    rval = md.on_save(asset)

    assert len(rval) == 0


# Given a key representing a markdown file
# When on_delete(key) is called
# Then on_delete returns a list of two assets
# And the first asset has a key ending in .htm
# And the first asset has deleted flag set
# And the second asset has a key ending in .json
# And the second asset has deleted flag set
@mock.patch.object(S3archivist, 's3')
def test_on_delete(mocks3):
    archivist = S3archivist('testbucket1')
    md = MarkdownSource(archivist=archivist)

    rval = md.on_delete('index.markdown')

    assert len(rval) == 2

    html, archetype = rval
    assert html.key == 'index.htm'
    assert html.deleted
    assert archetype.key == 'index.json'
    assert archetype.deleted


# Given a key representing a non-markdown file
# When on_delete(key) is called
# Then on_delete returns an empty list
@mock.patch.object(S3archivist, 's3')
def test_on_delete_cannot_handle(mocks3):
    archivist = S3archivist('testbucket1')
    md = MarkdownSource(archivist=archivist)

    rval = md.on_delete('index.htm')

    assert len(rval) == 0
