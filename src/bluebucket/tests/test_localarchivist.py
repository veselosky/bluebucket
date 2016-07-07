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
import os.path as path

from bluebucket.archivist.local import localarchivist, localresource
from bluebucket.archivist import inflate_config
import stubs
import pytest

contenttype = 'text/plain; charset=utf-8'


@pytest.fixture(scope="module")
def testbucket(request):
    import tempfile
    import shutil
    bucket = tempfile.mkdtemp()

    def cleanup():
        shutil.rmtree(bucket)
    return bucket


###########################################################################
# Archivist creating Asset objects
###########################################################################

# Given an archivist
# When I call archivist.new_resource(key)
# A new resource is returned
# and the resource's bucket attribute has the same value as the archivist's
# and the resource's key attribute is set with the argument
def test_new_resource_with_key(testbucket):
    arch = localarchivist(testbucket, siteconfig={})
    asset = arch.new_resource('test.key')
    assert asset.bucket == testbucket
    assert asset.key == 'test.key'


# Given an archivist
# When I call archivist.new_resource(key, **kwargs)
# A new asset is returned
# and the asset's attributes have been set by the kwargs
def test_new_resource_with_kwargs(testbucket):
    arch = localarchivist(testbucket, siteconfig={})
    asset = arch.new_resource('test.key', deleted=True)
    assert asset.deleted is True


###########################################################################
# Archivist save
###########################################################################

# Given a bucket
# When save() is called with all required params
# And then get() is called with the same key
# Then get returns a resource identical to the saved one
def test_save_success(testbucket):
    arch = localarchivist(testbucket, siteconfig={})
    asset = arch.new_resource('filename.txt',
                              content='contents',
                              contenttype=contenttype,
                              resourcetype='asset'
                              )
    arch.save(asset)

    resource = arch.get('filename.txt')

    assert path.exists(path.join(testbucket, 'filename.txt'))
    assert resource.key == 'filename.txt'
    assert resource.bucket == arch.bucket
    assert resource.content == 'contents'
    assert resource.resourcetype == 'asset'
    assert resource.contenttype == contenttype


# Given a bucket
# When save() is called with a deleted asset
# Then archivist removes the file and all metadata
def test_save_deleted(testbucket):
    arch = localarchivist(testbucket, siteconfig={})
    asset = arch.new_resource('filename.txt', deleted=True)
    arch.save(asset)
    assert not path.exists(path.join(testbucket, 'filename.txt'))
    assert not path.exists(path.join(testbucket, arch.meta_prefix,
                                     'filename.txt'))


# Given a bucket
# When save() is called with metadata
# Then archivist calls s3.put_object with correct params
def test_save_with_metadata(testbucket):
    arch = localarchivist(testbucket, siteconfig={})
    meta = {"stuff": "things"}
    asset = arch.new_resource('filename.txt',
                              content='contents',
                              contenttype=contenttype,
                              resourcetype='asset',
                              metadata=meta
                              )
    arch.save(asset)
    resource = arch.get('filename.txt')

    assert path.exists(path.join(testbucket, 'filename.txt'))
    assert resource.key == 'filename.txt'
    assert resource.bucket == arch.bucket
    assert resource.content == 'contents'
    assert resource.resourcetype == 'asset'
    assert resource.contenttype == contenttype
    assert resource.metadata == {"stuff": "things", "resourcetype": "asset"}


# Given a bucket
# When save() is called without "contenttype"
# Then archivist raises TypeError
def test_save_no_contenttype(testbucket):
    arch = localarchivist(testbucket, siteconfig={})
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
def test_save_no_content(testbucket):
    arch = localarchivist(testbucket, siteconfig={})
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
def test_save_no_filename(testbucket):
    arch = localarchivist(testbucket, siteconfig={})
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
def test_save_artifact_no_guid(testbucket):
    arch = localarchivist(testbucket, siteconfig={})
    with pytest.raises(ValueError) as einfo:
        asset = arch.new_resource(content='contents',
                                  contenttype=contenttype,
                                  resourcetype='artifact',
                                  key='artifact_without_guid.txt'
                                  )
        arch.save(asset)
    assert einfo


###########################################################################
# Archivist get
###########################################################################
# Given a bucket
# When get() is called without a filename
# Then archivist raises TypeError
def test_get_no_filename(testbucket):
    arch = localarchivist(testbucket, siteconfig={})
    with pytest.raises(TypeError):
        arch.get()


