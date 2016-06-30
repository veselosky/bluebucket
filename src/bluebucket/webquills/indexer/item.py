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
"""
The item indexer maintains an index of all item archetypes. Only the "Item"
sub-key of the archetype is added to the index. Other details must be retrieved
from the archive if needed.

In addition to the "Item" sub-key, several fields are calculated for use as
indexes. The `bucket_itemclass` field, combined with the `s3_key` field, serve
as the primary key.

    "WebQuillsItemByClass": {
      "Type": "AWS::DynamoDB::Table",
      "Properties": {
        "TableName": "webquills-item-by-class",
        "AttributeDefinitions": [
          {
            "AttributeName": "bucket_itemclass",
            "AttributeType": "S"
          },
          {
            "AttributeName": "s3key",
            "AttributeType": "S"
          },
          {
            "AttributeName": "updated_guid",
            "AttributeType": "S"
          },
          {
            "AttributeName": "category_updated_guid",
            "AttributeType": "S"
          }
        ],
        "KeySchema": [
          {
            "AttributeName": "bucket_itemclass",
            "KeyType": "HASH"
          },
          {
            "AttributeName": "s3key",
            "KeyType": "RANGE"
          }
        ],
        "LocalSecondaryIndexes": [
          {
            "IndexName": "updated-guid-index",
            "Projection": {
              "ProjectionType": "KEYS_ONLY"
            },
            "KeySchema": [
              {
                "AttributeName": "bucket_itemclass",
                "KeyType": "HASH"
              },
              {
                "AttributeName": "updated_guid",
                "KeyType": "RANGE"
              }
            ]
          },
          {
            "IndexName": "category-updated-guid-index",
            "Projection": {
              "ProjectionType": "KEYS_ONLY"
            },
            "KeySchema": [
              {
                "AttributeName": "bucket_itemclass",
                "KeyType": "HASH"
              },
              {
                "AttributeName": "category_updated_guid",
                "KeyType": "RANGE"
              }
            ]
          }
        ],
        "ProvisionedThroughput": {
          "ReadCapacityUnits": 5,
          "WriteCapacityUnits": 5
        },
        "StreamSpecification": {
          "StreamViewType": "KEYS_ONLY"
        }
      },
      "Metadata": {
        "AWS::CloudFormation::Designer": {
          "id": "8cd79099-67c0-405e-957c-b73fd0181c13"
        }
      }
    },
"""

from bluebucket.archivist import S3archivist, parse_aws_event
import boto3
import logging

logger = logging.getLogger(__name__)
item_table = 'webquills-item-by-class'


def on_save(db, archivist, resource):
    # Extract the item metadata from the item
    meta = resource.data['Item']

    # Add the calculated key fields bucket_itemclass, updated_guid,
    # category_updated_guid
    class_comps = [x.capitalize() for x in meta['itemtype'].split('/', 3)]
    meta['bucket_itemclass'] = archivist.bucket + '|' +\
        '/'.join(class_comps[:3])
    meta['updated_guid'] = '|'.join([meta['updated'], meta['guid']])
    meta['category_updated_guid'] = '|'.join([meta['category']['name'],
                                              meta['updated'],
                                              meta['guid']])
    meta['s3key'] = resource.key

    # Save to table
    db.Table(item_table).put_item(Item=meta)


def on_remove(db, archivist, key):
    # the itemclass is composed of components 1,2,3 of the path
    # TODO This path calculation should be done by the pathstrategy!
    class_comps = key.split('/', 4)[1:4]
    bucket_itemclass = archivist.bucket + '|' + '/'.join(class_comps[:3])
    db.Table(item_table).delete_item(
        Key={"bucket_itemclass": bucket_itemclass, "s3key": key}
    )


def update_item_index(message, context):
    "When the archive changes, update the index tables to match."
    events = parse_aws_event(message)
    if not events:
        logger.warn("No events found in message!\n%s" % message)
    for event in events:
        if event.is_save_event:
            db = boto3.resource('dynamodb', region_name=event.region)
            archivist = S3archivist(event.bucket)
            resource = archivist.get(event.key)
            on_save(db, archivist, resource)
        else:
            logger.warn("Not a save event!\n%s" % event)


