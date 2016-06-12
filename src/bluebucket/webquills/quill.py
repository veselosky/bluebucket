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
    quill [options] aws-install
    quill [options] init-bucket [options]

Options:
    -b BUCKET, --bucket BUCKET  The S3 bucket to use.
    -r REGION, --region REGION  The AWS region to operate in.
    -a ACCOUNT, --account ACCOUNT  The AWS account ID.
"""
from __future__ import absolute_import, print_function, unicode_literals
from bluebucket.archivist import S3archivist
from bluebucket.markdown import to_archetype
from docopt import docopt
from io import open
from os import path
from slugify import slugify

import boto3
import logging
import json
import sys
import uuid


logger = logging.getLogger(__name__)
stopwords = ['a', 'an', 'the']
item_types = {
    'article': 'Item/Page/Article'
}


# quill new <itemtype> [<title>]
# Generates a new markdown file from a template based on the requested item
# type. Prints to STDOUT, redirect it where you want it. Types supported are
# anything that has a JSON schema in the bluebucket.schemas package. If
# supplied, <title> will be added to the metadata.
def new_markdown(item_type, title=None, **kwargs):
    metas = ['item_type: %s' % item_type, 'guid: %s' % uuid.uuid4()]
    for key in kwargs:
        metas.append('%s: %s' % (key, kwargs[key]))
    if title is not None:
        metas.append('slug: %s' % slugify(title, stopwords=stopwords))
        metas.append('title: %s' % title)
    return "\n".join(metas) + "\n\n"


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
    contentmeta = to_archetype(text)
    assetmeta = {
        'contenttype': 'text/markdown; charset=utf-8',
        'resourcetype': 'asset',
        'acl': 'public-read',
    }
    key = archivist.pathstrategy.path_for(**dict(assetmeta, **contentmeta))
    asset = archivist.new_resource(
        key=key,
        text=text,
        **assetmeta
    )
    archivist.save(asset)


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
    # Create bucket if necessary
    s3 = boto3.client('s3', region_name=region)
    try:
        s3.head_bucket(Bucket=archivist.bucket)
    except Exception as e:
        if "404" not in str(e):
            raise
        s3.create_bucket(
            Bucket=archivist.bucket,
            CreateBucketConfiguration={'LocationConstraint': region}
        )
    # Bucket should exist now. Paint it Blue!
    s3.put_bucket_versioning(
        Bucket=archivist.bucket,
        VersioningConfiguration={
            'MFADelete': 'Disabled',
            'Status': 'Enabled'
        }
    )
    s3.put_bucket_website(
        Bucket=archivist.bucket,
        WebsiteConfiguration={
            'ErrorDocument': {
                'Key': '404.html'
            },
            'IndexDocument': {
                'Suffix': 'index.html'
            },
        }
    )
    # TODO Should we also enable CORS by default?

    # Add permission for S3 to invoke Lambda funcs for that bucket.
    src_scribe = 'webquills-scribe-source-text-markdown-to-archetype'
    lam = boto3.client('lambda', region_name=region)
    lam.add_permission(
        FunctionName=src_scribe,
        StatementId='webquills-scribe-s3-%s' % archivist.bucket,
        Action='lambda:InvokeFunction',
        Principal='s3.amazonaws.com',
        SourceArn="arn:aws:s3:::%s" % archivist.bucket,
        SourceAccount=account
    )

    # Add read-write permission on the bucket to the webquills-scribe role.
    iam = boto3.client('iam', region_name=region)
    policy_doc = {
        "Statement": [
            {
                "Action": [
                    "s3:*"
                ],
                "Effect": "Allow",
                "Resource": [
                    "arn:aws:s3:::%s/*" % archivist.bucket
                ]
            }
        ]
    }
    iam.put_role_policy(
        RoleName='webquills-scribe',
        PolicyName='webquills-scribe-s3-%s' % archivist.bucket,
        PolicyDocument=json.dumps(policy_doc)
    )
    # PUT site.json
    site_config_key = archivist.pathstrategy(resourcetype='config',
                                             key='site.json')
    site_config = archivist.new_resource(resourcetype='config',
                                         key=site_config_key,
                                         acl='public-read',
                                         contenttype='application/json',
                                         json=json.dumps(archivist.siteconfig)
                                         )
    archivist.save(site_config)

    # TODO PUT Schema files
    # Configure Event Sources to send to SNS Topics for this bucket
    pass


# MAIN: Dispatch to individual handlers
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

    elif param['aws-install']:
        aws_update(param['--region'], param['--account'])

    elif param['init-bucket']:
        # FIXME I am ashamed to hard code this stuff, just trying to get DONE.
        sitemeta = {
            "title": "WebQuills: Content Management for Effective Web Sites",
            "google_analytics_id": "UA-642116-5",
        }
        archivist = S3archivist(param['--bucket'], siteconfig=sitemeta)
        init_bucket(archivist, param['--region'], param['--account'])

