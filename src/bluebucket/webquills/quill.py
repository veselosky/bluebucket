# vim: set fileencoding=utf-8 :
#
#   Copyright 2016 Vince Veselosky and contributors
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
WebQuills command line interface.

Usage:
    quill [options] new ITEMTYPE [TITLE]
    quill [options] publish ITEMFILE

Options:
    -b BUCKET, --bucket BUCKET  The S3 bucket to use.
"""
from __future__ import absolute_import, print_function, unicode_literals
from bluebucket.archivist import S3archivist
from bluebucket.markdown import to_archetype
from docopt import docopt
from io import open
from os import path
from slugify import slugify

import logging
import sys
import uuid


logger = logging.getLogger(__name__)
stopwords = ['a', 'an', 'the']
item_types = {
    'article': 'Item/Page/Article'
}


def new_markdown(item_type, title=None, **kwargs):
    metas = ['item_type: %s' % item_type, 'guid: %s' % uuid.uuid4()]
    for key in kwargs:
        metas.append('%s: %s' % (key, kwargs[key]))
    if title is not None:
        metas.append('slug: %s' % slugify(title, stopwords=stopwords))
        metas.append('title: %s' % title)
    return "\n".join(metas) + "\n\n"


def publish(archivist, text):
    contentmeta = to_archetype(text)
    assetmeta = {
        'contenttype': 'text/markdown; charset=utf-8',
        'resourcetype': 'asset',
        'acl': 'public-read',
    }
    key = archivist.pathstrategy.path_for(**dict(assetmeta, **contentmeta))
    asset = archivist.new_asset(
        key=key,
        text=text,
        **assetmeta
    )
    archivist.save(asset)


def main():
    args = []
    if path.exists('webquills.conf'):
        with open('webquills.conf', encoding='utf-8') as f:
            args = f.read().split()
    args.extend(sys.argv[1:])
    logger.debug(repr(args))
    param = docopt(__doc__, argv=args)
    logger.debug(repr(param))

    if param['new']:
        print(new_markdown(item_types[param['ITEMTYPE'].lower()],
                           title=param['TITLE']))
    elif param['publish']:
        archivist = S3archivist(param['--bucket'], siteconfig={})
        with open(param['ITEMFILE'], encoding='utf-8') as f:
            text = f.read()
        publish(archivist, text)


# quill new <itemtype> [<title>]
# Generates a new markdown file from a template based on the requested item
# type. Prints to STDOUT, redirect it where you want it. Types supported are
# anything that has a JSON schema in the bluebucket.schemas package. If
# supplied, <title> will be added to the metadata.

# quill publish <bucket> <itemfile>
# Read <itemfile>, a local markdown file
# Create archivist using <bucket>
# Determine bucket key for file:
#   Extract metadata
#   Call archivist.make_path("source", meta) to determine bucket key.
# archivist.new_asset(markdown_source)
# SAVE (PUT) the asset
# TODO (After preview is implemented) Check for and delete any preview

# quill preview <bucket> <itemfile>
# Same as publish, but PUT to Preview dir.
# Generate and print a pre-signed URL to view the HTML.
