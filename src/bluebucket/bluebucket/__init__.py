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
from pytz import timezone

from .__about__ import *  # noqa
from .archivist import S3archivist
import bluebucket.markdown
import bluebucket.json


# TODO Decent configuration for logger
logger = logging.getLogger('bluebucket')
default_scribes = {
    '.md': [bluebucket.markdown],
    '.markdown': [bluebucket.markdown],
    '.mdown': [bluebucket.markdown],
    '.json': [bluebucket.json],
}


# DO NOT REGISTER THIS FUNCTION WITH LAMBDA! USE handle_message below!
# Handle an event:
def handle_event(scribe_map, event, context, archivist_class=S3archivist):
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
        return []

    bucket = event['s3']['bucket']['name']
    key = event['s3']['object']['key']
    archivist = archivist_class(bucket)

    basepath, ext = path.splitext(key)
    scribes = scribe_map.get(ext, None)
    # If ext not in handlers dict, ignore event
    if not scribes:
        logger.warning('Unhandled extention, ignoring: ' + ext)
        return []

    assets = []
    for scribe in scribes:
        if event['eventName'].startswith('ObjectRemoved:'):
            try:
                assets.extend(scribe.on_delete(archivist, key))
            except Exception as e:
                logger.error(e)
        elif event['eventName'].startswith('ObjectCreated:'):
            # Retrieve asset from S3 bucket and unwrap
            asset = archivist.get(key)
            try:
                assets.extend(scribe.on_save(archivist, asset))
            except Exception as e:
                logger.error(e)
        else:
            # Ignore unsupported event types
            logger.info('skipping unhandled event type %s' % event['eventName'])
            return

    archivist.persist(assets)
    return assets


def do_indexing(assets):
    pass  # TODO Make an indexer that does something


# Function to unloop events, calls handle_event for each event separately
# IRL never seen more than one per message, but may as well handle it.
# REGISTER THIS FUNCTION WITH LAMBDA
def handle_message(event, context):
    assets = []
    eventlist = event['Records']
    for ev in eventlist:
        try:
            assets.extend(handle_event(default_scribes, ev, context))
        except Exception as e:
            logger.exception("Event crashed: " + repr(e))
    if assets:
        do_indexing(assets)
    # Does Lambda care about the return value of this function?
    return assets


