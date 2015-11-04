"""
Translates a Markdown source to a JSON archetype, and also a raw HTML asset.

This Scribe uses Python Markdown, and activates almost all built-in extensions.
Of special note:

* the `toc` extension is configured with `permalink=True`

"""
from __future__ import absolute_import, print_function

import json
import markdown
import pytz

from bluebucket import SmartJSONEncoder, Scribe
from dateutil.parser import parse as parse_date
from markdown.extensions.toc import TocExtension
#from markdown.extensions.wikilinks import WikiLinkExtension
from os import path

extensions=[
    'markdown.extensions.extra',
    'markdown.extensions.admonition',
    'markdown.extensions.codehilite',
    'markdown.extensions.meta',
    'markdown.extensions.sane_lists',
    TocExtension(permalink=True),  # replaces headerId
#    WikiLinkExtension(base_url='', end_url='.html'),
]
# FIXME should get from siteconfig
zone = pytz.timezone('America/New_York')


class MarkdownSource(Scribe):
    accepts_artifacts = [None, 'source']
    accepts_suffixes = ['.markdown', '.md', '.mdown']
    target_suffix  = '.json'
    target_content_type = 'application/json'
    target_artifact = 'archetype'

    md = markdown.Markdown(extensions=extensions, lazy_ol=False,
        output_format='html5')

    def transform(self, body):
        html = self.md.convert(unicode(body))

        # Side-effect: write html fragment to S3 asset
        basepath, ext = path.splitext(self.key)
        fragment_file = basepath + '.htm'
        fragmeta = self.metadata or {}
        fragmeta['artifact'] = 'asset'

        self.s3.put_object(
            Bucket=self.bucket,
            Key=fragment_file,
            ContentType='text/html',
            Body=html,
            Metadata=fragmeta
        )

# The metadata needs a lot of clean up, because:
# 1. meta ext reads everything as a list, but most values should be scalar
# 2. because humans are sloppy, we treat keys as case-insensitive
# 3. because humans are sloppy, we parse and normalize date values
        metadata = self.md.Meta
        metadict = {}
        for key, value in metadata.items():
            if key.lower() in ['date', 'published', 'updated']:
                metadict[key.lower()] = zone.localize(parse_date(value[0]))
            else:
                metadict[key.lower()] = value[0] if len(value) == 1 else value

        return json.dumps(metadict, cls=SmartJSONEncoder, sort_keys=True)


handle_event = MarkdownSource.make_event_handler()