###########################################################################
# Archivist delete_object
###########################################################################

# Given a bucket
# When delete() is called with a filename
# Then archivist removes the file and metadata
def test_delete_by_key(testbucket):
    arch = localarchivist(testbucket, siteconfig={})
    arch.delete('filename.txt')
    assert not path.exists(path.join(testbucket, 'filename.txt'))
    assert not path.exists(path.join(testbucket, arch.meta_prefix,
                                     'filename.txt'))


# Given a bucket
# When delete() is called without a filename
# Then archivist raises TypeError
def test_delete_no_filename(testbucket):
    arch = localarchivist(testbucket, siteconfig={})
    with pytest.raises(TypeError):
        arch.delete()


###########################################################################
# Archivist all_archetypes
###########################################################################

# Given archivist
# When all_archetypes() is called
# Then it returns a list of all archetypes
def test_all_archetypes(testbucket):
    arch = localarchivist(testbucket, siteconfig={})
    for item in arch.all_archetypes():
        assert isinstance(item, localresource)


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
    bobj = localresource.from_s3object(resp)
    assert bobj.content_length == resp['ContentLength']
    assert bobj.contenttype == resp['ContentType']
    assert bobj.last_modified == resp['LastModified']
    assert bobj.metadata == resp['Metadata']
    assert bobj.resourcetype == resp['Metadata']['resourcetype']
    assert bobj.content == stubs.binary_content


def test_s3object_to_asset_binary_has_no_text():
    bobj = localresource.from_s3object(stubs.s3get_response_binary())
    assert bobj.content == stubs.binary_content
    with pytest.raises(ValueError):
        assert bobj.text == stubs.binary_content


def test_s3object_to_asset_binary_has_no_json():
    bobj = localresource.from_s3object(stubs.s3get_response_binary())
    assert bobj.content == stubs.binary_content
    with pytest.raises(ValueError):
        assert bobj.data == stubs.binary_content


# If the content type matches text/*, the text property will contain the decoded
# unicode text. The content property still contains raw bytes.
def test_s3object_to_asset_text():
    bobj = localresource.from_s3object(stubs.s3get_response_text_utf8())
    assert bobj.content == stubs.text_content.encode('utf-8')
    assert bobj.text == stubs.text_content


# If the content type is application/json, the data property should contain the
# parsed data structure.
def test_s3object_to_asset_json():
    bobj = localresource.from_s3object(stubs.s3get_response_json())
    assert bobj.content == stubs.json_content
    assert bobj.data == json.loads(stubs.json_content)


def test_asset_text_mutator(testbucket):
    arch = localarchivist(testbucket, siteconfig={})
    asset = arch.new_resource(key='testkey', text='¿Dónde esta el baño?',
                              contenttype='text/plain')
    assert type(asset.content) == bytes
    assert asset.text == '¿Dónde esta el baño?'


def test_asset_data_mutator(testbucket):
    arch = localarchivist(testbucket, siteconfig={})
    asset = arch.new_resource(key='testkey', data={"this": "that"},
                              contenttype='application/json')
    assert asset.content == '{"this": "that"}'
    assert asset.data == {"this": "that"}


#############################################################################
# Test jinja  # TODO update these for filesystem loader
#############################################################################
def test_jinja_defaults(testbucket):
    arch = localarchivist(testbucket,
                          siteconfig={})
    jinja = arch.jinja
    assert jinja.loader.searchpath == [path.join(testbucket, '_templates')]


def test_jinja_custom_prefix(testbucket):
    arch = localarchivist(testbucket,
                          siteconfig={"template_dir": "tests"})
    jinja = arch.jinja
    assert jinja.loader.searchpath == [path.join(testbucket, "tests")]


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
# Test localevent
###########################################################################

# Given a valid event struct
# When I construct localevent from it
# Then the correct properties are set
# def test_s3event_construct():
#     event = stubs.generate_event()['Records'][0]
#     ev = localevent(event)
#
#     assert ev.bucket == event['s3']['bucket']['name']
#     assert ev.etag == event['s3']['object']['eTag']
#     assert ev.key == event['s3']['object']['key']
#     assert ev.name == event['eventName']
#     assert ev.region == event['awsRegion']
#     assert ev.sequencer == event['s3']['object']['sequencer']
#     assert ev.source == event['eventSource']
#     assert ev.time == event['eventTime']
#     assert hasattr(ev.datetime, 'isoformat')

