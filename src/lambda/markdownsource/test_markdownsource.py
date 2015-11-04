from markdownsource import MarkdownSource

import mock

doc = b"""Title: Test Markdown Document
Date: 2015-11-03

This is a test of the emergency markdown system. If this were an actual 
markdown, it would be more interesting.
"""

postdoc = u'''<p>This is a test of the emergency markdown system. If this were an actual 
markdown, it would be more interesting.</p>'''

out = u'{"date": "2015-11-03T00:00:00-05:00", "title": "Test Markdown Document"}'

# Because transform writes an asset as a side-effect, need to mock out the
# s3 module.
@mock.patch.object(MarkdownSource, 's3')
def test_transform(mocks3):
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

