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
import mock

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
        u'Metadata': {'resourcetype': 'asset'},
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
        u'Metadata': {'resourcetype': 'asset'},
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
        u'Metadata': {'resourcetype': 'asset'},
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


def fake_scribe(on_save=None, on_delete=None):
    scribe = mock.Mock()
    if on_save is not None:
        if isinstance(on_save, Exception):
            scribe.on_save.side_effect = on_save
        else:
            scribe.on_save.return_value = on_save
    if on_delete is not None:
        if isinstance(on_delete, Exception):
            scribe.on_delete.side_effect = on_delete
        else:
            scribe.on_delete.return_value = on_delete
    return scribe


def fake_archivist(get=None):
    arch = mock.Mock()
    if get is None:
        arch.mock.get.return_value = s3get_response_text_utf8()
    elif isinstance(get, Exception):
        arch.mock.get.side_effect = get
    else:
        arch.mock.get.return_value = get

    return arch


s3eventsource = {
    "Records": [
        {
            "eventVersion": "2.0",
            "eventTime": "1970-01-01T00:00:00.000Z",
            "requestParameters": {
                "sourceIPAddress": "127.0.0.1"
            },
            "s3": {
                "configurationId": "testConfigRule",
                "object": {
                    "eTag": "0123456789abcdef0123456789abcdef",
                    "sequencer": "0A1B2C3D4E5F678901",
                    "key": "HappyFace.jpg",
                    "size": 1024
                },
                "bucket": {
                    "arn": "arn:aws:s3:::mybucket",
                    "name": "sourcebucket",
                    "ownerIdentity": {
                        "principalId": "EXAMPLE"
                    }
                },
                "s3SchemaVersion": "1.0"
            },
            "responseElements": {
                "x-amz-id-2": "EXAMPLE123/5678abcdefghijklambdaisawesome/mnop",
                "x-amz-request-id": "EXAMPLE123456789"
            },
            "awsRegion": "us-east-1",
            "eventName": "ObjectCreated:Put",
            "userIdentity": {
                "principalId": "EXAMPLE"
            },
            "eventSource": "aws:s3"
        }
    ]
}

sns_event = {
    "Records": [
        {
            "EventSource": "aws:sns",
            "EventSubscriptionArn": "arn:aws:sns:us-east-1:128119582937:webquills-on-save-source-text-markdown:82fd1d18-992d-4ec9-af3f-d90e5da1339e",
            "EventVersion": "1.0",
            "Sns": {
                "Message": "{\"Records\":[{\"eventVersion\":\"2.0\",\"eventSource\":\"aws:s3\",\"awsRegion\":\"us-east-1\",\"eventTime\":\"2016-06-23T03:02:47.174Z\",\"eventName\":\"ObjectCreated:Put\",\"userIdentity\":{\"principalId\":\"AWS:AIDAJVCTAKX7F6CQKUGIA\"},\"requestParameters\":{\"sourceIPAddress\":\"50.234.95.35\"},\"responseElements\":{\"x-amz-request-id\":\"AC43D5B771346F7E\",\"x-amz-id-2\":\"47ZDk9F7s1O7dZMqRd4XqHld7Bymibmc17FCobxVMaUB2ztbV8RdQOIdy+kF4cp6QBXI7XW2qy8=\"},\"s3\":{\"s3SchemaVersion\":\"1.0\",\"configurationId\":\"webquills-on-save-source-text-markdown\",\"bucket\":{\"name\":\"bluebucket.mindvessel.net\",\"ownerIdentity\":{\"principalId\":\"A2QB6MXE2Q7NFP\"},\"arn\":\"arn:aws:s3:::bluebucket.mindvessel.net\"},\"object\":{\"key\":\"_A/Source/text/markdown/02eb3153-6d45-4c96-8bcb-f7da85e69624.md\",\"size\":285,\"eTag\":\"bad92d984b68414a501e2f82fb7b7aa7\",\"versionId\":\"AIt1zwgyp_wBNEUMDA5nGcbhSHDjHFIb\",\"sequencer\":\"00576B5156F1106F82\"}}}]}",
                "MessageAttributes": {},
                "MessageId": "d6f0f15b-166c-51d5-b870-bebe45fbdf16",
                "Signature": "Sw9wlbPdI33csAYH+m1S52SILzUxH2QIYWieiLRHlR16+QSl1AU9jeC2vvmoYXLy9mhpjM4VV0gz5zpcNqEzS8vrD+DJsSP9A5Px41+yK+KnLeV+vgyuXTrZK4W7JlOO9ZbpMQEvxA2LApFD5pJAGz355QbrfFF3NMStfrhDQW0xCnVv+T2bUtg3U1EpUXjIN4Quk11zeEZq4GyRliDRI64G4Mf5a3EojnHe/J7ng9mk024jZbpgHV2TcM4xe2WFP6GgdF2MUc+cCs8DlvQCfRP42ANiCpGzIkmEoI5OwA4VK0Z6bONe+Rksr/BmQLpsSGH4dUCDlIweQmL82ErUjQ==",
                "SignatureVersion": "1",
                "SigningCertUrl": "https://sns.us-east-1.amazonaws.com/SimpleNotificationService-bb750dd426d95ee9390147a5624348ee.pem",
                "Subject": "Amazon S3 Notification",
                "Timestamp": "2016-06-23T03:02:47.333Z",
                "TopicArn": "arn:aws:sns:us-east-1:128119582937:webquills-on-save-source-text-markdown",
                "Type": "Notification",
                "UnsubscribeUrl": "https://sns.us-east-1.amazonaws.com/?Action=Unsubscribe&SubscriptionArn=arn:aws:sns:us-east-1:128119582937:webquills-on-save-source-text-markdown:82fd1d18-992d-4ec9-af3f-d90e5da1339e"
            }
        }
    ]
}
