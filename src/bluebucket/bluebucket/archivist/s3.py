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
from __future__ import absolute_import, print_function, unicode_literals
import boto3
from dateutil.parser import parse as parse_date
from io import open
import json
import logging
import pkg_resources
import re
from bluebucket.archivist.base import Archivist, Resource
from bluebucket.pathstrategy import DefaultPathStrategy
from bluebucket.util import gunzip, gzip


logger = logging.getLogger(__name__)


#######################################################################
# Model a stored S3 object
#######################################################################
class S3resource(Resource):
    def __init__(self, **kwargs):
        super(S3resource, self).__init__(**kwargs)
        if not hasattr(self, 'use_compression'):
            self.use_compression = True

    @classmethod
    def from_s3object(cls, obj, **kwargs):
        b = cls(**kwargs)
        b.last_modified = obj.get('LastModified')  # boto3 gives a datetime
        b.contenttype = obj.get('ContentType')
        # NOTE reflects compressed size if compressed
        b.content_length = obj.get('ContentLength')
        b.metadata = obj.get('Metadata', {})
        if obj.get('ContentEncoding') == 'gzip':
            b.contentencoding = obj['ContentEncoding']
            b.content = gunzip(obj['Body'].read())
        else:
            try:
                b.content = obj['Body'].read()
            except AttributeError:
                # no read() attr probably means not a real boto3 response, just
                # a json structure resembling it.
                b.content = obj['Body']

        return b

    def as_s3object(self, bucket=None):
        s3obj = dict(
            Bucket=bucket or self.bucket,
            Key=self.key,
            ContentType=self.contenttype,
            Metadata=self.metadata,
        )
        if self.is_compressible():
            s3obj['ContentEncoding'] = 'gzip'
            s3obj['Body'] = gzip(self.content)
        else:
            s3obj['Body'] = self.content
        if self.acl:
            s3obj['ACL'] = self.acl

        return s3obj

    def is_compressible(self):
        yes = r'^text\/|^application\/json|^application\/\w+\+xml'
        return self.use_compression and re.match(yes, self.contenttype)


