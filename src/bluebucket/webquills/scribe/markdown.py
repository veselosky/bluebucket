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
import json
import markdown
from markdown.extensions.toc import TocExtension
import pytz
import string

from bluebucket.archivist import parse_aws_event, S3archivist
from bluebucket.util import slugify


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


# markdown normalizes all meta keys to lower case, but keys for AWS are
# case-sensitive. Since we want to pass this query structure direct to AWS, we
# need to correct the case of the keys.
def fixup_query(query):
    structured_vals = [
        "exclusivestartkey",
        "expressionattributenames",
        "expressionattributevalues"
    ]
    correct = {
        "tablename": "TableName",
        "consistentread": "ConsistentRead",
        "exclusivestartkey": "ExclusiveStartKey",
        "expressionattributenames": "ExpressionAttributeNames",
        "expressionattributevalues": "ExpressionAttributeValues",
        "filterexpression": "FilterExpression",
        "indexname": "IndexName",
        "keyconditionexpression": "KeyConditionExpression",
        "limit": "Limit",
        "projectionexpression": "ProjectionExpression",
        "returnconsumedcapacity": "ReturnConsumedCapacity",
        "scanindexforward": "ScanIndexForward",
        "select": "Select"
    }
    new_query = {}
    for key in query:
        if key in structured_vals:
            new_query[correct[key]] = json.loads(query[key])
        else:
            new_query[correct[key]] = query[key]

    return new_query


def to_archetype(archivist, text):
    "Given text in markdown format, returns a dict of metadata and body text."
    timezone = archivist.siteconfig.get('timezone', pytz.utc)
    html = md.convert(text)

    metadata = md.Meta
    itemmeta = {}
    catalogmeta = {}
    # Here we implement some special case transforms for data that may need
    # cleanup or is hard to encode using markdown's simple format.
    for key, value in metadata.items():
        if key in ['created', 'date', 'published', 'updated']:
            # because humans are sloppy, we parse and normalize date values
            dt = parse_date(value[0])
            if dt.tzinfo:
                dt = dt.astimezone(timezone)
            else:
                dt = timezone.localize(dt)
            if key == 'date':  # Legacy DC.date, convert to specific
                key == 'published'
            itemmeta[key] = dt.isoformat()

        elif key == 'itemtype':
            itemmeta['itemtype'] = string.capwords(metadata['itemtype'][0], '/')

        elif key == 'author':
            itemmeta["attribution"] = [{"role": "author", "name":
                                        metadata[key][0]}]

        elif key == "copyright":  # Typical usage provides only notice
            itemmeta["rights"] = {"copyright_notice": metadata[key][0]}
        elif key.startswith("rights-"):
            if "rights" not in itemmeta:
                itemmeta["rights"] = {}
            itemmeta["rights"][key[7:]] = metadata[key][0]

        elif key == "category":  # Typical usage provides only name
            itemmeta["category"] = {"name": metadata[key][0]}
        elif key.startswith("category-"):
            if "category" not in itemmeta:
                itemmeta["category"] = {}
            itemmeta["category"][key[9:]] = metadata[key][0]

        elif key.startswith("query-"):
            if "query" not in catalogmeta:
                catalogmeta["query"] = {}
            catalogmeta["query"][key[6:]] = metadata[key][0]

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
    if "slug" not in itemmeta:
        itemmeta["slug"] = slugify(itemmeta["title"])
    if "published" not in itemmeta:
        itemmeta["published"] = itemmeta["updated"]
    if "updated" not in itemmeta:
        itemmeta["updated"] = itemmeta["published"]

    # Some metadata has fallback defaults from the siteconfig
    if "rights" not in itemmeta:
        itemmeta["rights"] = archivist.siteconfig.get("rights")
    if "attribution" not in itemmeta:
        itemmeta["attribution"] = archivist.siteconfig.get("attribution")

    archetype = {"Item": itemmeta, "Item_Page_Article": {"body": html}}
    if itemmeta['itemtype'].startswith('Item/Page/Catalog'):
        catalogmeta['query'] = fixup_query(catalogmeta['query'])
        archetype['Item_Page_Catalog'] = catalogmeta
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

