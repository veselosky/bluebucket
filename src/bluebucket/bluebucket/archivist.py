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
from __future__ import absolute_import, print_function, unicode_literals
import json
import boto3
from bluebucket.util import SmartJSONEncoder


class S3asset(object):
    artifact = None
    bucket = None
    content = None
    contenttype = None
    deleted = False
    encoding = 'utf-8'
    key = None
    last_modified = None
    metadata = None

    def __init__(self, **kwargs):
        for key in kwargs:
            setattr(self, key, kwargs[key])
        if self.metadata is None:
            self.metadata = {}

    @property
    def text(self):
        if self.contenttype.startswith('text/'):
            return self.content.decode(self.encoding)
        else:
            raise ValueError("Only text/* MIME types have a text property")

    @text.setter
    def text(self, newtext):
        self.content = newtext.decode(self.encoding)

    @property
    def data(self):
        return json.loads(self.content.decode(self.encoding))

    @data.setter
    def data(self, newdata):
        # dumper only outputs ascii chars, so this should be safe
        self.content = json.dumps(newdata, cls=SmartJSONEncoder)


# Note that for testing purposes, you can pass both the s3 object and the jinja
# object to the constructor.
class S3archivist(object):

    def __init__(self, bucket, **kwargs):
        self.bucket = bucket
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

        # FIXME siteconfig needs some post-processing to upgrade things to
        # python objects (e.g. timezone).
        if self.siteconfig is None:
            self.siteconfig = self.get('_bluebucket.json').data

    def get(self, filename):
        return self.s3object_to_asset(self.s3.get_object(Bucket=self.bucket,
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
        asset.metadata['artifact'] = asset.artifact
        s3obj = dict(
            Bucket=self.bucket,  # NOTE archivist's bucket, NOT asset's!
            Key=asset.key,
            Body=asset.content,  # TODO gzip content if compressable
            ContentType=asset.contenttype,
            Metadata=asset.metadata,
        )
        return self.s3.put_object(s3obj)

    def persist(self, assetlist):
        for asset in assetlist:
            self.save(asset)

    def delete(self, filename):
        return self.s3.delete_object(Bucket=self.bucket, Key=filename)

    def s3object_to_asset(self, s3object, **kwargs):
        b = S3asset(**kwargs)
        b.last_modified = s3object['LastModified']  # boto3 gives a datetime
        b.contenttype = s3object['ContentType']
        # NOTE reflects compressed size if compressed
        b.content_length = s3object['ContentLength']
        b.metadata = s3object['Metadata']
        b.artifact = s3object['Metadata']['artifact']
        # TODO ungzip content if compressed
        b.content = s3object['Body'].read()
        return b

    def new_asset(self, key=None, **kwargs):
        return S3asset(bucket=self.bucket, key=key, **kwargs)

    @property
    def jinja(self):
        if self._jinja:
            return self._jinja
        from jinja2 import Environment
        from jinja2_s3loader import S3loader
        template_dir = self.siteconfig.get('template_dir', '_templates')
        self._jinja = Environment(loader=S3loader(self.bucket, template_dir))
        return self._jinja
