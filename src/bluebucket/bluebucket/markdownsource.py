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
"""
Translates a Markdown source to a JSON archetype, and also a raw HTML asset.

This Scribe uses Python Markdown, and activates almost all built-in extensions.
Of special note:

* the `toc` extension is configured with `permalink=True`

"""
from __future__ import absolute_import, print_function

import json
import markdown

from bluebucket import SmartJSONEncoder, Scribe
from dateutil.parser import parse as parse_date
from markdown.extensions.toc import TocExtension
from os import path

extensions = [
    'markdown.extensions.extra',
    'markdown.extensions.admonition',
    'markdown.extensions.codehilite',
    'markdown.extensions.meta',
    'markdown.extensions.sane_lists',
    TocExtension(permalink=True),  # replaces headerId
]


class MarkdownSource(Scribe):
    accepts_artifacts = [None, 'source']
    accepts_suffixes = ['.markdown', '.md', '.mdown']
    target_suffix = '.json'
    target_content_type = 'application/json'
    target_artifact = 'archetype'

    md = markdown.Markdown(extensions=extensions, lazy_ol=False,
                           output_format='html5')

    def transform(self, iostream):
        html = self.md.convert(iostream.read().decode('utf-8'))

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
# 2. because humans are sloppy, we parse and normalize date values
        metadata = self.md.Meta
        metadict = {}
        for key, value in metadata.items():
            if key in ['date', 'published', 'updated']:
                metadict[key] = self.timezone.localize(parse_date(value[0]))
            else:
                metadict[key] = value[0] if len(value) == 1 else value

        # Since content is in separate file, add content_src to reference it.
        href = 'http://' + path.join(self.bucket, fragment_file)
        metadict['content_src'] = {'bucket': self.bucket,
                                   'key': fragment_file,
                                   'href': href,
                                   'type': 'text/html',
                                   }
        return json.dumps(metadict, cls=SmartJSONEncoder, sort_keys=True)


handle_event = MarkdownSource.make_event_handler()

