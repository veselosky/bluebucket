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

This bluebucket module is a library of functions and classes factored out from
the Blue Bucket Project Lambda function handlers.

For fields expecting an artifact, valid artifact values are:
    [None, 'anthology', 'archetype', 'asset', 'monograph', 'source']

"""
from __future__ import absolute_import, print_function, unicode_literals

import json
import logging
import posixpath as path
import pytz

from functools import partial

from .__about__ import *  # noqa
from .util import SmartJSONEncoder  # FIXME moved, fix imports
from .archivist import S3archivist

# TODO configloader
default_config = {
    "timezone": "America/New_York",
    "archivist": S3archivist,
}


class ConfigLoader(object):
    @property
    def siteconfig(self):
        """Dictionary of configuration data for your site (from _site.json)"""
        if not self._siteconfig:
            cfg = self.s3.get_object(Bucket=self.bucket, Key='_site.json')
            self._siteconfig = json.loads(cfg['Body'].read().decode('utf-8'))
        return self._siteconfig

    @property
    def logger(self):
        return logging.getLogger(type(self).__name__)

    @property
    def timezone(self):
        if self._timezone:
            return self._timezone
        zone = self.siteconfig.get('timezone', 'America/New_York')
        self._timezone = pytz.timezone(zone)
        return self._timezone

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

        if event['eventSource'] != 'aws:s3':
            self.logger.warning('Unexpected event, ignoring: ' + repr(event))
            return self.on_ignore()

        self.bucket = event['s3']['bucket']['name']
        self.key = event['s3']['object']['key']
        basepath, ext = path.splitext(self.key)
        if self.accepts_suffixes and ext not in self.accepts_suffixes:
            self.logger.warning(
                '%s does not have acceptable suffix, ignoring' % self.key)
            return self.on_ignore()
        # TODO filter against accepts_prefixes

        # TODO allow callable as target_suffix for more complex transformations
        self.targetkey = basepath + self.target_suffix

        if event['eventName'].startswith('ObjectRemoved:'):
            return self.on_delete()

        if not event['eventName'].startswith('ObjectCreated:'):
            self.logger.info('skipping unhandled event type %s'
                             % event['eventName'])
            return self.on_ignore()

        return self.on_save()

    @classmethod
    def make_event_handler(cls):
        def handle_event_with_class(cls, event, context):
            return_value = None
            eventlist = event['Records']
            for ev in eventlist:
                try:
                    return_value = cls().handle_event(ev, context)
                except Exception as e:
                    logging.exception("Event crashed: " + repr(e))
            return return_value  # return whatever the last event handler did

        return partial(handle_event_with_class, cls)

# Imperative version of handle_events
# load raw config
# from config, determine correct archivist class
# load archivist class
# !! bucket is required to instantiate an archivist. top-level code does not
# have the bucket of the event. Dispatcher must instantiate archivist.
# from config, determine scribe classes
# load scribe classes
# !! Scribes need archivist to produce Assets. Dispatcher must instantiate
# scribes, since it instantiates archivist.

