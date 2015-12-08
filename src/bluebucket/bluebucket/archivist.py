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


class S3archivist(object):
    s3 = None
    bucket = None

    def __init__(self, bucket):
        self.bucket = bucket
        if self.s3 is None:  # tests will mock.patch it, let them
            self.s3 = boto3.client('s3')

    def get(self, filename):
        return self.s3.get_object(Bucket=self.bucket, Key=filename)

    def save(self, filename, contents, contenttype, artifact, metadata=None):
        if metadata is None:
            metadata = {}
        metadata['artifact'] = artifact
        return self.s3.put_object(
            Bucket=self.bucket,
            Key=filename,
            Body=contents,
            ContentType=contenttype,
            Metadata=metadata,
        )

    def delete(self, filename):
        return self.s3.delete_object(Bucket=self.bucket, Key=filename)

