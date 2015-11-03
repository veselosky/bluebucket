"""
A Scribe that translates a YAML source to a JSON archetype.
"""
from __future__ import absolute_import, print_function

import json
import yaml

from bluebucket import SmartJSONEncoder, Scribe


class YAMLSource(Scribe):
    accepts_artifacts = [None, 'source']
    accepts_suffixes = ['.yaml', '.yml']
    target_suffix  = '.json'
    target_content_type = 'application/json'
    target_artifact = 'asset'

    def transform(self, body):
        data = yaml.safe_load(body)
        # TODO Validate and add metadata
        # YAML tries to be clever and parses dates and times into python objects
        # so we need a datetime-aware encoder. grrr.
        return json.dumps(data, cls=SmartJSONEncoder, sort_keys=True)

handle_event = YAMLSource.make_event_handler()

