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
from io import BytesIO
import datetime

from dateutil.tz import tzutc

__all__ = ["text_content", "json_content", "binary_content",
           "s3get_response_binary", "s3get_response_json",
           "s3get_response_text_utf8", "s3put_response", "s3delete_response"]

# saving for later, will need to mock out several versions
text_content = u'¡This string contains unicode — touché!'
json_content = b'{"type":"json"}'
binary_content = b'cmFuZG9tIHN0cmluZyB5b3UgY2FuIHJlYWQ=\n'
testable_datetime = datetime.datetime(2015, 10, 24, 21, 28, 51, tzinfo=tzutc())


def s3get_response_text_utf8():
    return {
        u'AcceptRanges': 'bytes',
        u'Body': BytesIO(text_content.encode('utf-8')),
        u'ContentLength': 43,
        u'ContentType': 'text/plain; charset=utf-8',
        u'ETag': '"ad668d6d0dd7cd4fadd7b3dcf92355aa"',
        u'LastModified': testable_datetime,
        u'Metadata': {'artifact': 'asset'},
        'ResponseMetadata': {
            'HTTPStatusCode': 200,
            'HostId': 'P7ndnrWmNBDnBwwiwNGodgDxohWTQyM0gP7ikcuKQJ+ZAU4XMcVGXr=',
            'RequestId': '665ED7B91C453AD6'
        },
        u'VersionId': '_9pHD0t9Su1DA9xIpipMZJyXgYBdU6.v'
    }


def s3get_response_json():
    return {
        u'AcceptRanges': 'bytes',
        u'Body': BytesIO(json_content),
        u'ContentLength': 15,
        u'ContentType': 'application/json',
        u'ETag': '"ad668d6d0dd7cd4fadd7b3dcf92355aa"',
        u'LastModified': testable_datetime,
        u'Metadata': {'artifact': 'asset'},
        'ResponseMetadata': {
            'HTTPStatusCode': 200,
            'HostId': 'P7ndnrWmNBDnBwwiwNGodgDxohWTQyM0gP7ikcuKQJ+ZAU4XMcVGX9=',
            'RequestId': '665ED7B91C453AD6'
        },
        u'VersionId': '_9pHD0t9Su1DA9xIpipMZJyXgYBdU6.v'
    }


def s3get_response_binary():
    return {
        u'AcceptRanges': 'bytes',
        u'Body': BytesIO(binary_content),
        u'ContentLength': 37,
        u'ContentType': 'application/octet-stream',
        u'ETag': '"ad668d6d0dd7cd4fadd7b3dcf92355aa"',
        u'LastModified': testable_datetime,
        u'Metadata': {'artifact': 'asset'},
        'ResponseMetadata': {
            'HTTPStatusCode': 200,
            'HostId': 'P7ndnrWmNBDnBwwiwNGodgDxohWTQyM0gP7ikcuKQJ+ZAU4XMcVGX9=',
            'RequestId': '665ED7B91C453AD6'
        },
        u'VersionId': '_9pHD0t9Su1DA9xIpipMZJyXgYBdU6.v'
    }


s3put_response = {
    'ETag': 'string',
    'VersionId': 'string',
}
s3delete_response = {
    'DeleteMarker': True,
    'VersionId': 'string',
}


# For a list of supported "method" params:
# https://docs.aws.amazon.com/AmazonS3/latest/dev/NotificationHowTo.html#supported-notification-event-types
def generate_event(bucket="bluebucket.mindvessel.net", key="index.html",
                   method="ObjectCreated:Put", source="aws:s3"):
    return {"Records": [
        {"eventVersion": "2.0",
         "eventTime": "1970-01-01T00:00:00.000Z",
         "requestParameters": {"sourceIPAddress": "127.0.0.1"},
         "s3": {
             "configurationId": "testConfigRule",
             "object": {
                 "eTag": "0123456789abcdef0123456789abcdef",
                 "sequencer": "0A1B2C3D4E5F678901",
                 "key": key,
                 "size": 1024
             },
             "bucket": {
                 "arn": "arn:aws:s3:::" + bucket,
                 "name": bucket,
                 "ownerIdentity": {
                     "principalId": "EXAMPLE"
                 }
             },
             "s3SchemaVersion": "1.0"
         },
         "responseElements": {
             "x-amz-id-2": "EXAMPLE123/5678abcdefghijk/mnopqrstuvwxyzABCDEFGH",
             "x-amz-request-id": "EXAMPLE123456789"
         },
         "awsRegion": "us-east-1",
         "eventName": method,
         "userIdentity": {
             "principalId": "EXAMPLE"
         },
         "eventSource": source
         }
    ]
    }


def archivist():
    pass
