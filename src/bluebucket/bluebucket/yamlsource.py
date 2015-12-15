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
A Scribe that translates a YAML source to a JSON archetype.
"""
from __future__ import absolute_import, print_function

import json
import posixpath as path
import yaml

from .util import SmartJSONEncoder
from .scribe import Scribe


class YAMLSource(Scribe):
    accepts_artifacts = [None, 'source']
    accepts_suffixes = ['.yaml', '.yml']
    target_suffix = '.json'
    target_contenttype = 'application/json'

    def on_save(self, asset):
        if not self.can_handle_path(asset.key):
            return []

        basepath, ext = path.splitext(asset.key)

        data = yaml.safe_load(asset.content)
        # TODO Validate and add metadata
        # YAML tries to be clever and parses dates and times into python objects
        # so we need a datetime-aware encoder. grrr.
        content = json.dumps(data, cls=SmartJSONEncoder, sort_keys=True)
        asset = self.archivist.new_asset(basepath + self.target_suffix,
                                         contenttype=self.target_contenttype,
                                         artifact='config',
                                         content=content)
        return [asset]

    def on_delete(self, key):
        if not self.can_handle_path(key):
            return []

        basepath, ext = path.splitext(key)
        asset = self.archivist.new_asset(basepath + self.target_suffix,
                                         deleted=True)
        return [asset]
