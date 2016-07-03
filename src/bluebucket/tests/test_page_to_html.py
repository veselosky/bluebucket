# vim: set fileencoding=utf-8 :
#
#   Copyright 2016 Vince Veselosky and contributors
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
from botocore.exceptions import ClientError
from webquills.scribe import page_to_html as scribe

siteconfig = {
    "template_dir": "tests",
    "default_template": "test_template.j2"
}

archetype = {
    "Item": {
        "itemtype": "Item/Page/Article",
        "title": "Page Title",
        "date": "2015-11-23",
        "guid": "f57beeec-9958-45bb-911e-df5a95064523",
        "contenttype": "text/html; charset=utf-8",
        "category": {"name": "test/category"},
        "slug": "page-title",
    },
    "Item/Page/Article": {
        "body": "<p>test</p>",
    }
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
    template = scribe.get_template(archivist, {})
    tlist = [mock.ANY]
    archivist.jinja.select_template.assert_called_with(tlist)
    assert template


# Given a siteconfig with a single default_template
# And an archetype with no custom template
# When I call get_template
# Then the templates are ordered most-specific to least specific
def test_get_template_no_custom():
    archivist = S3archivist(bucket=testbucket, siteconfig=siteconfig,
                            jinja=mock.Mock())
    template = scribe.get_template(archivist, {})
    tlist = ["test_template.j2", mock.ANY]
    archivist.jinja.select_template.assert_called_with(tlist)
    assert template


# Given a siteconfig with a single default_template
# And an archetype with a single custom template
# When I call get_template
# Then the templates are ordered most-specific to least specific
def test_get_template_1():
    archivist = S3archivist(bucket=testbucket, siteconfig=siteconfig,
                            jinja=mock.Mock())
    template = scribe.get_template(archivist,
                                   {"template": "custom_template.j2"})
    tlist = ["custom_template.j2", "test_template.j2", mock.ANY]
    archivist.jinja.select_template.assert_called_with(tlist)
    assert template


# Given a siteconfig with a single default_template
# And an archetype with a single custom template as a list of 1
# When I call get_template
# Then the templates are ordered most-specific to least specific
def test_get_template_list_of_1():
    archivist = S3archivist(bucket=testbucket, siteconfig=siteconfig,
                            jinja=mock.Mock())
    template = scribe.get_template(archivist, {"template":
                                               ["custom_template.j2"]})
    tlist = ["custom_template.j2", "test_template.j2", mock.ANY]
    archivist.jinja.select_template.assert_called_with(tlist)
    assert template


# Given a siteconfig with a single default_template
# And an archetype with a multiple custom templates
# When I call get_template
# Then the templates are ordered most-specific to least specific
def test_get_template_list():
    archivist = S3archivist(bucket=testbucket, siteconfig=siteconfig,
                            jinja=mock.Mock())
    template = scribe.get_template(archivist,
                                   {"template": ["tpl1.j2",
                                                 "tpl2.j2"]})
    tlist = ["tpl1.j2", "tpl2.j2", "test_template.j2", mock.ANY]
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
    template = scribe.get_template(archivist,
                                   {"template": "custom_template.j2"})
    tlist = ["custom_template.j2", "t1.j2", "t2.j2", mock.ANY]
    archivist.jinja.select_template.assert_called_with(tlist)
    assert template


#############################################################################
# Test on_save
#############################################################################
# Given a resource containing a valid archetype
# When I call scribe.on_save() with the resource
# Then the return value will be a resource containing a rendered template
def test_json_on_save():
    archivist = S3archivist(bucket=testbucket,
                            siteconfig=siteconfig,
                            s3=mock.Mock())
    archivist.s3.get_object.side_effect = ClientError({"Error": {}},
                                                      "NoSuchKey")
    archivist.publish = mock.Mock()
    the_thingy = archivist.new_resource('test.json',
                                        data=archetype,
                                        contenttype='application/json',
                                        resourcetype='archetype')
    these = scribe.on_save(archivist, the_thingy)
    assert len(these) == 1
    resource = these[0]
    assert resource.contenttype == 'text/html; charset=utf-8'
    assert resource.resourcetype == 'artifact'
    assert "<p>test</p>" in resource.text
    assert archivist.publish.called_with(resource)


def test_json_not_archetype_on_save():
    # JSON files that are not resourcetype "archetype" should be ignored, as
    # they are probably config files or something, not content
    archivist = S3archivist(bucket=testbucket,
                            siteconfig={},
                            jinja=mock.Mock())
    json_asset = archivist.new_resource('test.json', data={"json": "test"},
                                        contenttype='application/json')
    these = scribe.on_save(archivist, json_asset)
    assert len(these) == 0

