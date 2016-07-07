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
import json
import logging
import re
from bluebucket.pathstrategy import DefaultPathStrategy
from bluebucket.util import SmartJSONEncoder, gunzip, gzip
from pytz import timezone


logger = logging.getLogger(__name__)


def inflate_config(config):
    """Takes a bare decoded JSON dict and creates Python objects from certain
    keys"""
    tz = config.get('timezone', 'America/New_York')
    config['timezone'] = tz if hasattr(tz, 'utcoffset') else timezone(tz)
    # Your transformation here
    return config


#######################################################################
# Model a stored S3 object
#######################################################################
class S3resource(object):
    def __init__(self, **kwargs):
        self.acl = None
        self.bucket = None
        self.content = None
        self.contenttype = None
        self.contentencoding = None
        self.deleted = False
        self.encoding = 'utf-8'
        self.key = None
        self.last_modified = None
        self.metadata = kwargs.pop("metadata", {})
        self.use_compression = True

        for key in kwargs:
            setattr(self, key, kwargs[key])

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

    @property
    def resourcetype(self):
        return self.metadata.get("resourcetype")

    @resourcetype.setter
    def resourcetype(self, newval):
        self.metadata['resourcetype'] = newval

    @property
    def archetype_guid(self):
        return self.metadata.get("archetype_guid")

    @archetype_guid.setter
    def archetype_guid(self, newval):
        self.metadata['archetype_guid'] = newval

    @property
    def text(self):
        if self.contenttype.startswith('text/'):
            return self.content.decode(self.encoding)
        else:
            raise ValueError("Only text/* MIME types have a text property")

    @text.setter
    def text(self, newtext):
        self.content = newtext.encode(self.encoding)

    @property
    def data(self):
        return json.loads(self.content.decode(self.encoding))

    @data.setter
    def data(self, newdata):
        # dumper only outputs ascii chars, so this should be safe
        self.content = json.dumps(newdata, cls=SmartJSONEncoder, sort_keys=True)

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
class S3archivist(object):

    def __init__(self, bucket, **kwargs):
        self.bucket = bucket
        self.archetype_prefix = '_A/'
        self.index_prefix = '_I/'
        self.s3 = None
        self.siteconfig = None
        self.pathstrategy = DefaultPathStrategy()
        self._jinja = None  # See jinja property below
        for key in kwargs:
            if key == 'jinja':
                setattr(self, '_jinja', kwargs[key])
            else:
                setattr(self, key, kwargs[key])

        # If values for these were not provided, perform the (possibly
        # expensive) calculations for the defaults
        if self.s3 is None:
            self.s3 = boto3.client('s3')

        if self.siteconfig is None:
            cfg_path = self.archetype_prefix + 'site.json'
            self.siteconfig = inflate_config(self.get(cfg_path).data)

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
            args = dict(Bucket=self.bucket, Prefix=self.archetype_prefix)
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
