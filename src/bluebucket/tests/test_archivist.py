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

from bluebucket.archivist import S3archivist
# import stubs
import pytest

contenttype = 'text/plain; charset=utf-8'


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


# Given a bucket
# When save() is called with all required params
# Then archivist calls s3.put_object with correct params
@mock.patch.object(S3archivist, 's3')
def test_save_success(mocks3):
    arch = S3archivist('bluebucket.mindvessel.net')
    arch.save('filename.txt', 'contents', contenttype, 'source')

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
    arch.save('filename.txt', 'contents', contenttype, 'source', meta)

    mocks3.put_object.assert_called_with(
        Key='filename.txt',
        Body='contents',
        Metadata={"stuff": "things", "artifact": "source"},
        ContentType=contenttype,
        Bucket='bluebucket.mindvessel.net',
    )


# Given a bucket
# When save() is called without "artifact"
# Then archivist raises TypeError
@mock.patch.object(S3archivist, 's3')
def test_save_no_artifact(mocks3):
    arch = S3archivist('bluebucket.mindvessel.net')
    with pytest.raises(TypeError):
        arch.save('filename.txt', 'contents', contenttype)


# Given a bucket
# When save() is called without "contenttype"
# Then archivist raises TypeError
@mock.patch.object(S3archivist, 's3')
def test_save_no_contenttype(mocks3):
    arch = S3archivist('bluebucket.mindvessel.net')
    with pytest.raises(TypeError):
        arch.save('filename.txt', 'contents')


# Given a bucket
# When save() is called without "content"
# Then archivist raises TypeError
@mock.patch.object(S3archivist, 's3')
def test_save_no_content(mocks3):
    arch = S3archivist('bluebucket.mindvessel.net')
    with pytest.raises(TypeError):
        arch.save('filename.txt')


# Given a bucket
# When save() is called without "filename"
# Then archivist raises TypeError
@mock.patch.object(S3archivist, 's3')
def test_save_no_filename(mocks3):
    arch = S3archivist('bluebucket.mindvessel.net')
    with pytest.raises(TypeError):
        arch.save()


