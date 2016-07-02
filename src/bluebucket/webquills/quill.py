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
from datetime import datetime
from docopt import docopt
from io import open
from os import path
from slugify import slugify
from webquills.scribe.markdown import to_archetype

import boto3
import logging
import json
import pytz
import sys
import uuid


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
stopwords = ['a', 'an', 'the']
item_types = {
    'article': 'Item/Page/Article'
}
webquills_roles = {}


# Utility function to get the role details for webquills roles.
def get_roles():
    iam = boto3.client('iam')
    resp = iam.list_roles(PathPrefix='/webquills/')
    for role in resp['Roles']:
        if 'Scribe' in role['RoleName']:
            webquills_roles['scribe'] = role

    return webquills_roles


def permit_bucket_publish(bucket, topic_arn, region):
    # Permit this bucket to publish to this SNS topic.
    sns = boto3.client('sns', region_name=region)
    resp = sns.get_topic_attributes(TopicArn=topic_arn)
    policy = json.loads(resp['Attributes']['Policy'])
    for statement in policy['Statement']:
        if 'Sid' not in statement:
            continue
        if statement['Sid'] == bucket:
            logger.info("bucket has permission to publish to topic %s" %
                        topic_arn)
            break
    else:
        logger.info("Updating policy for bucket access to topic %s" %
                    topic_arn)
        policy['Statement'].append({
            "Sid": bucket,
            "Effect": "Allow",
            "Principal": {"AWS": "*"},
            "Action": "sns:Publish",
            "Resource": topic_arn,
            "Condition": {
                "ArnEquals": {
                    "aws:SourceArn": "arn:aws:s3:::" + bucket
                }
            }
        })
        sns.set_topic_attributes(
            TopicArn=topic_arn,
            AttributeName="Policy",
            AttributeValue=json.dumps(policy)
        )


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
        metas.append('slug: %s' % slugify(title, stopwords=stopwords))
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
    # Create bucket if necessary
    s3 = boto3.client('s3', region_name=region)
    try:
        s3.head_bucket(Bucket=archivist.bucket)
        logger.info("Bucket already exists, modifying: %s" % archivist.bucket)
    except Exception as e:
        if "404" not in str(e):
            raise
        s3.create_bucket(
            Bucket=archivist.bucket,
            CreateBucketConfiguration={'LocationConstraint': region}
        )
        logger.info("Creating bucket: %s" % archivist.bucket)
    # Bucket should exist now. Paint it Blue!
    logger.info("Enabling versioning for bucket: %s" % archivist.bucket)
    s3.put_bucket_versioning(
        Bucket=archivist.bucket,
        VersioningConfiguration={
            'MFADelete': 'Disabled',
            'Status': 'Enabled'
        }
    )
    # TODO Custom ErrorDocument?
    logger.info("Enabling website serving for bucket: %s" % archivist.bucket)
    s3.put_bucket_website(
        Bucket=archivist.bucket,
        WebsiteConfiguration={
            'IndexDocument': {
                'Suffix': 'index.html'
            }
        }
    )
    # TODO Should we also enable CORS by default?

    # Add read-write permission on the bucket to the webquills-scribe role.
    # Since Cloudformation does not allow me to name the role, we'll need to
    # search for it. NIEE. See get_roles above.
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
    logger.info("Granting Scribes permissions on bucket: %s" % archivist.bucket)
    roles = get_roles()
    iam.put_role_policy(
        RoleName=roles['scribe']['RoleName'],
        PolicyName='webquills-scribe-s3-%s' % archivist.bucket,
        PolicyDocument=json.dumps(policy_doc)
    )
    # PUT site.json
    logger.info("Writing site config to bucket: %s" % archivist.bucket)
    site_config_key = archivist.pathstrategy.path_for(resourcetype='config',
                                                      key='site.json')
    site_config = archivist.new_resource(resourcetype='config',
                                         key=site_config_key,
                                         contenttype='application/json',
                                         data=archivist.siteconfig
                                         )
    archivist.publish(site_config)

    # TODO PUT Schema files

    # Configure Event Sources to send to SNS Topics for this bucket.
    # For this, I need the ARNs for the topics in question. Sigh. Since topic
    # ARNs have a consistent naming pattern, I'm hard coding this. But we need a
    # more generic way to connect these.
    logger.info("Adding S3 notifications to SNS for: %s" % archivist.bucket)
    arn_pattern = "arn:aws:sns:%(region)s:%(account)s:%(topic)s"

    # Markdown Source events
    topic_save_source_markdown = arn_pattern % {
        "region": region,
        "account": account,
        "topic": "webquills-on-save-source-text-markdown"
    }
    permit_bucket_publish(archivist.bucket, topic_save_source_markdown, region)

    topic_remove_source_markdown = arn_pattern % {
        "region": region,
        "account": account,
        "topic": "webquills-on-remove-source-text-markdown"
    }
    permit_bucket_publish(archivist.bucket, topic_remove_source_markdown,
                          region)

    topic_save_article = arn_pattern % {
        "region": region,
        "account": account,
        "topic": "webquills-on-save-item-page-article"
    }
    permit_bucket_publish(archivist.bucket, topic_save_article, region)

    topic_remove_article = arn_pattern % {
        "region": region,
        "account": account,
        "topic": "webquills-on-remove-item-page-article"
    }
    permit_bucket_publish(archivist.bucket, topic_remove_article, region)

    s3.put_bucket_notification_configuration(
        Bucket=archivist.bucket,
        NotificationConfiguration={
            "TopicConfigurations": [
                {
                    "Id": "webquills-on-save-source-text-markdown",
                    "TopicArn": topic_save_source_markdown,
                    "Events": ["s3:ObjectCreated:*"],
                    "Filter": {
                        "Key": {
                            "FilterRules": [{"Name": "prefix", "Value":
                                             "_A/Source/text/markdown/"}]
                        }
                    }
                },
                {
                    "Id": "webquills-on-remove-source-text-markdown",
                    "TopicArn": topic_remove_source_markdown,
                    "Events": ["s3:ObjectRemoved:DeleteMarkerCreated"],
                    "Filter": {
                        "Key": {
                            "FilterRules": [{"Name": "prefix", "Value":
                                             "_A/Source/text/markdown/"}]
                        }
                    }
                },
                {
                    "Id": "webquills-on-save-item-page-article",
                    "TopicArn": topic_save_article,
                    "Events": ["s3:ObjectCreated:*"],
                    "Filter": {
                        "Key": {
                            "FilterRules": [{"Name": "prefix", "Value":
                                             "_A/Item/Page/Article/"}]
                        }
                    }
                },
                {
                    "Id": "webquills-on-remove-item-page-article",
                    "TopicArn": topic_remove_article,
                    "Events": ["s3:ObjectRemoved:DeleteMarkerCreated"],
                    "Filter": {
                        "Key": {
                            "FilterRules": [{"Name": "prefix", "Value":
                                             "_A/Item/Page/Article/"}]
                        }
                    }
                }
            ]
        }
    )


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

