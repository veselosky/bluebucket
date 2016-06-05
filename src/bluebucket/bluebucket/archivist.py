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
import json
import posixpath as path
import re
from .util import SmartJSONEncoder, gunzip, gzip
from pytz import timezone


def inflate_config(config):
    """Takes a bare decoded JSON dict and creates Python objects from certain
    keys"""
    tz = config.get('timezone', 'America/New_York')
    config['timezone'] = tz if hasattr(tz, 'utcoffset') else timezone(tz)
    # Your transformation here
    return config


class S3asset(object):
    def __init__(self, **kwargs):
        self.resourcetype = None
        self.bucket = None
        self.content = None
        self.contenttype = None
        self.contentencoding = None
        self.deleted = False
        self.encoding = 'utf-8'
        self.key = None
        self.last_modified = None
        self.metadata = {}
        self.use_compression = True

        for key in kwargs:
            setattr(self, key, kwargs[key])

    @classmethod
    def from_s3object(cls, obj, **kwargs):
        b = cls(**kwargs)
        b.last_modified = obj['LastModified']  # boto3 gives a datetime
        b.contenttype = obj['ContentType']
        # NOTE reflects compressed size if compressed
        b.content_length = obj['ContentLength']
        b.metadata = obj['Metadata']
        b.resourcetype = obj['Metadata']['resourcetype']
        if 'ContentEncoding' in obj and obj['ContentEncoding'] == 'gzip':
            b.contentencoding = obj['ContentEncoding']
            b.content = gunzip(obj['Body'].read())
        else:
            b.content = obj['Body'].read()
        return b

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
        self.content = json.dumps(newdata, cls=SmartJSONEncoder)

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
        return s3obj

    def is_compressible(self):
        yes = r'^text\/|^application\/json|^application\/\w+\+xml'
        return self.use_compression and re.match(yes, self.contenttype)


# Note that for testing purposes, you can pass both the s3 object and the jinja
# object to the constructor.
class S3archivist(object):

    def __init__(self, bucket, **kwargs):
        self.bucket = bucket
        self.archetype_prefix = '/_A/'
        self.index_prefix = '/_I/'
        self.s3 = None
        self.siteconfig = None
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
            self.siteconfig = inflate_config(self.get('bluebucket.json').data)

    def get(self, filename):
        return S3asset.from_s3object(self.s3.get_object(Bucket=self.bucket,
                                                        Key=filename))

    def save(self, asset):
        # To be saved an asset must have: key, contenttype, content
        # Strictly speaking, content is not required, but creating an empty
        # object should be explicit, so must pass empty string.
        if asset.key is None:
            raise TypeError("Cannot save asset without key")

        if asset.deleted:
            return self.s3.delete_object(
                Bucket=self.bucket,  # NOTE archivist's bucket, NOT asset's!
                Key=asset.key,
            )

        if asset.contenttype is None:
            raise TypeError("Cannot save asset without contenttype")
        if asset.content is None:
            raise TypeError("""To save an empty asset, set content to an empty
                            bytestring""")
        asset.metadata['resourcetype'] = asset.resourcetype
        s3obj = asset.as_s3object(self.bucket)
        return self.s3.put_object(**s3obj)

    def persist(self, assetlist):
        for asset in assetlist:
            self.save(asset)

    def delete(self, filename):
        return self.s3.delete_object(Bucket=self.bucket, Key=filename)

    def new_asset(self, key, **kwargs):
        if kwargs.get('resourcetype', None) == 'archetype':
            if not key.startswith(self.archetype_prefix):
                key = path.join(self.archetype_prefix, key)
        elif kwargs.get('resourcetype', None) == 'index':
            if not key.startswith(self.index_prefix):
                key = path.join(self.index_prefix, key)

        return S3asset(bucket=self.bucket, key=key, **kwargs)

    def unprefix(self, key):
        "Remove the archetype or index prefix from a key."
        if key.startswith(self.archetype_prefix):
            key = key[len(self.archetype_prefix):]
        elif key.startswith(self.index_prefix):
            key = key[len(self.index_prefix):]
        return key

    @property
    def jinja(self):
        if self._jinja:
            return self._jinja
        from jinja2 import Environment
        from jinja2_s3loader import S3loader
        template_dir = self.siteconfig.get('template_dir', '_templates')
        self._jinja = Environment(loader=S3loader(self.bucket, template_dir))
        return self._jinja

    def all_archetypes(self):
        "A generator function that will yield every archetype asset."
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
                asset = self.get(item['Key'])
                yield asset
            if listing['IsTruncated']:
                marker = listing['NextMarker']
            else:
                incomplete = False
