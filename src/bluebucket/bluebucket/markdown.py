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
from bluebucket.util import SmartJSONEncoder, change_ext
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
accepts_suffixes = ['.markdown', '.md', '.mdown']
md = markdown.Markdown(extensions=extensions, lazy_ol=False,
                       output_format='html5')


def on_save(archivist, asset):

    html = md.convert(asset.text)

    metadata = md.Meta
    metadict = {}
    timezone = archivist.siteconfig.get('timezone', pytz.utc)
    for key, value in metadata.items():
        if key in ['date', 'published', 'updated']:
            # because humans are sloppy, we parse and normalize date values
            metadict[key] = timezone.localize(parse_date(value[0]))
        else:
            # reads everything as list, but most values should be scalar
            metadict[key] = value[0] if len(value) == 1 else value

    metadict['_content'] = html
    content = json.dumps(metadict, cls=SmartJSONEncoder, sort_keys=True)
    archetype = archivist.new_asset(key=change_ext(asset.key, '.json'),
                                    contenttype='application/json',
                                    content=content,
                                    resourcetype='archetype')

    return [archetype]


def on_delete(archivist, key):
    arch = archivist.new_asset(key=change_ext(key, '.json'), deleted=True)
    return [arch]

