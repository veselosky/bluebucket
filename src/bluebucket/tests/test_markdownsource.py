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
from io import BytesIO
import mock

from bluebucket.markdownsource import MarkdownSource


doc = BytesIO(b"""Title: Test Markdown Document
Date: 2015-11-03

This is a test of the emergency markdown system.
If this were an actual markdown,
it would be more interesting.
""")

postdoc = u'''<p>This is a test of the emergency markdown system.
If this were an actual markdown,
it would be more interesting.</p>'''

out = u'{"content_src": {"bucket": "bluebucket.mindvessel.net", "href": "http://bluebucket.mindvessel.net/index.htm", "key": "index.htm", "type": "text/html"}, "date": "2015-11-03T00:00:00-05:00", "title": "Test Markdown Document"}'  # noqa


# Because transform writes an asset as a side-effect, need to mock out the
# s3 module.
@mock.patch.object(MarkdownSource, 's3')
def test_transform(mocks3):
    # for the siteconfig:
    mocks3.get_object.return_value = {'Body': BytesIO(b'{}')}

    md = MarkdownSource()
    # Normally set by handle_event:
    md.bucket = 'bluebucket.mindvessel.net'
    md.key = 'index.md'

    archetype = md.transform(doc)
    assert archetype == out
    mocks3.put_object.assert_called_with(
        Key='index.htm',
        Body=postdoc,
        Metadata={'artifact': 'asset'},
        ContentType='text/html',
        Bucket='bluebucket.mindvessel.net',
    )

