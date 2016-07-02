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
from __future__ import absolute_import, print_function, unicode_literals
from datetime import datetime
try:
    import mock
except ImportError:
    import unittest.mock as mock


def test_indexer_on_save():
    db = mock.Mock()
    archivist = mock.Mock()
    archivist.bucket = 'test-bucket'
    resource = mock.Mock()
    resource.data = {
        "Item": {
            "itemtype": "Item/Page/Article/Blogpost",
            "updated": datetime.now().isoformat(),
            "guid": "test-guid",
            "category": {"name": "test/category"}
        }
    }

    from webquills.indexer.item import on_save
    on_save(db, archivist, resource)
    db.Table().put_item.assert_called_with(Item=mock.ANY)


def test_indexer_on_remove():
    db = mock.Mock()
    archivist = mock.Mock()
    archivist.bucket = 'test-bucket'
    key = "_A/Item/Page/Article/Blogpost/asdf.json"

    expect_key = {
        "bucket_itemclass": "test-bucket|Item/Page/Article",
        "s3key": "_A/Item/Page/Article/Blogpost/asdf.json"
    }
    from webquills.indexer.item import on_remove
    on_remove(db, archivist, key)
    db.Table().delete_item.assert_called_with(Key=expect_key)
