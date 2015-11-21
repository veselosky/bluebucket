"""
Transforms a JSON archetype to a monograph using a Jinja2 template.
"""
from __future__ import absolute_import, print_function

import json
import yaml

from bluebucket import SmartJSONEncoder, Scribe


def is_sequence(arg):
    return (not hasattr(arg, "strip") and
            hasattr(arg, "__getitem__") or
            hasattr(arg, "__iter__"))


class JSONArchetype(Scribe):
    accepts_artifacts = ['archetype']
    accepts_suffixes = ['.json']
    target_suffix  = '.html'
    target_content_type = 'text/html'
    target_artifact = 'monograph'

    def transform(self, body):
        self.archetype = json.load(body)
        raise

    def load_template():
        template_names = self.get_template_names(archetype)
        # return the first found
        for template in template_names:

    def get_template_names(self):
        """Returns a list of potential template names, in order of preference."""
        templates = []

        # Most specific to least specific. Does the archetype request a 
        # custom template? Note that config values may be a list, or a
        # single string.
        t = self.archetype.get('template', None)
        if is_sequence(t):
            templates.extend(t)
        elif t:
            templates.append(t)

        # Does the siteconfig specify a default template?
        t = self.siteconfig.get('default_template', None)
        if is_sequence(t):
            templates.extend(t)
        elif t:
            templates.append(t)

        # If no configured default, fall back to conventional default.
        templates.append('_templates/page.html')
        return templates


handle_event = JSONArchetype.make_event_handler()

