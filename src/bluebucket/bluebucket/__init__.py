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
import pytz
import logging
import posixpath as path

from .__about__ import *  # noqa
from .archivist import S3archivist
import bluebucket.markdown
import bluebucket.json


# TODO Make an indexer that does something
class FakeIndexer(object):
    def do(action):
        pass


# TODO Decent configuration for logger
logger = logging.getLogger('bluebucket')
handlers = {
    '.md': bluebucket.markdown,
    '.markdown': bluebucket.markdown,
    '.mdown': bluebucket.markdown,
    '.json': bluebucket.json,
}


# Function to unloop events, calls handle_event for each event separately
# IRL never seen more than one per message, but may as well handle it.
# REGISTER THIS FUNCTION WITH LAMBDA
def handle_message(event, context):
    return_value = None
    eventlist = event['Records']
    for ev in eventlist:
        try:
            return_value = handle_event(ev, context)
        except Exception as e:
            logger.exception("Event crashed: " + repr(e))
    return return_value  # return whatever the last event handler did


# Handle an event:
def handle_event(event, context):
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
    # For now, ignore any event not coming from S3
    if event['eventSource'] != 'aws:s3':
        logger.warning('Unexpected event, ignoring: ' + repr(event))
        return

    bucket = event['s3']['bucket']['name']
    key = event['s3']['object']['key']
    archivist = S3archivist(bucket)
    indexer = FakeIndexer()

    basepath, ext = path.splitext(key)
    handler = handlers[ext]
    # If ext not in handlers dict, ignore event
    if not handler:
        logger.warning('Unhandled extention, ignoring: ' + ext)
        return

    assets = []
    if event['eventName'].startswith('ObjectRemoved:'):
        assets.extend(handler.on_delete(archivist, key))
    elif event['eventName'].startswith('ObjectCreated:'):
        # Retrieve asset from S3 bucket and unwrap
        asset = archivist.get(key)
        assets.extend(handler.on_save(archivist, asset))
    else:
        # Ignore unsupported event types
        logger.info('skipping unhandled event type %s' % event['eventName'])
        return

    archivist.persist(assets)
    indexer.index(assets)


class ConfigLoader(object):
    @property
    def timezone(self):
        if self._timezone:
            return self._timezone
        zone = self.siteconfig.get('timezone', 'America/New_York')
        self._timezone = pytz.timezone(zone)
        return self._timezone

