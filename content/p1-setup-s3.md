# Set up an S3 bucket as a web site

We will quickly walk through configuring S3 to be the repository for our Blue
Bucket NoCMS.

## First get your tools on

First, create a virtualenv and install the AWS tools on your machine.

    $ mkvirtualenv bluebucket
    $ pip install awscli boto3

Log into your AWS console and [create an IAM user][] to be used for this
project, giving that user permissions to own S3 and Lambda resources. Configure
your command line tools to use that user's credentials.

    $ aws configure
    AWS Access Key ID [None]: ****
    AWS Secret Access Key [None]: ****
    Default region name [us-east-1]:
    Default output format [None]: json

Now you can rock the AWS from the command line, making all this much more
reproducible. 

## Setting up our S3 bucket

Next, we'll create a bucket to hold our repository, and since it is also the web
site, we'll make it public by default.

    $ aws s3api create-bucket --bucket bluebucket.mindvessel.net
    {
    "Location": "/bluebucket.mindvessel.net"
    }

We also have to apply a policy to grant read permissions to the world.

    $ cat config/bucket-policy.json
    {
      "Statement": [
        {
          "Action": [
            "s3:GetObject"
          ], 
          "Effect": "Allow", 
          "Principal": "*", 
          "Resource": [
            "arn:aws:s3:::bluebucket.mindvessel.net/*"
          ]
        }
      ]
    }
    $ aws s3api put-bucket-policy --bucket bluebucket.mindvessel.net --policy file://config/bucket-policy.json

Since this is our main content repository, we'll also enable versioning.

    $ aws s3api put-bucket-versioning --bucket bluebucket.mindvessel.net --versioning-configuration Status=Enabled

Next we add a website configuration.

    $ aws s3 website s3://bluebucket.mindvessel.net/ --index-document index.html

Finally, for testing purposes, let's upload a home page.

    $ aws s3 cp index.html s3://bluebucket.mindvessel.net/index.html

And now we can load our site in a browser! A quick add of a CNAME record at my
DNS provider, pointing to
bluebucket.mindvessel.net.s3-website-us-east-1.amazonaws.com, and now I can load
my website at the subdomain of my own domain:
[http://bluebucket.mindvessel.net](http://bluebucket.mindvessel.net).

[create an IAM user]:http://docs.aws.amazon.com/IAM/latest/UserGuide/id_users_create.html#id_users_create_console

## Creating an Execution Role for Lambda

Now that we have a website, we need to make sure we have a role that will allow
Lambda access to our S3 bucket and other resources it will need.

    $ cat config/lambda-role-trust-policy.json
    {
        "Version": "2012-10-17",
        "Statement": [
            {
                "Effect": "Allow",
                "Principal": {
                    "Service": "lambda.amazonaws.com"
                },
                "Action": "sts:AssumeRole"
            }
        ]
    }
    $ aws iam create-role --role-name BlueBucketS3Agent \
        --assume-role-policy-document file://config/lambda-role-trust-policy.json

    $ cat config/lambda-role-access-policy.json
    {
        "Statement": [
            {
                "Action": [
                    "logs:CreateLogGroup",
                    "logs:CreateLogStream",
                    "logs:PutLogEvents"
                ],
                "Effect": "Allow",
                "Resource": "arn:aws:logs:*:*:*"
            },
            {
                "Action": [
                    "s3:*"
                ],
                "Effect": "Allow",
                "Resource": [
                    "arn:aws:s3:::bluebucket.mindvessel.net/*"
                ]
            }
        ]
    }
    $ aws iam put-role-policy --role-name BlueBucketS3Agent --policy-name BlueBucketS3AgentPolicy \
        --policy-document file://config/lambda-role-access-policy.json
