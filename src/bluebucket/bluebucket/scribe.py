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

import logging


class Scribe(object):
    """A base class for scribes."""

    #: List of file name (key) extensions acceptable as input. Override in
    #: subclass. Example: ['.yaml', '.yml']
    accepts_suffixes = None

    #: List of directories (key prefixes) acceptable as input. Override in
    #: subclass. Example: ['images/', 'pics/']
    accepts_prefixes = None

    def __init__(self, **kwargs):
        for name in kwargs:
            setattr(self, name, kwargs[name])

    @property
    def logger(self):
        return logging.getLogger(type(self).__name__)

    def can_handle_path(self, key):
        """Return True if this scribe can handle the given input path."""
        if self.accepts_suffixes \
                and not key.endswith(tuple(self.accepts_suffixes)):
            self.logger.info(
                '%s does not have acceptable suffix, ignoring' % key)
            return False

        if self.accepts_prefixes \
                and not key.startswith(tuple(self.accepts_prefixes)):
            self.logger.info(
                '%s does not have acceptable suffix, ignoring' % key)
            return False

        return True

    def on_delete(self, key):
        """Return a list of Assets that should be persisted to the archive.

        Normally, the returned assets will have their `deleted` flag set, since
        it is typical to delete a destination when its source is removed.
        However, you can also return full assets to be saved, in case you need
        the removal of one asset to trigger the creation of another.
        """
        raise NotImplementedError

    def on_save(self, asset):
        """Return a list of Assets that should be persisted to the archive.

        Normally, the returned assets will be full content objects, since
        typically the scribe will be creating a transformed version. However,
        you can also return assets with their `deleted` flag set, in case the
        creation of one asset should trigger the removal of another.
        """
        raise NotImplementedError

