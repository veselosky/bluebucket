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
import errno
import json
import logging
from bluebucket.pathstrategy import DefaultPathStrategy
from bluebucket.archivist.s3 import S3resource
from pytz import timezone
from io import open
import os
import os.path as path


logger = logging.getLogger(__name__)


def inflate_config(config):
    """Takes a bare decoded JSON dict and creates Python objects from certain
    keys"""
    tz = config.get('timezone', 'America/New_York')
    config['timezone'] = tz if hasattr(tz, 'utcoffset') else timezone(tz)
    # Your transformation here
    return config


#######################################################################
# Model a stored S3 object
#######################################################################
class localresource(S3resource):
    def __init__(self, **kwargs):
        super(localresource, self).__init__(**kwargs)
        # We don't compress local files
        self.use_compression = False


#######################################################################
# Archive Manager
#######################################################################
# Note that for testing purposes, you can pass both the s3 object and the jinja
# object to the constructor.
class localarchivist(object):

    def __init__(self, bucket, **kwargs):
        self.bucket = bucket
        self.archetype_prefix = '_A/'
        self.index_prefix = '_I/'
        self.meta_prefix = '.meta/'
        self.siteconfig = None
        self.pathstrategy = DefaultPathStrategy()
        self._jinja = None  # See jinja property below
        for key in kwargs:
            if key == 'jinja':
                setattr(self, '_jinja', kwargs[key])
            else:
                setattr(self, key, kwargs[key])

        if self.siteconfig is None:
            cfg_path = self.archetype_prefix + 'site.json'
            self.siteconfig = inflate_config(self.get(cfg_path).data)

    def _write_resource(self, resource):
        # Special, writes the s3obj in a meta place, then writes the content
        # only to the requested key.
        metafile = path.join(self.bucket, self.meta_prefix, resource.key)
        contentfile = path.join(self.bucket, resource.key)
        try:
            os.makedirs(path.split(metafile)[0])
        except OSError, e:  # be happy if someone already created the path
            if e.errno != errno.EEXIST:
                raise
        try:
            os.makedirs(path.split(contentfile)[0])
        except OSError, e:  # be happy if someone already created the path
            if e.errno != errno.EEXIST:
                raise
        with open(metafile, 'wb') as f:
            json.dump(resource.as_s3object(), f)
        with open(contentfile, 'wb') as f:
            f.write(resource.content)

    def _read_resource(self, Bucket, Key):
        # Reads a s3object file from the bucket's meta location. Does not
        # attempt to read the original content, as it is stored in the meta.
        the_file = path.join(self.bucket, self.meta_prefix, Key)
        with open(the_file, 'r', encoding='utf-8') as f:
            obj = json.load(f)
        return obj

    def _delete_resource(self, Bucket, Key):
        # Deletes a s3object file and its associated content file.
        metafile = path.join(Bucket, self.meta_prefix, Key)
        contentfile = path.join(Bucket, Key)
        mpath = path.split(metafile)[0]
        cpath = path.split(contentfile)[0]
        os.remove(contentfile)
        os.remove(metafile)
        try:
            os.removedirs(mpath)
        except OSError:
            pass
        try:
            os.removedirs(cpath)
        except OSError:
            pass

    def get(self, filename):
        reso = localresource.from_s3object(
            self._read_resource(Bucket=self.bucket, Key=filename)
        )
        reso.key = filename
        reso.bucket = self.bucket
        return reso

    def save(self, resource):
        # To be saved a resource must have: key, contenttype, content
        # Strictly speaking, content is not required, but creating an empty
        # object should be explicit, so must pass empty string.
        if resource.key is None:
            raise TypeError("Cannot save resource without key")

        if resource.deleted:
            return self._delete_resource(
                Bucket=self.bucket,  # NOTE archivist's bucket, NOT resource's!
                Key=resource.key,
            )

        if resource.contenttype is None:
            raise TypeError("Cannot save resource without contenttype")
        if resource.content is None:
            raise TypeError("""To save an empty resource, set content to an empty
                            bytestring""")
        if resource.resourcetype == 'artifact' and not resource.archetype_guid:
            raise ValueError("""Resources of type artifact must contain an
                             archetype_guid""")

        return self._write_resource(resource)
        # TODO On successful put, send SNS message to onSaveArtifact
        # Since artifacts do not have a fixed path prefix or suffix, we cannot
        # ask S3 to send notifications automatically, so we send them manually
        # here.

    def publish(self, resource):
        "Same as save, but ensures the resource is publicly readable."
        resource.acl = 'public-read'
        self.save(resource)

    def persist(self, resourcelist):
        for resource in resourcelist:
            self.save(resource)

    def delete(self, filename):
        return self._delete_resource(Bucket=self.bucket, Key=filename)

    def new_resource(self, key, **kwargs):
        return localresource(bucket=self.bucket, key=key, **kwargs)

    @property
    def jinja(self):
        if self._jinja:
            return self._jinja
        from jinja2 import Environment, FileSystemLoader
        template_dir = self.siteconfig.get('template_dir', '_templates')
        self._jinja = Environment(
            loader=FileSystemLoader(path.join(self.bucket, template_dir))
        )
        return self._jinja

    def all_archetypes(self):
        "A generator function that will yield every archetype resource."
        # S3 will return up to 1000 items in a list_objects call. If there are
        # more, IsTruncated will be True and NextMarker is the offset to use to
        # get the next 1000.
        for (dirpath, dirnames, filenames) in os.walk(self.bucket):
            for filename in filenames:
                yield self.get(path.join(dirpath, filename))

