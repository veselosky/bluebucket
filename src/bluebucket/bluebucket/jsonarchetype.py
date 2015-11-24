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

from jinja2 import Environment
from jinja2_s3loader import S3loader
import json

from bluebucket import Scribe


# This probably belongs in a util module.
def is_sequence(arg):
    return (not hasattr(arg, "strip") and
            (hasattr(arg, "__getitem__") or
            hasattr(arg, "__iter__")))


class JSONArchetype(Scribe):
    accepts_artifacts = ['archetype']
    accepts_suffixes = ['.json']
    target_suffix = '.html'
    target_content_type = 'text/html'
    target_artifact = 'monograph'
    _jinja = None

    @property
    def jinja(self):
        if self._jinja:
            return self._jinja
        template_dir = self.siteconfig.get('template_dir', '_templates')
        self._jinja = Environment(loader=S3loader(self.bucket, template_dir))
        return self._jinja

    def transform(self, iostream):
        context = json.loads(iostream.read().decode('utf-8'))
        context['_site'] = self.siteconfig
        if 'content_src' in context:
            context['_content'] = self.get_html(context['content_src'])
        template = self.get_template(context)
        return template.render(context)

    def get_html(self, content_src):
        if 'bucket' in content_src and 'key' in content_src:
            resp = self.s3.get_object(Bucket=content_src['bucket'],
                                      Key=content_src['key'])
            return resp['Body'].read().decode('utf-8')
        else:
            # TODO retrieve via href
            raise Exception('Bucket, key not found, href not yet supported.')

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

