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


class Dispatcher(object):
    """Receives and dispatches events from the archive."""

    def __init__(self, siteconfig):
        self.siteconfig = siteconfig

    @property
    def logger(self):
        return logging.getLogger(type(self).__name__)

    def get_event_asset(self):
        archivist = self.siteconfig['archivist'](self.bucket)
        return archivist.get(self.key)

    def handle_event(self, event, context):
        """Handles a single event from an event message.

        This method handles most of the boilerplate work for event handling,
        including filtering out non-s3 events and events on files that the
        class does not know how to handle. It will dispatch to one of three
        event handling routines: `on_delete`, `on_save`, or `on_ignore`. The
        base Scribe class has default implementations for all three. If your
        scribe implements a simple transform, there is no need for you to
        override these event handling routines. Simply override the
        `transform` method.

        """
        self.event = event
        self.context = context

        # For now we will ignore any events not coming from S3.
        if event['eventSource'] != 'aws:s3':
            self.logger.warning('Unexpected event, ignoring: ' + repr(event))
            return self.on_ignore()

        self.bucket = event['s3']['bucket']['name']
        self.key = event['s3']['object']['key']

        if event['eventName'].startswith('ObjectRemoved:'):
            return self.on_delete()

        if not event['eventName'].startswith('ObjectCreated:'):
            self.logger.info('skipping unhandled event type %s'
                             % event['eventName'])
            return self.on_ignore()

        return self.on_save()

    def on_delete(self):
        """Handles actions when an S3 object is deleted (or replaced with
        DeleteMarker)."""
        assets = []
        for scribe in self.siteconfig['scribes']:
            try:
                assets.extend(scribe.on_delete(self.key))
            except Exception as e:
                self.logger.error("Suppressed scribe.on_delete exception:" +
                                  str(e))
        return assets

    def on_save(self):
        """Handles actions when an S3 object is saved."""
        assets = []
        obj = self.get_event_asset()
        for scribe in self.siteconfig['scribes']:
            try:
                assets.extend(scribe.on_save(obj))
            except Exception as e:
                self.logger.error("Suppressed scribe.on_save exception:" +
                                  str(e))
        return assets

    def on_ignore(self):
        """Handles actions when an event is skipped (i.e. does nothing)."""
        return []

