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
import posixpath as path
import string


# The path strategy object will attempt to calculate a path for a resource given
# the resource metadata.
class DefaultPathStrategy(object):

    def __init__(self, **kwargs):
        self.archetype_prefix = '_A/'
        self.source_prefix = self.archetype_prefix + 'Source/'
        for key in kwargs:
            setattr(self, key, kwargs[key])

    def path_for(self, **meta):
        "Calculate a resource path based on metadata."
        contenttype = meta.get('contenttype')
        resourcetype = meta.get('resourcetype', 'asset')

        if resourcetype == 'asset':
            # Assets can live anywhere outside the archetypes dir, but Source
            # assets are special and live inside the archetypes dir.
            key = meta.get('key')
            if key is not None:
                if key.startswith(self.source_prefix):
                    return key
                else:
                    return self.unprefix(key)
            if contenttype.startswith('text/markdown'):
                guid = meta['guid']  # required in this case
                folder = self.source_prefix + 'text/markdown/'
                return folder + guid + '.md'

        elif resourcetype == 'archetype':
            # Archetypes do not allow any freedom in naming, they are always
            # itemtype and guid
            guid = meta['guid']  # required in this case

            # FIXME Ensure each component is capitalized.
            itemtype = string.capwords(meta['itemtype'], '/')

            return path.join(self.archetype_prefix, itemtype, guid + '.json')

        elif resourcetype == 'artifact':
            # FIXME Construct Artifact paths from metadata for SEO
            key = meta['key']
            return self.unprefix(key)

        elif resourcetype == 'config':
            # config files live in the archetypes directory
            key = meta['key']
            if not key.startswith(self.archetype_prefix):
                key = path.join(self.archetype_prefix, key)
            return key

        raise Exception("No path strategy found.")

    def unprefix(self, key):
        "Remove the archetype or index prefix from a key."
        if key.startswith(self.archetype_prefix):
            key = key[len(self.archetype_prefix):]
        return key

