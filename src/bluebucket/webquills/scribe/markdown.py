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


def to_archetype(archivist, text):
    "Given text in markdown format, returns a dict of metadata and body text."
    timezone = archivist.siteconfig.get('timezone', pytz.utc)
    html = md.convert(text)

    metadata = md.Meta
    itemmeta = {}
    for key, value in metadata.items():
        if key in ['created', 'date', 'published', 'updated']:
            # because humans are sloppy, we parse and normalize date values
            dt = parse_date(value[0])
            if dt.tzinfo:
                dt = dt.astimezone(timezone)
            else:
                dt = timezone.localize(dt)
            itemmeta[key] = dt.isoformat()
        elif key == 'author':
            itemmeta["attribution"] = [{"role": "author", "name":
                                        metadata[key][0]}]
        elif key == "copyright":
            itemmeta["rights"] = {"copyright_notice": metadata[key][0]}
        elif key.startswith("rights."):
            if "rights" not in itemmeta:
                itemmeta["rights"] = {}
            itemmeta["rights"][key[7:]] = metadata[key][0]
        elif key == "category":
            itemmeta["category"] = {"name": metadata[key][0]}
        else:
            # reads everything as list, but most values should be scalar
            itemmeta[key] = value[0] if len(value) == 1 else value

    # itemmeta needs a self-referencing archetype key.
    key = archivist.pathstrategy.path_for(resourcetype='archetype', **itemmeta)
    self_link = {
        "bucket": archivist.bucket,
        "key": key,
        "href": key
    }
    itemmeta['archetype'] = self_link
    itemmeta['contenttype'] = "text/html; charset=utf-8"
    if "itemtype" not in itemmeta:
        itemmeta["itemtype"] = "Item/Page/Article"
    if "published" not in itemmeta:
        itemmeta["published"] = itemmeta["updated"]
    if "updated" not in itemmeta:
        itemmeta["updated"] = itemmeta["published"]

    # Some metadata has fallback defaults from the siteconfig
    if "rights" not in itemmeta:
        itemmeta["rights"] = archivist.siteconfig.get("rights")
    if "attribution" not in itemmeta:
        itemmeta["attribution"] = archivist.siteconfig.get("attribution")

    archetype = {"Item": itemmeta, "Item/Page/Article": {"body": html}}
    return archetype


def on_save(archivist, resource):
    metadict = to_archetype(archivist, resource.text)
    archetype = archivist.new_resource(key=metadict['Item']['archetype']['key'],
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

