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
Transforms a JSON archetype to a monograph using a Jinja2 template.
"""
from __future__ import absolute_import, print_function

from jinja2 import Environment
from jinja2_s3loader import S3loader
import json

from bluebucket import Scribe


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

    @property
    def jinja(self):
        if self._jinja:
            return self._jinja
        template_dir = self.siteconfig.get('template_dir', '_templates')
        self._jinja = Environment(loader=S3loader(self.bucket, template_dir))
        return self._jinja

    def transform(self, body):
        context = json.load(body)
        context['_site'] = self.siteconfig
        template = self.get_template()
        return template.render(context)

    def get_template(self):
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
        templates.append('page.html')

        return self.jinja.select_template(templates)


handle_event = JSONArchetype.make_event_handler()

