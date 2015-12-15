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
import mock

from bluebucket.yamlsource import YAMLSource
from bluebucket.archivist import S3archivist, S3asset

yaml_body = """
---
testkey: testvalue
"""
json_body = '{"testkey": "testvalue"}'


# Given an asset with yaml content
# When on_save is called
# Then on_save returns list containing an asset with JSON content
# And asset.key has a .json extension
@mock.patch.object(S3archivist, 's3')
def test_transform_on_save(mocks3):
    asset = S3asset(content=yaml_body,
                    contenttype='application/yaml',
                    key='name.yml')
    ys = YAMLSource(archivist=S3archivist('testbucket1'))
    rval = ys.on_save(asset)
    assert len(rval) == 1
    assert rval[0].content == json_body
    assert rval[0].key == 'name.json'


# Given an asset with a .json extension
# When on_save is called
# Then on_save returns an empty list
@mock.patch.object(S3archivist, 's3')
def test_on_save_cannot_handle(mocks3):
    asset = S3asset(content=yaml_body,
                    contenttype='application/yaml',
                    key='name.json')
    ys = YAMLSource(archivist=S3archivist('testbucket1'))
    rval = ys.on_save(asset)
    assert len(rval) == 0


# Given a key ending in .yml
# When on_delete(key) is called
# Then on_delete returns an asset with extension .json
# And asset.deleted is True
@mock.patch.object(S3archivist, 's3')
def test_on_delete(mocks3):
    ys = YAMLSource(archivist=S3archivist('testbucket1'))
    rval = ys.on_delete('testdir/name.yaml')
    assert len(rval) == 1
    assert rval[0].deleted
    assert rval[0].key == 'testdir/name.json'


# Given a key with a .json extension
# When on_delete is called
# Then on_delete returns an empty list
@mock.patch.object(S3archivist, 's3')
def test_on_delete_cannot_handle(mocks3):
    ys = YAMLSource(archivist=S3archivist('testbucket1'))
    rval = ys.on_delete('any/name.json')
    assert len(rval) == 0

