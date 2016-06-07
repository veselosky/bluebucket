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
AssumeRolePolicyDoc = {
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Principal": {
                "Service": "lambda.amazonaws.com"
            },
            "Action": "sts:AssumeRole"
        }
    ]
}
#: The WebquillsScribePolicyDoc describes all the permissions granted to Scribe
#: Lambda functions. It is assigned to the webquills-scribe role.
WebquillsScribePolicyDoc = {
    "Version": "2012-10-17",
    "Statement": [
        {
            "Action": [
                "logs:CreateLogGroup",
                "logs:CreateLogStream",
                "logs:PutLogEvents"
            ],
            "Effect": "Allow",
            "Resource": "arn:aws:logs:*:*:*"
        },
        {
            "Effect": "Allow",
            "Action": ["sns:Publish", "sns:Receive", "sns:Subscribe"],
            "Resource": "arn:aws:sns:*:*:webquills-*"
        }
    ]
}
Topics = [
    "webquills-on-save-source-text-markdown",
    "webquills-on-remove-source-text-markdown",
    "webquills-on-save-item-page-article",
    "webquills-on-remove-item-page-article",
    "webquills-on-save-artifact",
    "webquills-on-remove-artifact"
]


def aws_update(region, account):
    "Install or update core functions and SNS Topics for WebQuills"
    # ensure we have our Lambda execution role
    iam = boto3.client("iam", region_name=region)
    resp = iam.list_roles(PathPrefix='/webquills/')
    if len(resp['Roles']) < 1:
        print("Creating role for webquills-scribe")
        resp = iam.create_role(
            Path='/webquills/',
            RoleName='webquills-scribe',
            AssumeRolePolicyDocument=json.dumps(AssumeRolePolicyDoc)
        )
    else:
        for role in resp['Roles']:
            print('Found role %s' % role['RoleName'])

    # Don't bother checking, just update. Unlikely to throttle at this rate.
    print("Updating policy for role webquills-scribe")
    iam.put_role_policy(
        RoleName='webquills-scribe',
        PolicyName='webquills-scribe-general-policy',
        PolicyDocument=json.dumps(WebquillsScribePolicyDoc)
    )

    # Create or update the policies that grant permissions to our functions
    # arn:aws:iam::account-id:policy/policy-name
    # Fucking hell this managed policy shit is complicated!
    # TODO Switching to inline policies for now. Fix later.
#    arn = 'arn:aws:iam::%s:policy/webquills/webquills-scribe' % account
#    try:
#        resp = iam.list_policy_versions(PolicyArn=arn)
#    except Exception as e:
#        if "NoSuchEntity" in str(e):
#            print("Creating policy for webquills-scribe")
#            resp = iam.create_policy(
#                PolicyName="webquills-scribe",
#                Path="/webquills/",
#                PolicyDocument=json.dumps(WebquillsScribePolicyDoc),
#                Description="Policy for WebQuills Scribe Lambda functions"
#            )
#        else:
#            raise
#    for version in resp['Versions']:
#        if version['IsDefaultVersion']:
#            latest = version['VersionId']
#            break
#    else:
#        latest = None
#    if latest:
#        resp = iam.get_policy_version(PolicyArn=arn, VersionId=latest)
#        print(repr(resp))
#        if WebquillsScribePolicyDoc != resp['PolicyVersion']['Document']:
#            print("Updating policy for webquills-scribe")
#        else:
#            print("Policy for webquills-scribe is up to date!")

    # Accounts can have thousands of topics, but the listTopics call can only
    # return 100 at a time. Rather than paginate forever, we just try to
    # recreate them. The create method is idempotent, so it succeeds if the
    # topic already exists.
    sns = boto3.client("sns", region_name=region)
    for topic in Topics:
        print("Ensuring SNS Topic exists: %s" % topic)
        resp = sns.create_topic(Name=topic)

    # TODO Create or update Lambda functions


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

