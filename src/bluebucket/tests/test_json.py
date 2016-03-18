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

import mock
from bluebucket.archivist import S3archivist
import bluebucket.json

siteconfig = {
    "template_dir": "tests",
    "default_template": "test_template.j2"
}

archetype = {
    "title": "Page Title",
    "date": "2015-11-23",
    "_content": "<p>test</p>",
}
testbucket = 'test-bucket'


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
def test_get_template_no_default_no_custom():
    archivist = S3archivist(bucket=testbucket, siteconfig={},
                            jinja=mock.Mock())
    template = bluebucket.json.get_template(archivist, {})
    tlist = ["page.html"]
    archivist.jinja.select_template.assert_called_with(tlist)
    assert template


# Given a siteconfig with a single default_template
# And an archetype with no custom template
# When I call get_template
# Then the templates are ordered most-specific to least specific
def test_get_template_no_custom():
    archivist = S3archivist(bucket=testbucket, siteconfig=siteconfig,
                            jinja=mock.Mock())
    template = bluebucket.json.get_template(archivist, {})
    tlist = ["test_template.j2", "page.html"]
    archivist.jinja.select_template.assert_called_with(tlist)
    assert template


# Given a siteconfig with a single default_template
# And an archetype with a single custom template
# When I call get_template
# Then the templates are ordered most-specific to least specific
def test_get_template_1():
    archivist = S3archivist(bucket=testbucket, siteconfig=siteconfig,
                            jinja=mock.Mock())
    template = bluebucket.json.get_template(archivist,
                                            {"template": "custom_template.j2"})
    tlist = ["custom_template.j2", "test_template.j2", "page.html"]
    archivist.jinja.select_template.assert_called_with(tlist)
    assert template


# Given a siteconfig with a single default_template
# And an archetype with a single custom template as a list of 1
# When I call get_template
# Then the templates are ordered most-specific to least specific
def test_get_template_list_of_1():
    archivist = S3archivist(bucket=testbucket, siteconfig=siteconfig,
                            jinja=mock.Mock())
    template = bluebucket.json.get_template(archivist, {"template":
                                            ["custom_template.j2"]})
    tlist = ["custom_template.j2", "test_template.j2", "page.html"]
    archivist.jinja.select_template.assert_called_with(tlist)
    assert template


# Given a siteconfig with a single default_template
# And an archetype with a multiple custom templates
# When I call get_template
# Then the templates are ordered most-specific to least specific
def test_get_template_list():
    archivist = S3archivist(bucket=testbucket, siteconfig=siteconfig,
                            jinja=mock.Mock())
    template = bluebucket.json.get_template(archivist,
                                            {"template": ["tpl1.j2",
                                                          "tpl2.j2"]})
    tlist = ["tpl1.j2", "tpl2.j2", "test_template.j2", "page.html"]
    archivist.jinja.select_template.assert_called_with(tlist)
    assert template


# Given a siteconfig with a list of default_template
# And an archetype with a single custom template
# When I call get_template
# Then the templates are ordered most-specific to least specific
def test_get_template_default_is_list():
    archivist = S3archivist(bucket=testbucket,
                            siteconfig={"default_template": ["t1.j2", "t2.j2"]},
                            jinja=mock.Mock())
    template = bluebucket.json.get_template(archivist,
                                            {"template": "custom_template.j2"})
    tlist = ["custom_template.j2", "t1.j2", "t2.j2", "page.html"]
    archivist.jinja.select_template.assert_called_with(tlist)
    assert template


#############################################################################
# Test on_save
#############################################################################
# Given an asset containing a valid JSON string
# When I call json.on_save() with the asset
# Then the return value will be an asset containing a rendered template
def test_json_on_save():
    archivist = S3archivist(bucket=testbucket,
                            siteconfig={},
                            jinja=mock.Mock())
    json_asset = archivist.new_asset('test.json', data={"json": "test"})
    these = bluebucket.json.on_save(archivist, json_asset)
    # Hmm, this is a mock generated by rendermock generated by templatemock
    # generated by jinjamock. What can I assert about it other than it is a
    # mock? I can manually inspect the list of calls to see that it happened,
    # but cannot figure out how to do it programmatically. Sigh. --Vince
    assert len(these) == 1


#############################################################################
# Test on_delete
#############################################################################
# Given a key
# When I call json.on_delete
# Then a new asset is returned with the key's extension transformed to .html
# And the new asset has the deleted flag set
def test_json_on_delete():
    archivist = S3archivist(bucket=testbucket,
                            siteconfig={},
                            jinja=mock.Mock())
    these = bluebucket.json.on_delete(archivist, 'test.json')
    assert these[0].deleted
    assert these[0].key == 'test.html'

