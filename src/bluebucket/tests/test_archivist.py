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

# The S3 Archivist is a simplified wrapper around S3.
from __future__ import print_function, unicode_literals
try:
    import mock
except ImportError:
    import unittest.mock as mock

import json

from bluebucket.archivist import S3archivist
import stubs
import pytest

contenttype = 'text/plain; charset=utf-8'


###########################################################################
# Archivist creating Asset objects
###########################################################################

# Given an archivist
# When I call archivist.new_asset()
# A new asset is returned
# and the asset has a bucket attribute with the same value as the archivist
@mock.patch.object(S3archivist, 's3')
def test_new_asset(mocks3):
    arch = S3archivist('bluebucket.mindvessel.net')
    asset = arch.new_asset()
    assert asset.bucket == arch.bucket


# Given an archivist
# When I call archivist.new_asset(key)
# A new asset is returned
# and the asset's bucket attribute has the same value as the archivist's
# and the asset's key attribute is set with the argument
@mock.patch.object(S3archivist, 's3')
def test_new_asset_with_key(mocks3):
    arch = S3archivist('bluebucket.mindvessel.net')
    asset = arch.new_asset('test.key')
    assert asset.bucket == arch.bucket
    assert asset.key == 'test.key'


# Given an archivist
# When I call archivist.new_asset(key, **kwargs)
# A new asset is returned
# and the asset's attributes have been set by the kwargs
@mock.patch.object(S3archivist, 's3')
def test_new_asset_with_kwargs(mocks3):
    arch = S3archivist('bluebucket.mindvessel.net')
    asset = arch.new_asset('test.key', deleted=True)
    assert asset.bucket == arch.bucket


###########################################################################
# Archivist get_object
###########################################################################

# Given a bucket
# When get() is called with a filename
# Then archivist calls s3.get_object with correct params
# Should we support conditional GET with If-None-Match, If-Modified-Since?
@mock.patch.object(S3archivist, 's3')
def test_get_by_key(mocks3):
    arch = S3archivist('bluebucket.mindvessel.net')
    arch.get('filename.txt')

    mocks3.get_object.assert_called_with(
        Key='filename.txt',
        Bucket='bluebucket.mindvessel.net',
    )


# Given a bucket
# When get() is called without a filename
# Then archivist raises TypeError
@mock.patch.object(S3archivist, 's3')
def test_get_no_filename(mocks3):
    arch = S3archivist('bluebucket.mindvessel.net')
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
@mock.patch.object(S3archivist, 's3')
def test_delete_by_key(mocks3):
    arch = S3archivist('bluebucket.mindvessel.net')
    arch.delete('filename.txt')

    mocks3.delete_object.assert_called_with(
        Key='filename.txt',
        Bucket='bluebucket.mindvessel.net',
    )


# Given a bucket
# When delete() is called without a filename
# Then archivist raises TypeError
@mock.patch.object(S3archivist, 's3')
def test_delete_no_filename(mocks3):
    arch = S3archivist('bluebucket.mindvessel.net')
    with pytest.raises(TypeError):
        arch.delete()


###########################################################################
# Archivist save_object
###########################################################################

# Given a bucket
# When save() is called with all required params
# Then archivist calls s3.put_object with correct params
@mock.patch.object(S3archivist, 's3')
def test_save_success(mocks3):
    arch = S3archivist('bluebucket.mindvessel.net')
    asset = arch.new_asset('filename.txt',
                           content='contents',
                           contenttype=contenttype,
                           artifact='source'
                           )
    arch.save(asset)

    mocks3.put_object.assert_called_with(
        Key='filename.txt',
        Body='contents',
        Metadata={"artifact": "source"},
        ContentType=contenttype,
        Bucket='bluebucket.mindvessel.net',
    )


# Given a bucket
# When save() is called with metadata
# Then archivist calls s3.put_object with correct params
@mock.patch.object(S3archivist, 's3')
def test_save_with_metadata(mocks3):
    meta = {"stuff": "things"}
    arch = S3archivist('bluebucket.mindvessel.net')
    asset = arch.new_asset('filename.txt',
                           content='contents',
                           contenttype=contenttype,
                           artifact='source',
                           metadata=meta
                           )
    arch.save(asset)

    mocks3.put_object.assert_called_with(
        Key='filename.txt',
        Body='contents',
        Metadata={"stuff": "things", "artifact": "source"},
        ContentType=contenttype,
        Bucket='bluebucket.mindvessel.net',
    )


