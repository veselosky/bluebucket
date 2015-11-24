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
from __future__ import absolute_import, print_function

import boto3
import datetime
import json
import logging
import posixpath as path

from functools import partial


class SmartJSONEncoder(json.JSONEncoder):
    """
    JSONEncoder subclass that knows how to encode date/time.
    """
    def default(self, o):
        if isinstance(o, datetime.datetime):
            r = o.isoformat()
            if o.microsecond:
                r = r[:23] + r[26:]
            if r.endswith('+00:00'):
                r = r[:-6] + 'Z'
            return r
        elif isinstance(o, datetime.date):
            return o.isoformat()
        elif isinstance(o, datetime.time):
            r = o.isoformat()
            if o.microsecond:
                r = r[:12]
            return r
        else:
            return super(SmartJSONEncoder, self).default(o)


class Scribe(object):
    """A base class for scribes. Reads from S3, performs transform, writes back.

    To use the Scribe class, create a subclass, overriding the key attributes
    and methods. Then call `make_event_handler` to produce a handler function
    for Lambda. ::

        # File: html2text.py
        from bluebucket import Scribe

        class HTML2Text(Scribe):
            accepts_suffixes = ['.html']
            accepts_artifacts = [None, 'source']
            target_suffix = '.txt'
            target_content_type = 'text/plain'
            target_artifact = 'monograph'

            def transform(self, iostream):
                from utils.html import strip_tags
                return strip_tags(iostream.read().decode('utf-8'))

        handle_event = HTML2Text.make_event_handler()
        # Now register html2text.handle_event as your Lambda function handler
    """

    #: List of file name (key) extensions acceptable as input. Override in
    #: subclass. Example: ['.yaml', '.yml']
    accepts_suffixes = None

    #: List of directories (key prefixes) acceptable as input. Override in
    #: subclass. Example: ['images/', 'pics/']
    accepts_prefixes = None

    #: List of artifact types acceptable as input. Override in subclass.
    #: Example: [None, 'source']
    accepts_artifacts = None

    #: The file name extension (key suffix) the scribe outputs.
    #: Example: '.html'
    target_suffix = None

    #: The content type the scribe generates as output. Example: 'text/html'
    target_content_type = None

    #: The artifact type the scribe outputs. Example: 'archetype'
    target_artifact = 'asset'

    #: Metadata dict to append when saving target.
    metadata = None

    #: A reference to the boto3 s3 client. Mock this out for unit tests!
    s3 = boto3.client('s3')

    _siteconfig = None
    
    @property
    def siteconfig(self):
        """Dictionary of configuration data for your site (from _site.json)"""
        if not self._siteconfig:
            cfg = self.s3.get_object(Bucket=self.bucket, Key='_site.json')
            self._siteconfig = json.load(cfg['Body'])
        return self._siteconfig

    @property
    def logger(self):
        return logging.getLogger(type(self).__name__)

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

    def on_delete(self):
        """Handles actions when an S3 object is deleted (or replaced with
        DeleteMarker)."""
        # NOTE: If target does not exist, raises exception. That's cool.
        target = self.s3.get_object(Bucket=self.bucket, Key=self.targetkey)
        try:
            if target['Metadata'].get('artifact', None) != self.target_artifact:
                self.logger.warning(
                    'Target artifact %s of %s does not match'
                    % (target['Metadata']['artifact'], self.targetkey))
                return
        except:
            self.logger.warning('Target artifact (None) of %s does not match'
                                % self.targetkey)
            return

        self.logger.info('%s deleted, removing %s' % (self.key, self.targetkey))
        self.s3.delete_object(Bucket=self.bucket, Key=self.targetkey)
        return

    def on_ignore(self):
        """Handles actions when an event is skipped (i.e. does nothing)."""
        pass

    def on_save(self):
        """Handles actions when an S3 object is saved.

        The default implementation calls `self.transform` to transform the
        object's body content, then saves the target object back to the bucket.
        Most subclasses will only need to override the `transform` method.
        """
        self.obj = self.s3.get_object(Bucket=self.bucket, Key=self.key)
        # test artifact against accepts_artifacts
        source_artifact = self.obj['Metadata'].get('artifact', None)
        if source_artifact not in self.accepts_artifacts:
            self.logger.warning(
                'Unacceptable input artifact (%s) for %s, skipping'
                % (source_artifact, self.key))
            return

        body = self.transform(self.obj['Body'])
        # TODO ¿Merge source metadata with target metadata?
        metadata = self.metadata or {}
        metadata['artifact'] = self.target_artifact

        self.s3.put_object(
            Bucket=self.bucket,
            Key=self.targetkey,
            ContentType=self.target_content_type,
            Body=body,
            Metadata=metadata
        )

    def transform(self, iostream):
        raise NotImplemented

    @classmethod
    def make_event_handler(cls):
        def handle_event_with_class(cls, event, context):
            return_value = None
            eventlist = event['Records']
            for ev in eventlist:
                try:
                    return_value = cls().handle_event(ev, context)
                except Exception as e:
                    logging.exception("Event crashed: " + repr(ev))
            return return_value  # return whatever the last event handler did

        return partial(handle_event_with_class, cls)

