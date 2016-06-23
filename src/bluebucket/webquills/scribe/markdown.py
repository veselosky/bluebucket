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

from dateutil.parser import parse as parse_date
import logging
import markdown
from markdown.extensions.toc import TocExtension
import pytz

from bluebucket.archivist import parse_aws_event, S3archivist

logger = logging.getLogger(__name__)
extensions = [
    'markdown.extensions.extra',
    'markdown.extensions.admonition',
    'markdown.extensions.codehilite',
    'markdown.extensions.meta',
    'markdown.extensions.sane_lists',
    TocExtension(permalink=True),  # replaces headerId
]
md = markdown.Markdown(extensions=extensions, lazy_ol=False,
                       output_format='html5')


def to_archetype(text, timezone=pytz.utc):
    "Given text in markdown format, returns a dict of metadata and body text."
    html = md.convert(text)

    metadata = md.Meta
    metadict = {}
    for key, value in metadata.items():
        if key in ['date', 'published', 'updated']:
            # because humans are sloppy, we parse and normalize date values
            metadict[key] = timezone.localize(parse_date(value[0]))
        else:
            # reads everything as list, but most values should be scalar
            metadict[key] = value[0] if len(value) == 1 else value

    metadict['body'] = html
    return metadict


def on_save(archivist, resource):
    timezone = archivist.siteconfig.get('timezone', pytz.utc)
    metadict = to_archetype(resource.text, timezone)
    key = archivist.pathstrategy.path_for(resourcetype='archetype', **metadict)
    archetype = archivist.new_resource(key=key,
                                       data=metadict,
                                       contenttype='application/json',
                                       resourcetype='archetype')
    archivist.publish(archetype)
    return [archetype]


def source_text_mardown_to_archetype(message, context):
    events = parse_aws_event(message)
    if not events:
        logger.warn("No events found in message!\n%s" % message)
    for event in events:
        if event.is_save_event:
            archivist = S3archivist(event.bucket)
            resource = archivist.get(event.key)
            on_save(archivist, resource)
        else:
            logger.warn("Not a save event!\n%s" % event)

