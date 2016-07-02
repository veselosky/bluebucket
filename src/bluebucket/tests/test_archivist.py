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

# The S3 Archivist is a simplified wrapper around S3.
from __future__ import absolute_import, print_function, unicode_literals
try:
    import mock
except ImportError:
    import unittest.mock as mock

import json
from pytz import timezone

from bluebucket.archivist import S3archivist, S3resource, S3event
from bluebucket.archivist import inflate_config, parse_aws_event
from bluebucket.util import gzip
import stubs
import pytest

contenttype = 'text/plain; charset=utf-8'
testbucket = 'test-bucket'


###########################################################################
# Archivist creating Asset objects
###########################################################################

# Given an archivist
# When I call archivist.new_resource(key)
# A new asset is returned
# and the asset's bucket attribute has the same value as the archivist's
# and the asset's key attribute is set with the argument
def test_new_resource_with_key():
    arch = S3archivist(testbucket, s3=mock.Mock(), siteconfig={})
    asset = arch.new_resource('test.key')
    assert asset.bucket == testbucket
    assert asset.key == 'test.key'


# Given an archivist
# When I call archivist.new_resource(key, **kwargs)
# A new asset is returned
# and the asset's attributes have been set by the kwargs
def test_new_resource_with_kwargs():
    arch = S3archivist(testbucket, s3=mock.Mock(), siteconfig={})
    asset = arch.new_resource('test.key', deleted=True)
    assert asset.deleted is True


###########################################################################
# Archivist get
###########################################################################

# Given a bucket
# When get() is called with a filename
# Then archivist calls s3.get_object with correct params
# And the returned object has its key and bucket attributes set
# Should we support conditional GET with If-None-Match, If-Modified-Since?
def test_get_by_key():
    arch = S3archivist(testbucket, s3=mock.Mock(), siteconfig={})
    arch.s3.get_object.return_value = stubs.s3get_response_text_utf8()
    resource = arch.get('filename.txt')

    arch.s3.get_object.assert_called_with(
        Key='filename.txt',
        Bucket=testbucket,
    )
    assert resource.key == 'filename.txt'
    assert resource.bucket == arch.bucket


# Given a bucket
# When get() is called without a filename
# Then archivist raises TypeError
def test_get_no_filename():
    arch = S3archivist(testbucket, s3=mock.Mock(), siteconfig={})
    with pytest.raises(TypeError):
        arch.get()


###########################################################################
# Archivist delete_object
###########################################################################

# Given a bucket
# When delete() is called with a filename
# Then archivist calls s3.delete_object with correct params
# According to the docs, AMZ does not support If-Match conditions
# on delete, so other args are ignored.
# https://docs.aws.amazon.com/AmazonS3/latest/API/RESTObjectDELETE.html
def test_delete_by_key():
    arch = S3archivist(testbucket, s3=mock.Mock(), siteconfig={})
    arch.delete('filename.txt')

    arch.s3.delete_object.assert_called_with(
        Key='filename.txt',
        Bucket=testbucket,
    )


# Given a bucket
# When delete() is called without a filename
# Then archivist raises TypeError
def test_delete_no_filename():
    arch = S3archivist(testbucket, s3=mock.Mock(), siteconfig={})
    with pytest.raises(TypeError):
        arch.delete()


###########################################################################
# Archivist save
###########################################################################

# Given a bucket
# When save() is called with all required params
# Then archivist calls s3.put_object with correct params
def test_save_success():
    arch = S3archivist(testbucket, s3=mock.Mock(), siteconfig={})
    asset = arch.new_resource('filename.txt',
                              content='contents',
                              contenttype=contenttype,
                              resourcetype='asset'
                              )
    arch.save(asset)

    arch.s3.put_object.assert_called_with(
        Key='filename.txt',
        Body=mock.ANY,
        Metadata={"resourcetype": "asset"},
        ContentType=contenttype,
        ContentEncoding='gzip',
        Bucket=testbucket,
    )


# Given a bucket
# When save() is called with metadata
# Then archivist calls s3.put_object with correct params
def test_save_with_metadata():
    arch = S3archivist(testbucket, s3=mock.Mock(), siteconfig={})
    meta = {"stuff": "things"}
    asset = arch.new_resource('filename.txt',
                              content='contents',
                              contenttype=contenttype,
                              resourcetype='asset',
                              metadata=meta
                              )
    arch.save(asset)

    arch.s3.put_object.assert_called_with(
        Key='filename.txt',
        Body=mock.ANY,
        Metadata={"stuff": "things", "resourcetype": "asset"},
        ContentType=contenttype,
        ContentEncoding='gzip',
        Bucket=testbucket,
    )


