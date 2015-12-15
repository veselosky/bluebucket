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
import posixpath as path

from bluebucket.archivist import S3asset
from bluebucket.scribe import Scribe
from bluebucket.util import SmartJSONEncoder
from dateutil.parser import parse as parse_date
import markdown
from markdown.extensions.toc import TocExtension
import pytz

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

    md = markdown.Markdown(extensions=extensions, lazy_ol=False,
                           output_format='html5')

    def on_save(self, asset):
        if not self.can_handle_path(asset.key):
            return []

        basepath, ext = path.splitext(asset.key)

        html = self.md.convert(asset.text)
        fragpath = basepath + '.htm'
        contenttype = 'text/html; charset=utf-8'
        fragment = self.archivist.new_asset(key=fragpath,
                                            contenttype=contenttype,
                                            content=html,
                                            artifact='curio')

# The metadata needs a lot of clean up, because:
# 1. meta ext reads everything as a list, but most values should be scalar
# 2. because humans are sloppy, we parse and normalize date values
        metadata = self.md.Meta
        metadict = {}
        timezone = self.siteconfig.get('timezone', pytz.utc)
        for key, value in metadata.items():
            if key in ['date', 'published', 'updated']:
                metadict[key] = timezone.localize(parse_date(value[0]))
            else:
                metadict[key] = value[0] if len(value) == 1 else value

        # Since content is in separate file, add content_src to reference it.
        href = 'http://' + path.join(self.archivist.bucket, fragpath)
        metadict['content_src'] = {'bucket': self.archivist.bucket,
                                   'key': fragpath,
                                   'href': href,
                                   'type': 'text/html; charset=utf-8',
                                   }
        content = json.dumps(metadict, cls=SmartJSONEncoder, sort_keys=True)
        archetype = S3asset(key=basepath + '.json',
                            contenttype='application/json',
                            content=content,
                            artifact='archetype')

        return [fragment, archetype]

    def on_delete(self, key):
        if not self.can_handle_path(key):
            return []

        basepath, ext = path.splitext(key)
        html = S3asset(key=basepath + '.htm', deleted=True)
        arch = S3asset(key=basepath + '.json', deleted=True)
        return [html, arch]

