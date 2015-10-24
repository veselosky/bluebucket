"""
A Scribe that translates a YAML source to a JSON archetype.
"""
from __future__ import absolute_import, print_function

import boto3
import datetime
import json
import logging
import posixpath as path
import yaml

logging.basicConfig(level=logging.DEBUG, format='%(asctime)s %(levelname)s %(message)s')

s3 = boto3.client('s3')


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


def _handle_event(event, context):
    # events can arrive out of order. need to track sequencer values to
    # prevent lost updates. 
    # http://docs.aws.amazon.com/AmazonS3/latest/dev/notification-content-structure.html
    logging.debug("Event: " + repr(event))
    logging.debug("Context: " + repr(context))

    if event['eventSource'] != 'aws:s3':
        logging.warning('Unexpected event, ignoring: ' + repr(event))
        return
    
    bucket = event['s3']['bucket']['name']
    key = event['s3']['object']['key']
    obj = s3.get_object(Bucket=bucket, Key=key)
    # check the source, determine the target
    if 'artifact' in obj['Metadata'] and obj['Metadata']['artifact'] != 'source':
        logging.error("%s is not a source item, bailing." % key)
        raise Exception
    if not key.endswith('.yaml') or key.endswith('.yml'):
        logging.warning('%s does not have a yaml extension, trying anyway' % key)
    # TODO probably should also check ContentType

    basepath, _ = path.splitext(key)
    targetkey = basepath + '.json'

    if 'DeleteMarker' in obj and obj['DeleteMarker']:
        if event['eventName'].startswith('ObjectRemoved:'):
            s.delete_object(Bucket=bucket, Key=targetkey)
            logging.info('%s deleted, removing %s' % (key, targetkey))
        return

    if not event['eventName'].startswith('ObjectCreated:'):
        logging.info('skipping unhandled event type %s' % event['eventName'])
        return

    data = yaml.safe_load(obj['Body'])
    # TODO Validate and add metadata
    # YAML tries to be clever and parses dates and times into python objects
    # so we need a datetime-aware encoder. grrr.
    body = json.dumps(data, cls=SmartJSONEncoder, sort_keys=True)

    s3.put_object(
        Bucket=bucket,
        Key=targetkey,
        ContentType='application/json',
        Body=body,
        Metadata={'artifact': 'archetype'}
    )


def handle_event(msg, context):
    """Dispatches events to the appropriate handler method.
    
    Determines the nature of the event, and whether the event affects
    a source item. Dispatches the appropriate event handler."""
    eventlist = []
    try:
        eventlist = msg['Records']
    except KeyError:
        # Does not look like event JSON at all. Ignore.
        logging.error("Malformed Event Message: " + repr(event))
        return None

    for event in eventlist:
        try:
            _handle_event(event, context)
        except Exception as e:
            logging.exception("Event crashed: " + repr(event))


if __name__ == "__main__":
    msg = {'Records': [{'eventName':"localtest"}]}
    handle_event(msg,{"key": "I am context"})
