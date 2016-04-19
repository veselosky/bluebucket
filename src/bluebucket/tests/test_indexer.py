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
from bluebucket.archivist import S3archivist
from bluebucket.indexer import Indexer
try:
    import mock
except ImportError:
    import unittest.mock as mock

contenttype = 'text/plain; charset=utf-8'
testbucket = 'test-bucket'
asset_data = {
    "published": "2016-03-31T19:00:00Z",
    "updated": "2016-03-31T19:00:00Z",
    "category": "Category",
    "title": "The Item Title",
    "author": "The Author",
    "description": "Item description or empty string.",
    "image": "/image/thumbnail.jpg",
    "monograph": "/path/to/monograph.html"
}


###########################################################################
# Indexer
###########################################################################

# Given an asset
# When I call indexer.record_for_asset
# Then a dictionary with values from the asset is returned
def test_record_from_asset():
    arch = S3archivist(testbucket, s3=mock.Mock(), siteconfig={})
    asset = arch.new_asset(key='test.key', data=asset_data)
    indexer = Indexer(archivist=arch)
    ix = indexer.record_for_asset(asset)
    assert ix['title'] == asset_data['title']
    assert ix['published'] == asset_data['published']
    assert ix['updated'] == asset_data['updated']
    assert ix['category'] == asset_data['category']
    assert ix['author'] == asset_data['author']
    assert ix['description'] == asset_data['description']
    assert ix['image'] == asset_data['image']
    assert ix['monograph'] == asset_data['monograph']
    assert ix['archetype'] == 'test.key'
    assert 'itemtype' in ix


def test_load_index():
    arch = mock.Mock()
    arch.index_prefix = 'test'
    indexer = Indexer(archivist=arch)
    indexer.load_index(indexer.index_key)
    assert arch.get.called_once_with(indexer.index_key)
    assert indexer.index_key in indexer.indexes


def test_add_to_index():
    arch = mock.Mock()
    arch.index_prefix = 'test'
    indexer = Indexer(archivist=arch)
    entries = []
    indexer.indexes[indexer.index_key] = {"entries": entries}
    asset = arch.new_asset(key='test.key', data=asset_data)

    indexer.add_to_index(indexer.index_key, asset)

    assert len(entries) == 1


def test_full_reindex():
    arch = mock.Mock()
    arch.index_prefix = 'test'
    arch.siteconfig = {"site": asset_data}
    arch.all_archetypes.return_value = []
    indexer = Indexer(archivist=arch)
    indexer.full_reindex(indexer.index_key)

    ix = indexer.indexes[indexer.index_key]
    assert ix['title'] == asset_data['title']
    arch.all_archetypes.assert_called_with()


def test_on_save_with_non_archetype():
    arch = mock.Mock()
    arch.index_prefix = 'test'
    arch.siteconfig = {"site": asset_data}
    arch.all_archetypes.return_value = []
    asset = arch.new_asset(key='test.key', data=asset_data, artifact='thing')
    indexer = Indexer(archivist=arch)

    indexer.on_save(asset)
    arch.assert_not_called()


def test_on_delete():
    arch = S3archivist(testbucket, s3=mock.Mock(), siteconfig={})
    testkey = arch.archetype_prefix + 'test.key'
    asset = arch.new_asset(key=testkey, data=asset_data, artifact='archetype')
    asset2 = arch.new_asset(key='non-matching.key', data=asset_data,
                            artifact='archetype')
    entries = []
    indexer = Indexer(archivist=arch)
    indexer.indexes[indexer.index_key] = {"entries": entries}
    indexer.add_to_index(indexer.index_key, asset)
    indexer.add_to_index(indexer.index_key, asset2)
    assert len(entries) == 2  # just to be sure our setup worked

    indexer.on_delete(testkey)
    assert len(entries) == 1

