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
"""
The Indexer creates or updates JSON indexes of saved assets. The output files
live in a dedicated data directory in the bucket.

/_indexes/index.json:
    all items, sorted by date descending

The index JSON file is a JSON object, with the top-level keys containing some
metadata about the index. The top-level "entries" key contains the list of index
entries, sorted reverse chronological (or otherwise as defined by the index).
The metadata should be sufficient to generate an RSS or Atom feed from the index
file. RSS requires a link to the channel's site (equivalent to rel=alternate),
and common practice also includes a rel=self link for the feed. If the index is
too large to fit in a single file, the links will also include a rel=next and/or
rel=prev as appropriate.

    {
    "title": "The Channel Title",
    "description": "Description of this index (required by RSS)",
    "author": "Default channel author",
    "updated": "2016-03-31T19:00:00Z (The lastBuildDate of this index)",
    "category": "As defined in Atom. Useful for category feeds.",
    "links": [{"rel": ["alternate"], "href": "/url"}]
    "entries": [entry1, entry2],
    }

An index entry stores a small subset of the metdata describing the object, and
the path to the object's archetype. The shape is:

    {
    "published": "2016-03-31T19:00:00Z",
    "updated": "2016-03-31T19:00:00Z",
    "category": "Category",
    "title": "The Item Title",
    "author": "The Author",
    "description": "Item description or empty string.",
    "image": "/image/thumbnail.jpg",
    "archetype": "/path/to/archetype.json",
    "monograph": "/path/to/monograph.html"
    }

"""
from __future__ import absolute_import, print_function, unicode_literals
from datetime import datetime
import posixpath as path
import pytz


class Indexer(object):

    def __init__(self, archivist, **kwargs):
        self.archivist = archivist
        self.index_key = path.join(archivist.index_prefix, 'index.json')
        self.indexes = {}
        for key in kwargs:
            setattr(self, key, kwargs[key])

    def record_for_asset(self, asset):
        site = self.archivist.siteconfig.get('site', {})
        ix = {
            "published": asset.data.get('published', None),
            "updated": asset.data.get('updated', None),
            "category": asset.data.get('category', 'uncategorized'),
            "title": asset.data.get('title', ''),
            "author": asset.data.get('author', site.get('author', '')),
            "description": asset.data.get('description', ''),
            "image": asset.data.get('image', ''),
            "monograph": asset.data.get('monograph', ''),
            "itemtype": asset.data.get('itemtype', ''),
            "archetype": asset.key
        }
        return ix

    def bisect_left(self, a, x, lo=0, hi=None, sortfield='published'):
        """Return index where to insert item x in list a, assuming a is reverse sorted.

        The return value i is such that all e in a[:i] have e > x, and all e in
        a[i:] have e <= x.  So if x already appears in the list, a.insert(x)
        will insert just before the leftmost x already there.

        Optional args lo (default 0) and hi (default len(a)) bound the
        slice of a to be searched.

        Optional arg sortfield defines which index field to sort on. Defaults to
        "published".

        This code was cribbed from the standard library bisect module, which is
        hard coded to sort only in ascending order. Modified for our needs.
        """
        if lo < 0:
            raise ValueError('lo must be non-negative')
        if hi is None:
            hi = len(a)
        while lo < hi:
            mid = (lo + hi) // 2
            if a[mid][sortfield] > x:
                lo = mid + 1
            else:
                hi = mid
        return lo

    def load_index(self, index_key, archivist=None):
        if index_key in self.indexes:
            return
        arch = archivist or self.archivist
        # Intentionally allow exception to propogate on 404
        index = arch.get(index_key)
        self.indexes[index_key] = index.data

    def add_to_index(self, index_key, asset):
        entries = self.indexes[index_key]['entries']

        ix = self.record_for_asset(asset)
        where = self.bisect_left(entries, ix['published'])
        entries.insert(where, ix)

    def full_reindex(self, index_key, archivist=None):
        "Reads all archetypes and adds them to a clean index."
        arch = archivist or self.archivist
        # Create a clean index structure
        site = arch.siteconfig.get('site', {})
        index = {
            "title": site.get('title', ''),
            "description": site.get('description', ''),
            "author": site.get('author', ''),
            "updated": datetime.now(pytz.utc),
            "category": site.get('category', 'uncategorized'),
            "links": [{"rel": ["alternate"], "href": site.get('url', '')}],
            "entries": [],
        }
        self.indexes[index_key] = index
        for asset in arch.all_archetypes():
            self.add_to_index(index_key, asset)

    def on_save(self, asset, archivist=None):
        if not asset.artifact == 'archetype':
            return
        try:
            self.load_index(self.index_key)
            self.add_to_index(self.index_key, asset)
        except Exception:  # FIXME be specific what's a 404?
            # Index file does not exist. Generate from scratch.
            return self.full_reindex(self.index_key, archivist)

    def on_delete(self, key, archivist=None):
        entries = self.indexes[self.index_key]['entries']
        # Scan the index to find the item with that key
        try:  # Generator expression marginally more efficient than for loop?
            at = next(i for i, entry in enumerate(entries)
                      if entry['archetype'] == key)
            del entries[at]
        except StopIteration:
            # The item was not in the index!
            pass

