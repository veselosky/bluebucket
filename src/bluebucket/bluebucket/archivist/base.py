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
import json
import logging
from bluebucket.util import SmartJSONEncoder


logger = logging.getLogger(__name__)


#######################################################################
# Model an object stored in the archive
#######################################################################
class Resource(object):
    def __init__(self, **kwargs):
        self.acl = None
        self.bucket = None
        self.content = None
        self.contenttype = None
        self.contentencoding = None
        self.deleted = False
        self.encoding = 'utf-8'
        self.key = None
        self.last_modified = None
        self.metadata = kwargs.pop("metadata", {})

        for key in kwargs:
            setattr(self, key, kwargs[key])

    @property
    def resourcetype(self):
        return self.metadata.get("resourcetype")

    @resourcetype.setter
    def resourcetype(self, newval):
        self.metadata['resourcetype'] = newval

    @property
    def archetype_guid(self):
        return self.metadata.get("archetype_guid")

    @archetype_guid.setter
    def archetype_guid(self, newval):
        self.metadata['archetype_guid'] = newval

    @property
    def text(self):
        if self.contenttype.startswith('text/'):
            return self.content.decode(self.encoding)
        else:
            raise ValueError("Only text/* MIME types have a text property")

    @text.setter
    def text(self, newtext):
        self.content = newtext.encode(self.encoding)

    @property
    def data(self):
        return json.loads(self.content.decode(self.encoding))

    @data.setter
    def data(self, newdata):
        # dumper only outputs ascii chars, so this should be safe
        self.content = json.dumps(newdata, cls=SmartJSONEncoder, sort_keys=True)


#######################################################################
# Archive Manager
#######################################################################
# Note that for testing purposes, you can pass both the s3 object and the jinja
# object to the constructor.
class Archivist(object):

    def get(self, filename):
        raise NotImplementedError

    def save(self, resource):
        raise NotImplementedError

    def publish(self, resource):
        "Same as save, but ensures the resource is publicly readable."
        raise NotImplementedError

    def persist(self, resourcelist):
        for resource in resourcelist:
            self.save(resource)

    def delete(self, filename):
        raise NotImplementedError

    def new_resource(self, key, **kwargs):
        raise NotImplementedError

    @property
    def jinja(self):
        raise NotImplementedError

    def all_archetypes(self):
        "A generator function that will yield every archetype resource."
        raise NotImplementedError

    def init_bucket(self):
        raise NotImplementedError
