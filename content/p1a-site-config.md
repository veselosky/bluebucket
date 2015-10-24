# Archivist: Automatic Transformation on Upload

A web site is more than just a bunch of files. It has structure and site-wide
properties. Since different sites may want to utilize different features of our
Blue Bucket software, we may also have some site-specific software
configurations. We need a place to store this information.

## Site Configuration for Blue Bucket Sites

Our principles state that the [file system is our repository][], so we're going to
store the site configuration file in our web site repository. However, remember
that this site configuration will be public, just like all the files in your S3
bucket. **Do not store any private information like passwords in the site
configuration!**

Because [web standards are our instruction manual][], we want to store our site
configuration in a standard web format. We're using JSON format for all data
storage. JSON can be a bit of a pain to edit by hand, however. Let's allow the
site configuration to be written in YAML, a superset of JSON that's a bit more
friendly to humans, yet easily parsed by software. This gives us the opportunity
to create our first archivist, which will translate our site configuration from
YAML to JSON.

[siteconfig.yaml](siteconfig.yaml)
 
## Create the Lambda function

    $ aws lambda create-function --function-name yamlsource \
        --runtime python2.7 \
        --role arn:aws:iam::000011112222:role/BlueBucketS3Agent \
        --handler yamlsource.handle_event \
        --publish \
        --zip-file fileb://../yamlsource.zip
    {
        "CodeSha256": "qdi3InaGSLSID1LElv6nzcqvjQ+VKg9AK7BuCPq9Jrs=", 
        "FunctionName": "yamlsource", 
        "CodeSize": 101952, 
        "MemorySize": 128, 
        "FunctionArn": "arn:aws:lambda:us-east-1:000011112222:function:yamlsource", 
        "Version": "1", 
        "Role": "arn:aws:iam::000011112222:role/BlueBucketS3Agent", 
        "Timeout": 3, 
        "LastModified": "2015-10-24T15:22:56.680+0000", 
        "Handler": "yamlsource.handle_event", 
        "Runtime": "python2.7", 
        "Description": ""
    }

Grant S3 permission to execute the function. (You cannot put the bucket
notification configuration until this is done.)

    $ aws lambda add-permission --function-name yamlsource \
        --statement-id 's3-invoke-yamlsource' \
        --source-account 000011112222 \
        --source-arn 'arn:aws:s3:::bluebucket.mindvessel.net' \
        --principal 's3.amazonaws.com' \
        --action 'lambda:InvokeFunction'
    {
        "Statement": "{\"Condition\":{\"StringEquals\":{\"AWS:SourceAccount\":\"000011112222\"},\"ArnLike\":{\"AWS:SourceArn\":\"arn:aws:s3:::bluebucket.mindvessel.net\"}},\"Action\":[\"lambda:InvokeFunction\"],\"Resource\":\"arn:aws:lambda:us-east-1:000011112222:function:yamlsource\",\"Effect\":\"Allow\",\"Principal\":{\"Service\":\"s3.amazonaws.com\"},\"Sid\":\"s3-invoke-yamlsource\"}"
    }

Connect the S3 event notification to run the lambda function.

    $ aws s3api put-bucket-notification-configuration \
        --bucket bluebucket.mindvessel.net \
        --notification-configuration file://config/bucket-notification.json

If you find a bug, you can update the function code and publish a new version.

    $ aws lambda update-function-code --function-name yamlsource \
        --zip-file fileb://../yamlsource.zip --publish