# Given a bucket
# When save() is called with a deleted asset
# Then archivist calls s3.delete_object with correct params
def test_save_deleted():
    arch = S3archivist(testbucket, s3=mock.Mock(), siteconfig={})
    asset = arch.new_resource('filename.txt', deleted=True)
    arch.save(asset)

    arch.s3.delete_object.assert_called_with(
        Key='filename.txt',
        Bucket=testbucket,
    )


# Given a bucket
# When save() is called without "contenttype"
# Then archivist raises TypeError
def test_save_no_contenttype():
    arch = S3archivist(testbucket, s3=mock.Mock(), siteconfig={})
    asset = arch.new_resource('filename.txt',
                              content='contents',
                              resourcetype='asset',
                              )
    with pytest.raises(TypeError) as einfo:
        arch.save(asset)
    assert 'contenttype' in str(einfo.value)


# Given a bucket
# When save() is called without "content"
# Then archivist raises TypeError
def test_save_no_content():
    arch = S3archivist(testbucket, s3=mock.Mock(), siteconfig={})
    asset = arch.new_resource('filename.txt',
                              contenttype=contenttype,
                              resourcetype='asset',
                              )
    with pytest.raises(TypeError) as einfo:
        arch.save(asset)
    assert 'content' in str(einfo.value)


# Given a bucket
# When save() is called without "key"
# Then archivist raises TypeError
def test_save_no_filename():
    arch = S3archivist(testbucket, s3=mock.Mock(), siteconfig={})
    with pytest.raises(TypeError) as einfo:
        asset = arch.new_resource(content='contents',
                                  contenttype=contenttype,
                                  resourcetype='asset',
                                  )
        arch.save(asset)
    assert einfo


# Given a resource of type artifact
# When save() is called on an artifact with no archetype_guid
# Then archivist raises a ValueError because archetype_guid is required
def test_save_artifact_no_guid():
    arch = S3archivist(testbucket, s3=mock.Mock(), siteconfig={})
    with pytest.raises(ValueError) as einfo:
        asset = arch.new_resource(content='contents',
                                  contenttype=contenttype,
                                  resourcetype='artifact',
                                  key='artifact_without_guid.txt'
                                  )
        arch.save(asset)
    assert einfo


###########################################################################
# Archivist all_archetypes
###########################################################################

# Given archivist
# When all_archetypes() is called
# Then it attempts to retrieve all archetypes from s3
def test_all_archetypes():
    arch = S3archivist(testbucket, s3=mock.Mock(), siteconfig={})
    arch.s3.list_objects.side_effect = [
        {"IsTruncated": True, "NextMarker": "1", "Contents": []},
        {"IsTruncated": False, "Contents": []},
    ]
    for item in arch.all_archetypes():
        pass
    call = mock.call
    call1 = call(Bucket=arch.bucket, Prefix=arch.archetype_prefix)
    call2 = call(Bucket=arch.bucket, Marker="1", Prefix=arch.archetype_prefix)
    arch.s3.list_objects.assert_has_calls([call1, call2])


###########################################################################
# Asset and S3 response to asset
###########################################################################
# The archivist returns Asset objects that wrap the S3 response and process it
# as necessary. Although S3 returns iostreams, we pre-read the iostream to
# produce the raw content. This could be problematic for very large objects.
# Later if we choose to support a streaming response for better performance of
# large objects, we'll add a get_stream method that returns a StreamingAsset.

def test_s3object_to_asset_binary():
    resp = stubs.s3get_response_binary()
    bobj = S3resource.from_s3object(resp)
    assert bobj.content_length == resp['ContentLength']
    assert bobj.contenttype == resp['ContentType']
    assert bobj.last_modified == resp['LastModified']
    assert bobj.metadata == resp['Metadata']
    assert bobj.resourcetype == resp['Metadata']['resourcetype']
    assert bobj.content == stubs.binary_content


def test_s3object_to_asset_binary_has_no_text():
    bobj = S3resource.from_s3object(stubs.s3get_response_binary())
    assert bobj.content == stubs.binary_content
    with pytest.raises(ValueError):
        assert bobj.text == stubs.binary_content


def test_s3object_to_asset_binary_has_no_json():
    bobj = S3resource.from_s3object(stubs.s3get_response_binary())
    assert bobj.content == stubs.binary_content
    with pytest.raises(ValueError):
        assert bobj.data == stubs.binary_content


# If the content type matches text/*, the text property will contain the decoded
# unicode text. The content property still contains raw bytes.
def test_s3object_to_asset_text():
    bobj = S3resource.from_s3object(stubs.s3get_response_text_utf8())
    assert bobj.content == stubs.text_content.encode('utf-8')
    assert bobj.text == stubs.text_content


