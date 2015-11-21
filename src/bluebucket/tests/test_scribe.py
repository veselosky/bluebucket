# vim: set fileencoding=utf-8 :
# Test cases for Scribe
from __future__ import print_function, unicode_literals

import copy
import datetime
import logging
import mock

from bluebucket import Scribe
from dateutil.tz import tzutc

logging.basicConfig(level=logging.INFO)

###############################################################################
# Test the handle_event logic that dispatches to the specific event handling
# methods. This performs checks against the event itself, without any S3 I/O.
###############################################################################
class ScribeTest(Scribe):
    accepts_suffixes = ['.html']
    accepts_artifacts = [None]
    target_artifact = 'asset'
    target_content_type = 'text/plain'
    target_suffix = '.txt'
    s3 = 'to be mocked out by tests'

    def transform(self, body):
        return body


handle_event = ScribeTest.make_event_handler()
bucket = "bluebucket.mindvessel.net"
key = "index.html"
good_event = {
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
          "key": key,
          "size": 1024
        },
        "bucket": {
          "arn": "arn:aws:s3:::bluebucket.mindvessel.net",
          "name": bucket,
          "ownerIdentity": {
            "principalId": "EXAMPLE"
          }
        },
        "s3SchemaVersion": "1.0"
      },
      "responseElements": {
        "x-amz-id-2": "EXAMPLE123/5678abcdefghijklambdaisawesome/mnopqrstuvwxyzABCDEFGH",
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


# Happy path
# eventType is objectCreated
@mock.patch.object(ScribeTest, 'on_ignore')
@mock.patch.object(ScribeTest, 'on_delete')
@mock.patch.object(ScribeTest, 'on_save')
def test_good_event(on_save, on_delete, on_ignore):
    resp = ScribeTest.make_event_handler()(good_event, {})

    on_save.assert_called_with()
    assert on_delete.called == False
    assert on_ignore.called == False

# eventSource not aws:s3
@mock.patch.object(ScribeTest, 'on_ignore')
@mock.patch.object(ScribeTest, 'on_delete')
@mock.patch.object(ScribeTest, 'on_save')
def test_bad_event_source(on_save, on_delete, on_ignore):
    bad_event_source = copy.deepcopy(good_event)
    bad_event_source['Records'][0]['eventSource'] = 'not s3'
    
    resp = ScribeTest.make_event_handler()(bad_event_source, {})

    on_ignore.assert_called_with()
    assert on_delete.called == False
    assert on_save.called == False

# object key does not match accepts_suffixes
@mock.patch.object(ScribeTest, 'on_ignore')
@mock.patch.object(ScribeTest, 'on_delete')
@mock.patch.object(ScribeTest, 'on_save')
def test_bad_object_suffix(on_save, on_delete, on_ignore):
    bad_object_suffix = copy.deepcopy(good_event)
    bad_object_suffix['Records'][0]['s3']['object']['key'] = 'test.jpg'

    resp = ScribeTest.make_event_handler()(bad_object_suffix, {})

    on_ignore.assert_called_with()
    assert on_delete.called == False
    assert on_save.called == False

# Edge case: object key does not have a suffix, should compare empty string
@mock.patch.object(ScribeTest, 'on_ignore')
@mock.patch.object(ScribeTest, 'on_delete')
@mock.patch.object(ScribeTest, 'on_save')
def test_no_object_suffix(on_save, on_delete, on_ignore):
    no_object_suffix = copy.deepcopy(good_event)
    no_object_suffix['Records'][0]['s3']['object']['key'] = 'testWithoutExtension'

    resp = ScribeTest.make_event_handler()(no_object_suffix, {})

    on_ignore.assert_called_with()
    assert on_delete.called == False
    assert on_save.called == False

# * eventType is objectRemoved
@mock.patch.object(ScribeTest, 'on_ignore')
@mock.patch.object(ScribeTest, 'on_delete')
@mock.patch.object(ScribeTest, 'on_save')
def test_object_removed(on_save, on_delete, on_ignore):
    object_removed = copy.deepcopy(good_event)
    object_removed['Records'][0]['eventName'] = 'ObjectRemoved:Delete'

    resp = ScribeTest.make_event_handler()(object_removed, {})

    on_delete.assert_called_with()
    assert on_ignore.called == False
    assert on_save.called == False

# * eventType is somethingElse
@mock.patch.object(ScribeTest, 'on_ignore')
@mock.patch.object(ScribeTest, 'on_delete')
@mock.patch.object(ScribeTest, 'on_save')
def test_unknown_event(on_save, on_delete, on_ignore):
    unknown_event = copy.deepcopy(good_event)
    unknown_event['Records'][0]['eventName'] = 'ReducedRedundancyLostObject'

    resp = ScribeTest.make_event_handler()(unknown_event, {})

    on_ignore.assert_called_with()
    assert on_delete.called == False
    assert on_save.called == False


###############################################################################
# Test the individual event handlers. For this we need to mock an S3 object
# with get_object, put_object, and delete_object methods.
###############################################################################

# saving for later, will need to mock out several versions
s3get_response = {
    u'AcceptRanges': 'bytes',
    u'Body': b'This is the content body',
    u'ContentLength': 702,
    u'ContentType': 'application/json',
    u'ETag': '"ad668d6d0dd7cd4fadd7b3dcf92355aa"',
    u'LastModified': datetime.datetime(2015, 10, 24, 21, 28, 51, tzinfo=tzutc()),
    u'Metadata': {'artifact': 'asset'},
    'ResponseMetadata': {
        'HTTPStatusCode': 200,
        'HostId': 'P7ndnrWmNBDnBwwiwNGodgDxohWTQyM0gP7ikcuKQJ+ZAU4XMcVGX9yy0rX0H+vVWKZwWHADadQ=',
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

# Happy path for delete: target object exists and matches target_artifact
def test_on_delete_matches_artifact():
    object_removed = copy.deepcopy(good_event)
    object_removed['Records'][0]['eventName'] = 'ObjectRemoved:Delete'
    mocks3 = mock.Mock()
    mocks3.get_object.return_value = s3get_response
    mocks3.delete_object.return_value = s3delete_response

    with mock.patch.object(ScribeTest, 's3', mocks3):
        retval = ScribeTest.make_event_handler()(object_removed, {})

    mocks3.get_object.assert_called_with(Bucket=bucket, Key='index.txt')
    mocks3.delete_object.assert_called_with(Bucket=bucket, Key='index.txt')


# Target exists but artifact does not match target_artifact
def test_on_delete_does_not_match_artifact():
    object_removed = copy.deepcopy(good_event)
    object_removed['Records'][0]['eventName'] = 'ObjectRemoved:Delete'
    response = copy.deepcopy(s3get_response)
    response['Metadata']['artifact'] = 'monograph'
    mocks3 = mock.Mock()
    mocks3.get_object.return_value = response

    with mock.patch.object(ScribeTest, 's3', mocks3):
        retval = ScribeTest.make_event_handler()(object_removed, {})

    mocks3.get_object.assert_called_with(Bucket=bucket, Key='index.txt')
    assert mocks3.delete_object.called == False


# Target for delete does not exist in the bucket
def test_on_delete_object_missing():
    object_removed = copy.deepcopy(good_event)
    object_removed['Records'][0]['eventName'] = 'ObjectRemoved:Delete'
    mocks3 = mock.Mock()
    mocks3.get_object.side_effect = Exception("NoSuchKey")

    with mock.patch.object(ScribeTest, 's3', mocks3):
        retval = ScribeTest.make_event_handler()(object_removed, {})

    mocks3.get_object.assert_called_with(Bucket=bucket, Key='index.txt')
    assert mocks3.delete_object.called == False


# Happy path for save: source artifact matches accepts_artifacts
def test_on_save_artifact_matches():
    response = copy.deepcopy(s3get_response)
    response['Metadata'] = {}
    mocks3 = mock.Mock()
    mocks3.get_object.return_value = response

    with mock.patch.object(ScribeTest, 's3', mocks3):
        retval = ScribeTest.make_event_handler()(good_event, {})

    mocks3.get_object.assert_called_with(Bucket=bucket, Key=key)
    mocks3.put_object.assert_called_with(
        Bucket=bucket,
        Key='index.txt',
        ContentType=ScribeTest.target_content_type,
        Body=response['Body'],
        Metadata={'artifact': ScribeTest.target_artifact}
    )
    assert mocks3.delete_object.called == False

# source artifact does not match accepts_artifacts
def test_on_save_does_not_match_artifact():
    mocks3 = mock.Mock()
    mocks3.get_object.return_value = s3get_response

    with mock.patch.object(ScribeTest, 's3', mocks3):
        retval = ScribeTest.make_event_handler()(good_event, {})

    mocks3.get_object.assert_called_with(Bucket=bucket, Key=key)
    assert mocks3.delete_object.called == False
    assert mocks3.put_object.called == False


