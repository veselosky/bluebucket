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
from bluebucket.pathstrategy import DefaultPathStrategy
import pytest


# Use cases:

# I have a markdown file I want to save as a source asset
def test_markdown_source_asset():
    p = DefaultPathStrategy()
    meta = {
        "resourcetype": "asset",
        "itemtype": "Item/Page/Article",
        "contenttype": "text/markdown; charset=utf-8",
        "guid": "653f3ad8-cf4e-43db-afcb-a06ff3e2bfdb"
    }
    target = p.path_for(**meta)
    assert target ==\
        '_A/Source/text/markdown/653f3ad8-cf4e-43db-afcb-a06ff3e2bfdb.md'


# Given meta with no guid
# When I call path_for()
# Then it raises ValueError because guid is required for a source asset
def test_markdown_source_no_guid():
    p = DefaultPathStrategy()
    meta = {
        "resourcetype": "asset",
        "itemtype": "Item/Page/Article",
        "contenttype": "text/markdown; charset=utf-8",
    }
    with pytest.raises(Exception):
        p.path_for(**meta)


# Given meta representing an archetype of an Article
# When I call path_for()
# Then it returns a path with category + slug.html
def test_article_archetype():
    p = DefaultPathStrategy()
    meta = {
        "resourcetype": "artifact",
        "itemtype": "Item/Page/Article",
        "contenttype": "text/html; charset=utf-8",
        "category": {"name": "test/category"},
        "slug": "article-slug",
    }
    answer = p.path_for(**meta)
    assert answer == 'test/category/article-slug.html'


# Given meta representing an archetype of a Catalog
# When I call path_for()
# Then it returns a path with category + slug.html
def test_catalog_archetype():
    p = DefaultPathStrategy()
    meta = {
        "resourcetype": "artifact",
        "itemtype": "Item/Page/Catalog",
        "contenttype": "text/html; charset=utf-8",
        "category": {"name": "test/category"},
        "slug": "catalog-slug",
    }
    answer = p.path_for(**meta)
    assert answer == 'test/category/catalog-slug.html'


# Given meta representing an archetype of a Catalog
# When I call path_for()
# Then it returns a path with category + slug.html
def test_catalog_archetype_as_xml():
    p = DefaultPathStrategy()
    meta = {
        "resourcetype": "artifact",
        "itemtype": "Item/Page/Catalog",
        "contenttype": "application/atom+xml",
        "category": {"name": "test/category"},
        "slug": "catalog-slug",
    }
    answer = p.path_for(**meta)
    assert answer == 'test/category/catalog-slug.xml'


def test_archetype():
    p = DefaultPathStrategy()

    meta = {
        "resourcetype": "archetype",
        "itemtype": "item/page/article",
        "contenttype": "application/json",
        "guid": "653f3ad8-cf4e-43db-afcb-a06ff3e2bfdb"
    }
    target = p.path_for(**meta)
    assert target ==\
        '_A/Item/Page/Article/653f3ad8-cf4e-43db-afcb-a06ff3e2bfdb.json'
