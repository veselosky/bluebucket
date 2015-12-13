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

import boto3
import json


class S3Asset(object):
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
        if self.content_type.startswith('text/'):
            return self.content.decode(self.encoding)
        else:
            raise ValueError("Only text/* MIME types have a text property")

    @property
    def json(self):
        return json.loads(self.content.decode(self.encoding))


class S3archivist(object):
    s3 = None
    bucket = None

    def __init__(self, bucket):
        self.bucket = bucket
        if self.s3 is None:  # tests will mock.patch it, let them
            self.s3 = boto3.client('s3')

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
        return self.s3.put_object(
            Bucket=self.bucket,  # NOTE archivist's bucket, NOT asset's!
            Key=asset.key,
            Body=asset.content,  # TODO gzip content if compressable
            ContentType=asset.contenttype,
            Metadata=asset.metadata,
        )

    def delete(self, filename):
        return self.s3.delete_object(Bucket=self.bucket, Key=filename)

    def s3object_to_asset(self, s3object, **kwargs):
        b = S3Asset(**kwargs)
        b.last_modified = s3object['LastModified']  # boto3 gives a datetime
        b.content_type = s3object['ContentType']
        # NOTE reflects compressed size if compressed
        b.content_length = s3object['ContentLength']
        b.metadata = s3object['Metadata']
        b.artifact = s3object['Metadata']['artifact']
        # TODO ungzip content if compressed
        b.content = s3object['Body'].read()
        return b

    def new_asset(self, key=None, **kwargs):
        return S3Asset(bucket=self.bucket, key=key, **kwargs)