#######################################################################
# Archive Manager
#######################################################################
# Note that for testing purposes, you can pass both the s3 object and the jinja
# object to the constructor.
class S3archivist(Archivist):

    def __init__(self, bucket, **kwargs):
        self.bucket = bucket
        self.cloudformation = None  # rarely used, only init_bucket
        self.iam = None  # rarely used
        self.pathstrategy = None
        self.s3 = None
        self.siteconfig = None
        self._jinja = None  # See jinja property below
        self._account = None  # See account property
        for key in kwargs:
            if key == 'jinja':
                setattr(self, '_jinja', kwargs[key])
            else:
                setattr(self, key, kwargs[key])

        # If values for these were not provided, perform the (possibly
        # expensive) calculations for the defaults
        if self.s3 is None:
            self.s3 = boto3.client('s3')
        self.region = self.s3.meta.region_name

        if self.pathstrategy is None:
            self.pathstrategy = DefaultPathStrategy()

        if self.siteconfig is None:
            cfg_path = self.pathstrategy.archetype_prefix + 'site.json'
            self.siteconfig = self.get(cfg_path).data

    def get(self, filename):
        reso = S3resource.from_s3object(self.s3.get_object(Bucket=self.bucket,
                                                           Key=filename))
        reso.key = filename
        reso.bucket = self.bucket
        return reso

    def save(self, resource):
        # To be saved a resource must have: key, contenttype, content
        # Strictly speaking, content is not required, but creating an empty
        # object should be explicit, so must pass empty string.
        if resource.key is None:
            raise TypeError("Cannot save resource without key")

        if resource.deleted:
            return self.s3.delete_object(
                Bucket=self.bucket,  # NOTE archivist's bucket, NOT resource's!
                Key=resource.key,
            )

        if resource.contenttype is None:
            raise TypeError("Cannot save resource without contenttype")
        if resource.content is None:
            raise TypeError("""To save an empty resource, set content to an empty
                            bytestring""")
        if resource.resourcetype == 'artifact' and not resource.archetype_guid:
            raise ValueError("""Resources of type artifact must contain an
                             archetype_guid""")

        s3obj = resource.as_s3object(self.bucket)
        return self.s3.put_object(**s3obj)
        # TODO On successful put, send SNS message to onSaveArtifact
        # Since artifacts do not have a fixed path prefix or suffix, we cannot
        # ask S3 to send notifications automatically, so we send them manually
        # here.

    def publish(self, resource):
        "Same as save, but ensures the resource is publicly readable."
        resource.acl = 'public-read'
        self.save(resource)

    def persist(self, resourcelist):
        for resource in resourcelist:
            self.save(resource)

    def delete(self, filename):
        return self.s3.delete_object(Bucket=self.bucket, Key=filename)

    def new_resource(self, key, **kwargs):
        return S3resource(bucket=self.bucket, key=key, **kwargs)

    @property
    def account(self):
        if not self._account:
            # There's no direct way to discover the account id, but it is part of
            # the ARN of the user, so we get the current user and parse it out.
            iam = self.iam or boto3.client('iam')
            resp = iam.get_user()
            # 'arn:aws:iam::128119582937:user/vince'
            m = re.match(r'arn:aws:iam::(\d+):.*', resp["User"]["Arn"])
            self._account =  m.group(1)
        return self._account

    @property
    def jinja(self):
        if self._jinja:
            return self._jinja
        from jinja2 import Environment
        from jinja2_s3loader import S3loader
        template_dir = self.siteconfig.get('template_dir', '_templates')
        self._jinja = Environment(loader=S3loader(self.bucket,
                                                  template_dir,
                                                  s3=self.s3))
        return self._jinja

    def all_archetypes(self):
        "A generator function that will yield every archetype resource."
        # S3 will return up to 1000 items in a list_objects call. If there are
        # more, IsTruncated will be True and NextMarker is the offset to use to
        # get the next 1000.
        incomplete = True
        marker = None
        while incomplete:
            args = dict(Bucket=self.bucket,
                        Prefix=self.pathstrategy.archetype_prefix)
            if marker:
                args['Marker'] = marker
            listing = self.s3.list_objects(**args)
            for item in listing['Contents']:
                resource = self.get(item['Key'])
                yield resource
            if listing['IsTruncated']:
                marker = listing['NextMarker']
            else:
                incomplete = False

    def init_bucket(self):
        "Initialize a bucket and create a cloudformation stack for it."
        # To be absolutely certain that cloudformation will not delete customer
        # data from the bucket, we leave the bucket out of the stack entirely,
        # create it separately and pass it in as a parameter to the stack.

        # Create bucket if necessary
        s3 = self.s3
        bucket = self.bucket
        region = self.region
        account = self.account
        try:
            s3.head_bucket(Bucket=bucket)
            logger.info("Bucket already exists, modifying: %s" % bucket)
        except Exception as e:
            if "404" not in str(e):
                raise
            s3.create_bucket(
                Bucket=bucket,
                CreateBucketConfiguration={'LocationConstraint': self.region}
            )
            logger.info("Creating bucket: %s" % bucket)

        # Use Cloudformation to create a "stack" that contains all the
        # non-bucket resources the system needs. Stack creation happens in the
        # background so we get it started early and then do the rest of our
        # synchronous calls.
        cf_file = pkg_resources.resource_filename('bluebucket.archivist',
                                                  'cloudformation.json')
        with open(cf_file, encoding="utf-8") as f:
            stackdef = f.read()
        # Calculate the stack name based on the bucket name
        # starter = re.sub(r'[^A-Za-z0-9]+', '-', bucket.lower())
        stack_name = "WebQuills" + ''.join(s.capitalize() for s in bucket.split('.'))

        # Check if the stack already exists. If yes, maybe update needed.
        cf = self.cloudformation or boto3.client('cloudformation',
                                                 region_name=self.region)
        try:
            resp = cf.describe_stacks(StackName=stack_name)
            stack_exists = len(resp['Stacks']) > 0
        except Exception as e:
            if "does not exist" not in str(e):
                raise
            stack_exists = False

        if stack_exists:  # exists, update
            logger.info("Updating cloudformation stack: %s" % stack_name)
            try:
                cf.update_stack(StackName=stack_name,
                                TemplateBody=stackdef,
                                Capabilities=['CAPABILITY_IAM'],
                                Parameters=[
                                    {
                                        "ParameterKey": "BucketNameParameter",
                                        "ParameterValue": bucket,
                                    },
                                    {
                                        "ParameterKey": "BucketArnParameter",
                                        "ParameterValue": "arn:aws:s3:::" + bucket,
                                    }
                                ]
                                )
                waiter = cf.get_waiter("stack_update_complete")
            except Exception as e:
                if "No updates" not in str(e):
                    raise
                logger.info("No updates needed for: %s" % stack_name)
                waiter = cf.get_waiter("stack_exists")

        else:  # Stack does not exist. Create
            logger.info("Creating cloudformation stack: %s" % stack_name)
            cf.create_stack(StackName=stack_name,
                            TemplateBody=stackdef,
                            Capabilities=['CAPABILITY_IAM'],
                            Parameters=[
                                {
                                    "ParameterKey": "BucketNameParameter",
                                    "ParameterValue": bucket,
                                },
                                {
                                    "ParameterKey": "BucketArnParameter",
                                    "ParameterValue": "arn:aws:s3:::" + bucket,
                                }
                            ]
                            )
            waiter = cf.get_waiter("stack_create_complete")

        # Bucket should exist now. Paint it Blue!
        logger.info("Enabling versioning for bucket: %s" % bucket)
        s3.put_bucket_versioning(
            Bucket=bucket,
            VersioningConfiguration={
                'MFADelete': 'Disabled',
                'Status': 'Enabled'
            }
        )
        logger.info("Enabling website serving for bucket: %s" % bucket)
        s3.put_bucket_website(
            Bucket=bucket,
            WebsiteConfiguration={
                'IndexDocument': {
                    'Suffix': 'index.html'
                }
            }
        )

        # PUT site.json
        # TODO check for existing config, don't overwrite. Or maybe update?
        logger.info("Writing site config to bucket: %s" % bucket)
        site_config_key = self.pathstrategy.path_for(resourcetype='config',
                                                     key='site.json')
        site_config = self.new_resource(resourcetype='config',
                                        key=site_config_key,
                                        contenttype='application/json',
                                        data=self.siteconfig
                                        )
        self.publish(site_config)

        # TODO PUT Schema files

        # Cannot configure notifications until the destinations have been
        # created by cloudformation.
        logger.info("Waiting for cloudformation stack: %s" % stack_name)
        waiter.wait(StackName=stack_name)

        # Configure Event Sources to send to SNS Topics for this bucket.
        # For this, I need the ARNs for the topics in question. Sigh. Since topic
        # ARNs have a consistent naming pattern, I'm hard coding this. But we need a
        # more generic way to connect these.
        logger.info("Adding S3 notifications to SNS for: %s" % bucket)
        arn_pattern = ":".join(["arn:aws:sns", region, account, stack_name])
        topic_save_source_markdown = arn_pattern + "-on-save-source-text-markdown"
        topic_remove_source_markdown = arn_pattern + "-on-remove-source-text-markdown"
        topic_save_article = arn_pattern + "-on-save-item-page-article"
        topic_remove_article = arn_pattern + "-on-remove-item-page-article"
        topic_save_catalog = arn_pattern + "-on-save-item-page-catalog"
        topic_remove_catalog = arn_pattern + "-on-remove-item-page-catalog"

        s3.put_bucket_notification_configuration(
            Bucket=bucket,
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
                    },
                    {
                        "Id": "webquills-on-save-item-page-catalog",
                        "TopicArn": topic_save_catalog,
                        "Events": ["s3:ObjectCreated:*"],
                        "Filter": {
                            "Key": {
                                "FilterRules": [{"Name": "prefix", "Value":
                                                "_A/Item/Page/Catalog/"}]
                            }
                        }
                    },
                    {
                        "Id": "webquills-on-remove-item-page-catalog",
                        "TopicArn": topic_remove_catalog,
                        "Events": ["s3:ObjectRemoved:DeleteMarkerCreated"],
                        "Filter": {
                            "Key": {
                                "FilterRules": [{"Name": "prefix", "Value":
                                                "_A/Item/Page/Catalog/"}]
                            }
                        }
                    }
                ]
            }
        )


