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
import posixpath as path
from bluebucket.util import is_sequence


def get_template(archivist, context):
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
    t = archivist.siteconfig.get('default_template', None)
    if is_sequence(t):
        templates.extend(t)
    elif t:
        templates.append(t)

    # If no configured default, fall back to conventional default.
    templates.append('page.html')

    return archivist.jinja.select_template(templates)


def on_save(archivist, asset):
    basepath, ext = path.splitext(asset.key)
    context = asset.data
    context['_site'] = archivist.siteconfig
    template = get_template(archivist, context)
    content = template.render(context)
    monograph = archivist.new_asset(key=basepath + '.html',
                                    contenttype='text/html; charset=utf-8',
                                    content=content,
                                    artifact='monograph')
    return [monograph]


def on_delete(archivist, key):
    basepath, ext = path.splitext(key)
    return [archivist.new_asset(key=basepath + '.html', deleted=True)]

