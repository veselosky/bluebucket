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
from __future__ import absolute_import, print_function, unicode_literals
from io import BytesIO

import mock
from jinja2 import Template

from bluebucket.jsonarchetype import JSONArchetype, is_sequence

siteconfig = b'''{
"template_dir": "tests",
"default_template": "test_template.j2"
}
'''

archetype = b'''{
"title": "Page Title",
"date": "2015-11-23",
"content_src": {
    "bucket": "test-bucket",
    "key": "test-key",
    "href": "http://test-bucket/test-key",
    "type": "text/html"
}
}'''


#############################################################################
# NOTE To test anything but the jinja property, mock out the jinja property.
#############################################################################

#############################################################################
# Test get_template
#############################################################################
# Given a siteconfig with no default_template
# And an archetype with no custom template
# When I call get_template
# Then the fallback template is selected
@mock.patch.object(JSONArchetype, 's3')
@mock.patch.object(JSONArchetype, 'jinja')
def test_get_template_no_default_no_custom(mockjinja, mocks3):
    mockjinja.select_template.return_value = Template('')
    empty_siteconfig = b'{}'
    mocks3.get_object.return_value = {"Body": BytesIO(empty_siteconfig)}
    cut = JSONArchetype()
    cut.bucket = "test-bucket"
    cut.key = "test-key"
    template = cut.get_template({})
    assert type(template) == Template
    tlist = ["page.html"]
    mockjinja.select_template.assert_called_with(tlist)


# Given a siteconfig with a single default_template
# And an archetype with no custom template
# When I call get_template
# Then the templates are ordered most-specific to least specific
@mock.patch.object(JSONArchetype, 's3')
@mock.patch.object(JSONArchetype, 'jinja')
def test_get_template_no_custom(mockjinja, mocks3):
    mockjinja.select_template.return_value = Template('')
    mocks3.get_object.return_value = {"Body": BytesIO(siteconfig)}
    cut = JSONArchetype()
    cut.bucket = "test-bucket"
    cut.key = "test-key"
    template = cut.get_template({})
    assert type(template) == Template
    tlist = ["test_template.j2", "page.html"]
    mockjinja.select_template.assert_called_with(tlist)


# Given a siteconfig with a single default_template
# And an archetype with a single custom template
# When I call get_template
# Then the templates are ordered most-specific to least specific
@mock.patch.object(JSONArchetype, 's3')
@mock.patch.object(JSONArchetype, 'jinja')
def test_get_template_1(mockjinja, mocks3):
    mockjinja.select_template.return_value = Template('')
    mocks3.get_object.return_value = {"Body": BytesIO(siteconfig)}
    cut = JSONArchetype()
    cut.bucket = "test-bucket"
    cut.key = "test-key"
    template = cut.get_template({"template": "custom_template.j2"})
    assert type(template) == Template
    tlist = ["custom_template.j2", "test_template.j2", "page.html"]
    mockjinja.select_template.assert_called_with(tlist)


# Given a siteconfig with a single default_template
# And an archetype with a single custom template as a list of 1
# When I call get_template
# Then the templates are ordered most-specific to least specific
@mock.patch.object(JSONArchetype, 's3')
@mock.patch.object(JSONArchetype, 'jinja')
def test_get_template_list_of_1(mockjinja, mocks3):
    mockjinja.select_template.return_value = Template('')
    mocks3.get_object.return_value = {"Body": BytesIO(siteconfig)}
    cut = JSONArchetype()
    cut.bucket = "test-bucket"
    cut.key = "test-key"
    template = cut.get_template({"template": ["custom_template.j2"]})
    assert type(template) == Template
    tlist = ["custom_template.j2", "test_template.j2", "page.html"]
    mockjinja.select_template.assert_called_with(tlist)


# Given a siteconfig with a single default_template
# And an archetype with a multiple custom templates
# When I call get_template
# Then the templates are ordered most-specific to least specific
@mock.patch.object(JSONArchetype, 's3')
@mock.patch.object(JSONArchetype, 'jinja')
def test_get_template_list(mockjinja, mocks3):
    mockjinja.select_template.return_value = Template('')
    mocks3.get_object.return_value = {"Body": BytesIO(siteconfig)}
    cut = JSONArchetype()
    cut.bucket = "test-bucket"
    cut.key = "test-key"
    template = cut.get_template({"template": ["tpl1.j2", "tpl2.j2"]})
    assert type(template) == Template
    tlist = ["tpl1.j2", "tpl2.j2", "test_template.j2", "page.html"]
    mockjinja.select_template.assert_called_with(tlist)


# Given a siteconfig with a list of default_template
# And an archetype with a single custom template
# When I call get_template
# Then the templates are ordered most-specific to least specific
@mock.patch.object(JSONArchetype, 's3')
@mock.patch.object(JSONArchetype, 'jinja')
def test_get_template_default_is_list(mockjinja, mocks3):
    mockjinja.select_template.return_value = Template('')
    multi_tpl_siteconfig = b'{"default_template":["t1.j2","t2.j2"]}'
    mocks3.get_object.return_value = {"Body": BytesIO(multi_tpl_siteconfig)}
    cut = JSONArchetype()
    cut.bucket = "test-bucket"
    cut.key = "test-key"
    template = cut.get_template({"template": "custom_template.j2"})
    assert type(template) == Template
    tlist = ["custom_template.j2", "t1.j2", "t2.j2", "page.html"]
    mockjinja.select_template.assert_called_with(tlist)


#############################################################################
# Test transform
#############################################################################
@mock.patch.object(JSONArchetype, 's3')
@mock.patch.object(JSONArchetype, 'get_template')
def test_transform(mockgt, mocks3):
    template = Template('{{ _site.template_dir }}')
    mockgt.return_value = template
    mocks3.get_object.return_value = {"Body": BytesIO(siteconfig)}
    cut = JSONArchetype()
    cut.bucket = "test-bucket"
    cut.key = "test-key"
    out = cut.transform(BytesIO(archetype))
    assert out == u'tests'
    mocks3.get_object.assert_called_with(Bucket='test-bucket', Key='test-key')


#############################################################################
# Test jinja
#############################################################################
# Given a siteconfig with a list of default_template
# And an archetype with a single custom template
# When I call get_template
# Then the templates are ordered most-specific to least specific
@mock.patch.object(JSONArchetype, 's3')
def test_jinja(mocks3):
    mocks3.get_object.return_value = {"Body": BytesIO(siteconfig)}
    cut = JSONArchetype()
    cut.bucket = "test-bucket"
    cut.key = "test-key"
    jinja = cut.jinja
    assert jinja.loader.bucket == "test-bucket"
    assert jinja.loader.prefix == "tests"


#############################################################################
# Test is_sequence
#############################################################################
def test_string_is_sequence():
    assert not is_sequence('test string')


def test_list_is_sequence():
    assert is_sequence(['a list'])

