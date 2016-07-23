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
    quill -b BUCKET -r REGION -a ACCOUNT -s CFG aws-install
    quill init-bucket -b BUCKET -r REGION -a ACCOUNT -s CFG
    quill -b BUCKET -s CFG local-init-bucket

Options:
    -b BUCKET, --bucket BUCKET  The bucket name to use.
    -r REGION, --region REGION  The AWS region to operate in.
    -a ACCOUNT, --account ACCOUNT  The AWS account ID.
    -s CFG, --siteconfig CFG  A JSON file containing site configuration for the
        bucket
"""
from __future__ import absolute_import, print_function, unicode_literals
from bluebucket.archivist import S3archivist
from datetime import datetime
from docopt import docopt
from io import open
from os import path
from bluebucket.util import slugify
from webquills.scribe.markdown import to_archetype

import boto3
import logging
import json
import pytz
import sys
import uuid


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
item_types = {
    'article': 'Item/Page/Article'
}


# quill new <itemtype> [<title>]
# Generates a new markdown file from a template based on the requested item
# type. Prints to STDOUT, redirect it where you want it. Types supported are
# anything that has a JSON schema in the bluebucket.schemas package. If
# supplied, <title> will be added to the metadata.
def new_markdown(item_type, title=None, **kwargs):
    # Some defaults
    now = datetime.now()
    # FIXME Timezones are hard. Hard coding for now.
    now = pytz.timezone('America/New_York').localize(now)
    text = ""

    metas = ['itemtype: %s' % item_type, 'guid: %s' % uuid.uuid4()]
    for key in kwargs:
        metas.append('%s: %s' % (key, kwargs[key]))
    if 'created' not in kwargs:
        metas.append('updated: %s' % now.isoformat())
    if 'updated' not in kwargs:
        metas.append('updated: %s' % now.isoformat())
    if 'category' not in kwargs:
        metas.append('category: uncategorized')
        text = text + '''
        For SEO, please assign a keyword-rich category like "keyword/seo" above.
        It will be used to generate a URL.
        '''

    if title:
        metas.append('slug: %s' % slugify(title))
        metas.append('title: %s' % title)
    else:
        metas.append('slug:')
        metas.append('title:')
        text = text + '''
        You need to set a title and slug. Slug will be used to generate a URL.
        '''

    return "\n".join(metas) + "\n\n" + text


# quill publish <bucket> <itemfile>
# Read <itemfile>, a local markdown file
# Create archivist using <bucket>
# Determine bucket key for file:
#   Extract metadata
#   Call archivist.make_path("source", meta) to determine bucket key.
# archivist.new_resource(markdown_source)
# SAVE (PUT) the asset
# TODO (After preview is implemented) Check for and delete any preview
def publish(archivist, text):
    contentmeta = to_archetype(archivist, text)['Item']
    assetmeta = {
        'contenttype': 'text/markdown; charset=utf-8',
        'resourcetype': 'asset',
        'acl': 'public-read',
    }
    key = archivist.pathstrategy.path_for(**dict(contentmeta, **assetmeta))
    asset = archivist.new_resource(
        key=key,
        text=text,
        **assetmeta
    )
    archivist.publish(asset)


# TODO quill preview <bucket> <itemfile>
# Same as publish, but PUT to Preview dir.
# Generate and print a pre-signed URL to view the HTML.


# quill aws-install
# Install the required roles, SNS Topics, and Lambda functions for basic
# publishing functionality.
def aws_update(region, account):
    "Install or update core functions and SNS Topics for WebQuills"
    print("Switched to Cloudformation. Use 'make setup' instead.")


def init_bucket(archivist, region, account):
    archivist.init_bucket()


# MAIN: Dispatch to individual handlers
def main():
    args = []
    if path.exists('webquills.conf'):
        with open('webquills.conf', encoding='utf-8') as f:
            args = f.read().split()
    args.extend(sys.argv[1:])
    logger.debug(repr(args))
    param = docopt(__doc__, argv=args)
    logger.warn(repr(param))

    if param['new']:
        print(new_markdown(item_types[param['ITEMTYPE'].lower()],
                           title=param['TITLE']))
    elif param['publish']:
        archivist = S3archivist(param['--bucket'], siteconfig={})
        with open(param['ITEMFILE'], encoding='utf-8') as f:
            text = f.read()
        publish(archivist, text)

    elif param['aws-install']:
        aws_update(param['--region'], param['--account'])

    elif param['init-bucket']:
        # FIXME I am ashamed to hard code this stuff, just trying to get DONE.
        sitemeta = {
            "google_analytics_id": "UA-642116-5",
            "title": "WebQuills: Content Management for Effective Web Sites",
            "rights": {
                "copyright_notice": "Copyright 2016 Vince Veselosky"
            },
            "attribution": [
                {"role": "author", "name": "Vince Veselosky"}
            ]
        }
        archivist = S3archivist(param['--bucket'], siteconfig=sitemeta)
        init_bucket(archivist, param['--region'], param['--account'])

    elif param['local-init-bucket']:
        # FIXME I am ashamed to hard code this stuff, just trying to get DONE.
        from bluebucket.archivist.local import localarchivist
        sitemeta = {}
        if param['--siteconfig']:
            with open(param['--siteconfig']) as f:
                sitemeta = json.load(f)
        archivist = localarchivist(param['--bucket'], siteconfig=sitemeta)
        archivist.init_bucket()