#######################################################################
# S3 Events
#######################################################################
class S3event(object):
    def __init__(self, event=None, **kwargs):
        self.event = event or {"s3": {"object": {}, "bucket": {}}, }
        for key in kwargs:
            setattr(self, key, kwargs[key])

    @property
    def bucket(self):
        return self.event['s3']['bucket']['name']

    @bucket.setter
    def bucket(self, newval):
        self.event['s3']['bucket']['name'] = newval

    @property
    def datetime(self):
        "The event time as a datetime object, rather than a string."
        return parse_date(self.time)

    @property
    def etag(self):
        return self.event['s3']['object']['eTag']

    @etag.setter
    def etag(self, newval):
        self.event['s3']['object']['eTag'] = newval

    @property
    def is_save_event(self):
        return 'ObjectCreated' in self.name

    @property
    def key(self):
        return self.event['s3']['object']['key']

    @key.setter
    def key(self, newval):
        self.event['s3']['object']['key'] = newval

    @property
    def name(self):
        return self.event['eventName']

    @name.setter
    def name(self, newval):
        self.event['eventName'] = newval

    @property
    def region(self):
        return self.event['awsRegion']

    @region.setter
    def region(self, newval):
        self.event['awsRegion'] = newval

    @property
    def sequencer(self):
        return self.event['s3']['object']['sequencer']

    @sequencer.setter
    def sequencer(self, newval):
        self.event['s3']['object']['sequencer'] = newval

    @property
    def source(self):
        return self.event['eventSource']

    @source.setter
    def source(self, newval):
        self.event['eventSource'] = newval

    @property
    def time(self):
        return self.event['eventTime']

    @time.setter
    def time(self, newval):
        self.event['eventTime'] = newval

    def as_json(self):
        "Returns a serialized JSON string of the S3 event"
        return json.dumps(self.event)


def parse_aws_event(message, **kwargs):
    eventlist = message['Records']
    events = []
    for event in eventlist:
        if 'eventSource' in event and event['eventSource'] == 'aws:s3':
            events.append(S3event(event))
        elif "EventSource" in event and event['EventSource'] == "aws:sns":
            try:
                unwrapped = json.loads(event['Sns']['Message'])
                ev_list = unwrapped['Records']
            except Exception:
                logger.error(json.dumps(event))
                raise
            for ev in ev_list:
                if 'eventSource' in ev and ev['eventSource'] == 'aws:s3':
                    events.append(S3event(ev))
        else:
            # Event from elsewhere. Log it.
            logger.warn("Unrecognized event message:\n%s" %
                        json.dumps(message, sort_keys=True))
            return []

    return events
