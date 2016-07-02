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
from bluebucket.util import is_sequence
from bluebucket.archivist import parse_aws_event, S3archivist
from jinja2 import Template
import logging

logger = logging.getLogger(__name__)
fallback_template = """
<doctype html><html><head>
  <title>{{ Item.title }}</title>
</head><body>{{ Item_Page_Article.body }}
</body></html>
"""


def get_template(archivist, context):
    """Return the correct Jinja2 Template object for this archetype."""
    templates = []

    # Most specific to least specific. Does the archetype request a
    # custom template? Note that config values may be a list, or a
    # single string.
    t = context.get('template')
    if is_sequence(t):
        templates.extend(t)
    elif t:
        templates.append(t)

    # Does the siteconfig specify a default template?
    t = archivist.siteconfig.get('default_template')
    if is_sequence(t):
        templates.extend(t)
    elif t:
        templates.append(t)

    # If no configured default, fall back to "emergency" default.
    templates.append(Template(fallback_template))

    return archivist.jinja.select_template(templates)


def on_save(archivist, resource):
    if not resource.resourcetype == 'archetype':
        return []
    context = resource.data
    for key in context:
        if '/' in key:
            new_key = key.replace('/', '_')
            context[new_key] = context.pop(key)
    context['_site'] = archivist.siteconfig
    template = get_template(archivist, context)
    content = template.render(context)
    resmeta = {
        "contenttype": "text/html; charset=utf-8",
        "resourcetype": "artifact"
    }
    key = archivist.pathstrategy.path_for(**dict(resource.data["Item"],
                                                 **resmeta))
    monograph = archivist.new_resource(key=key,
                                       content=content,
                                       **resmeta)
    archivist.publish(monograph)
    return [monograph]


def item_page_article_to_html(message, context):
    events = parse_aws_event(message)
    if not events:
        logger.warn("No events found in message!\n%s" % message)
    for event in events:
        if event.is_save_event:
            archivist = S3archivist(event.bucket)
            resource = archivist.get(event.key)
            on_save(archivist, resource)
        else:
            logger.warn("Not a save event!\n%s" % event)