# If the content type is application/json, the data property should contain the
# parsed data structure.
def test_s3object_to_asset_json():
    bobj = S3resource.from_s3object(stubs.s3get_response_json())
    assert bobj.content == stubs.json_content
    assert bobj.data == json.loads(stubs.json_content)


def test_asset_text_mutator():
    arch = S3archivist(testbucket, s3=mock.Mock(), siteconfig={})
    asset = arch.new_resource(key='testkey', text='¿Dónde esta el baño?',
                              contenttype='text/plain')
    assert type(asset.content) == bytes
    assert asset.text == '¿Dónde esta el baño?'


def test_asset_data_mutator():
    arch = S3archivist(testbucket, s3=mock.Mock(), siteconfig={})
    asset = arch.new_resource(key='testkey', data={"this": "that"},
                              contenttype='application/json')
    assert asset.content == '{"this": "that"}'
    assert asset.data == {"this": "that"}


def test_text_asset_compresses():
    asset = S3resource(bucket=testbucket, text='¿Dónde esta el baño?',
                       contenttype='text/plain; charset=utf-8')
    result = asset.as_s3object()
    assert result['Body'] == gzip('¿Dónde esta el baño?'.encode('utf-8'))
    assert result['ContentEncoding'] == 'gzip'


def test_json_asset_compresses():
    data = json.dumps({"a": '¿Dónde esta el baño?'})
    asset = S3resource(bucket=testbucket, content=data,
                       contenttype='application/json')
    result = asset.as_s3object()
    assert result['Body'] == gzip(data)
    assert result['ContentEncoding'] == 'gzip'


def test_rss_compresses():
    asset = S3resource(bucket=testbucket, text='¿Dónde esta el baño?',
                       contenttype='application/rss+xml')
    result = asset.as_s3object()
    assert result['Body'] == gzip('¿Dónde esta el baño?'.encode('utf-8'))
    assert result['ContentEncoding'] == 'gzip'


def test_uncompressable_contenttype():
    asset = S3resource(bucket=testbucket, text='¿Dónde esta el baño?',
                       contenttype='application/octet-stream')
    result = asset.as_s3object()
    assert result['Body'] == '¿Dónde esta el baño?'.encode('utf-8')
    assert 'ContentEncoding' not in result


def test_compression_disabled():
    asset = S3resource(bucket=testbucket, text='¿Dónde esta el baño?',
                       contenttype='text/plain; charset=utf-8',
                       use_compression=False)
    result = asset.as_s3object()
    assert result['Body'] == '¿Dónde esta el baño?'.encode('utf-8')
    assert 'ContentEncoding' not in result


#############################################################################
# Test jinja
#############################################################################
def test_jinja_defaults():
    arch = S3archivist(testbucket,
                       s3=mock.Mock(),
                       siteconfig={})
    jinja = arch.jinja
    assert jinja.loader.bucket == testbucket
    assert jinja.loader.prefix == '_templates'


def test_jinja_custom_prefix():
    arch = S3archivist(testbucket,
                       s3=mock.Mock(),
                       siteconfig={"template_dir": "tests"})
    jinja = arch.jinja
    assert jinja.loader.bucket == testbucket
    assert jinja.loader.prefix == "tests"


###########################################################################
# Test inflate_config
###########################################################################

# Given a timezone in string format
# When inflate_config
# Then the return value has timezone object as returned by pytz
def test_timezone_from_str():
    config = {'timezone': 'America/New_York'}
    cfg = inflate_config(config)

    assert hasattr(cfg['timezone'], 'localize')


# Given a timezone in object form
# When inflate_config
# Then the return value has timezone object as returned by pytz
def test_timezone_from_obj():
    config = {'timezone': timezone('America/New_York')}
    cfg = inflate_config(config)

    assert hasattr(cfg['timezone'], 'localize')


###########################################################################
# Test S3event
###########################################################################

# Given a valid event struct
# When I construct S3event from it
# Then the correct properties are set
def test_s3event_construct():
    event = stubs.generate_event()['Records'][0]
    ev = S3event(event)

    assert ev.bucket == event['s3']['bucket']['name']
    assert ev.etag == event['s3']['object']['eTag']
    assert ev.key == event['s3']['object']['key']
    assert ev.name == event['eventName']
    assert ev.region == event['awsRegion']
    assert ev.sequencer == event['s3']['object']['sequencer']
    assert ev.source == event['eventSource']
    assert ev.time == event['eventTime']
    assert hasattr(ev.datetime, 'isoformat')


def test_parse_aws_event():
    message = stubs.generate_event()
    result = parse_aws_event(message)

    assert len(result) == 1
    assert type(result[0]) == S3event


def test_parse_sns_event():
    message = stubs.sns_event
    result = parse_aws_event(message)

    assert len(result) == 1
    assert type(result[0]) == S3event