# Given a bucket
# When save() is called with a deleted asset
# Then archivist calls s3.delete_object with correct params
@mock.patch.object(S3archivist, 's3')
def test_save_deleted(mocks3):
    arch = S3archivist('bluebucket.mindvessel.net')
    asset = arch.new_asset('filename.txt', deleted=True)
    arch.save(asset)

    mocks3.delete_object.assert_called_with(
        Key='filename.txt',
        Bucket='bluebucket.mindvessel.net',
    )


# Given a bucket
# When save() is called without "contenttype"
# Then archivist raises TypeError
@mock.patch.object(S3archivist, 's3')
def test_save_no_contenttype(mocks3):
    arch = S3archivist('bluebucket.mindvessel.net')
    asset = arch.new_asset('filename.txt',
                           content='contents',
                           artifact='source',
                           )
    with pytest.raises(TypeError) as einfo:
        arch.save(asset)
    assert 'contenttype' in str(einfo.value)


# Given a bucket
# When save() is called without "content"
# Then archivist raises TypeError
@mock.patch.object(S3archivist, 's3')
def test_save_no_content(mocks3):
    arch = S3archivist('bluebucket.mindvessel.net')
    asset = arch.new_asset('filename.txt',
                           contenttype=contenttype,
                           artifact='source',
                           )
    with pytest.raises(TypeError) as einfo:
        arch.save(asset)
    assert 'content' in str(einfo.value)


# Given a bucket
# When save() is called without "key"
# Then archivist raises TypeError
@mock.patch.object(S3archivist, 's3')
def test_save_no_filename(mocks3):
    arch = S3archivist('bluebucket.mindvessel.net')
    asset = arch.new_asset(content='contents',
                           contenttype=contenttype,
                           artifact='source',
                           )
    with pytest.raises(TypeError) as einfo:
        arch.save(asset)
    assert 'key' in str(einfo.value)


###########################################################################
# Asset and S3 response to asset
###########################################################################
# The archivist returns Asset objects that wrap the S3 response and process it
# as necessary. Although S3 returns iostreams, we pre-read the iostream to
# produce the raw content. This could be problematic for very large objects.
# Later if we choose to support a streaming response for better performance of
# large objects, we'll add a get_stream method that returns a StreamingAsset.

@mock.patch.object(S3archivist, 's3')
def test_s3object_to_asset_binary(mocks3):
    resp = stubs.s3get_response_binary()
    arch = S3archivist('bluebucket.mindvessel.net')
    bobj = arch.s3object_to_asset(resp)
    assert bobj.content_length == resp['ContentLength']
    assert bobj.content_type == resp['ContentType']
    assert bobj.last_modified == resp['LastModified']
    assert bobj.metadata == resp['Metadata']
    assert bobj.artifact == resp['Metadata']['artifact']
    assert bobj.content == stubs.binary_content


@mock.patch.object(S3archivist, 's3')
def test_s3object_to_asset_binary_has_no_text(mocks3):
    arch = S3archivist('bluebucket.mindvessel.net')
    bobj = arch.s3object_to_asset(stubs.s3get_response_binary())
    assert bobj.content == stubs.binary_content
    with pytest.raises(ValueError):
        assert bobj.text == stubs.binary_content


@mock.patch.object(S3archivist, 's3')
def test_s3object_to_asset_binary_has_no_json(mocks3):
    arch = S3archivist('bluebucket.mindvessel.net')
    bobj = arch.s3object_to_asset(stubs.s3get_response_binary())
    assert bobj.content == stubs.binary_content
    with pytest.raises(ValueError):
        assert bobj.json == stubs.binary_content


# If the content type matches text/*, the text property will contain the decoded
# unicode text. The content property still contains raw bytes.
@mock.patch.object(S3archivist, 's3')
def test_s3object_to_asset_text(mocks3):
    arch = S3archivist('bluebucket.mindvessel.net')
    bobj = arch.s3object_to_asset(stubs.s3get_response_text_utf8())
    assert bobj.content == stubs.text_content.encode('utf-8')
    assert bobj.text == stubs.text_content


# If the content type is application/json, the json property should contain the
# parsed data structure.
@mock.patch.object(S3archivist, 's3')
def test_s3object_to_asset_json(mocks3):
    arch = S3archivist('bluebucket.mindvessel.net')
    bobj = arch.s3object_to_asset(stubs.s3get_response_json())
    assert bobj.content == stubs.json_content
    assert bobj.json == json.loads(stubs.json_content)

