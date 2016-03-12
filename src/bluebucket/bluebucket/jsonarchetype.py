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
from __future__ import absolute_import, print_function, unicode_literals

from bluebucket.scribe import Scribe


# This probably belongs in a util module.
def is_sequence(arg):
    return (not hasattr(arg, "strip") and
            (hasattr(arg, "__getitem__") or
            hasattr(arg, "__iter__")))


class JSONArchetype(Scribe):

    def __init__(self, **kwargs):
        self.jinja = kwargs.get('jinja')
        self.archivist = kwargs.get('archivist')
        self.siteconfig = kwargs.get('siteconfig', {})

        self.accepts_artifacts = ('archetype', )
        self.accepts_suffixes = ('.json', )
        self.target_suffix = '.html'
        self.target_content_type = 'text/html'
        self.target_artifact = 'monograph'

    def on_save(self, asset):
        if not self.can_handle_path(asset.key):
            return []
        context = asset.json
        context['_site'] = self.siteconfig
        if 'content_src' in context:
            context['_content'] = self.get_html(context['content_src'])
        template = self.get_template(context)
        return template.render(context)

    def get_html(self, content_src):
        if 'key' in content_src:
            resp = self.archivist.get(content_src['key'])
            return resp.text
        elif 'href' in content_src:
            raise Exception('HTTP get via href not yet supported.')
        else:
            # TODO retrieve via href
            raise Exception('Unable to resolve content_src reference.')

    def get_template(self, context):
        """Return the correct Jinja2 Template object for this archetype."""
        templates = []

        # Most specific to least specific. Does the archetype request a
        # custom template? Note that config values may be a list, or a
        # single string.
        t = context.get('template', None)
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

