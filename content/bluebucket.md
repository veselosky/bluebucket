# Blue Bucket Project: #NoCMS

What if you could eliminate 99% of the cost of running your online presence, and
at the same time make it bulletproof against traffic spikes, software bugs,
infrastructure failures, and most kinds of attacks?

The Blue Bucket Project aims to show that the existing pattern used to build web
content management systems is broken, or at least, that the most common
publishing use cases are better served by a different implementation pattern.
My contention is that traditional database-driven, vertically-integrated content
management systems are an anti-pattern for web publishing, and are as much
hindrance as help to publishing operations at many scales. A CMS can be
decomposed into a distributed system of cooperating processes. By rearranging
the flow of work through these processes, the system could produce the same
outcomes using orders of magnitude less compute power, dramatically reducing
costs while simultaneously improving reliability and performance.

## The Problem and its Significance

The typical system architecture of current content management systems used in
production does not fit with the task given. These systems are constructed as if
they were near-real-time transactional systems, and therefore they make the
wrong trade-offs in cost and scalability. As a result, small publishers may be
paying 100x more than they need to, for a system that is prone to crashing and
vulnerable to denial of service attacks. Large publishers are losing millions.

Why Bother? Does the world really need yet another CMS? I think it does.

I was intrigued by and attracted to the web from the very beginning because I
saw it as a democratizing technology. On the web, a lone individual and a
mega-corporation were effectively equal. The platform provided a level playing
field that allowed the message to stand on its own, to be distributed globally,
available to all at almost no cost. The average person could not afford to run
her own television station, but she could easily afford to run her own web site.
To the site visitor, that site would appear no different from the one "next
door" built by the giant media company. Finally, everyone could have a voice!

Of course, the practice never quite lived up to the ideal. Building *good* web
sites required teams of people, and serving the world required racks of servers.
There always seemed to be this divide between the small scale operations and the
large scale operations. Handling large scale meant spending big bank.

Open source content management systems like Wordpress and Drupal changed the
game for small publishers, but even free software costs money to run at scale.
You need to pay not only for servers and bandwidth but for expertise in software
maintenance and network security, or your entire business could go up in smoke.

This is a significant issue for non-profits who need to leverage the instant,
worldwide communication capabilities of the web while putting every dollar of
their limited funds to the most efficient use.

It is a major problem for small enterprises whose business is driven more and
more by digital channels, where downtime or availability problems can have
direct impact on revenues, and IT costs make up a significant portion of
overhead and/or cost of goods sold.

With Blue Bucket, I'm aiming to prove that the combination of *simple* open
source software components, pay-as-you-go cloud services, and good system
design, can produce a very scalable, very low-cost publishing system. That
system can be simple enough that it can replace static site generators or
Wordpress, and scalable enough that it can replace the high-end commercial
systems used at large media companies.

## The Objective and Hypothesis

With Blue Bucket, I'm aiming to prove that the combination of *simple* open
source software components, pay-as-you-go cloud services, and good system
design, can produce a publishing system with much better scalability and
reliability, at a dramatically reduced cost. That system can be simple enough
that it can replace static site generators or small Wordpress installations, and
scalable enough that it can replace the high-end commercial systems used at
large media companies.

This outcome is achieved by leveraging these concepts, which are the key
hypotheses of the Blue Bucket Project:

1. Static generation of browser assets at publish time is superior to dynamic
   generation at request time. A static system should perform better in terms of
   reliability, overall cost, and ability to absorb traffic spikes.
2. Digital infrastructure has reached utility scale. Organizations will save
   both time and money leveraging cloud services rather than running their own
   servers and software (like connecting to the grid vs generating your own
   electricity).

# Contents

## Architecture, Design, and Theory of Operation

* [Jobs of an Integrated CMS]()
* [Static Site Generators]()
* [Design of a Static CMS]()
* [Design of a Typical Dynamic CMS](a0-dynamic-cms.html)
* [Common Modifications to the Dynamic Model for Scalability and Reliability]()
* [Blue Bucket architecture](p0-architecture-1.html)
* [Content types and metadata attributes](p0-types.html)

## Methods
* [Implementation Outline](m0-goals.html)
* [AWS Services](m0-aws.html)
* [Key Metrics](m0-metrics.html)

## Phase 1: Archive and Basic Transformation
* [Setting up an S3 bucket as a web site](p1-setup-s3.html)
* A Site Configuration File for Blue Bucket Sites
* Implement a Scribe for JSON->HTML
* Implement a Scribe for Markdown->JSON.
* Introduce the POSH template set and style sheet.
* Utilities for S3 and Lambda.

## Phase 2: Content Index and Site Structure
* Producing a Catalogue of the content.
* Generate a "recently published" index page.
* Generate an Atom/RSS feed.
* Generate a category index page.

# Blue Bucket Architecture

Here are some down-to-earth principles used in Blue Bucket's design:

* Web standards are the instruction manual.
* Cloud services are the magic sauce. Hardware and software are anti-patterns.
  Minimize use of infrastructure and custom code.
* Small pieces, loosely joined, are better than big, complex tools.
* The file system is the canonical repository. Every artifact of the site is
  stored in, or derived from, flat files.

I apologize in advance to professionals in the library science field. The
metaphors I have adopted to describe the Blue Bucket architecture misuse and
abuse the language of that field. Nevertheless I find the library metaphor, if
sometimes misapplied, still eases communication and understanding, because it is
so much easier to talk about Archivists and Scribes than about "repository
manager" and "format transformer."

## Some definitions

For this discussion we will be using the metaphor of our system as a
**library**, and the software processes as **agents** or employees in our
library.

If this is the digital library of your content, in the Blue Bucket architecture
S3 is the **archive**, the repository where all your materials are kept.
Conveniently, S3 stores items in what it calls "buckets." We'll just paint ours
blue!

Files stored in our archive are either **sources** or **artifacts**. Sources get
uploaded by external agents called **curators**. Artifacts get created by
**scribes**, agents implemented as Lambda functions.

An **item** is a generic, abstract *thing* that we want to store in our archive.
An item may have many different artifacts in the archive that represent it. For
example, an item might be a picture. In the archive, that item might be
represented as a PNG image file, *and* as a smaller thumbnail image, *and* as an
HTML page that features that image in its body content, *and* as a JSON file
storing metadata about the picture. All these artifacts represent the same item,
the picture.

An **archetype** is the canonical representation of an item in our archive. We
will store them as JSON files. Each source item is transformed into one or more
archetypes. All other artifacts are derived from the archetype.

An **asset** is an artifact associated with an archetype. Typically, an
archetype will store metadata about the content and a pointer to one or more
assets. The asset will store the actual content of the item. Sometimes this will
be identical to the source (e.g. if the source is a PDF file). Other time is
will be different (e.g. the HTML fragment produced from a Markdown source).

A **monograph** is a generated artifact derived from a single archetype, for
example an article page.

An **anthology** is a generated artifact derived from more than one archetype,
for example an index page.

A **template** is a file used to perform transformation of an archetype into an
artifact.

# Goals of the Blue Bucket Project

## Classic CMS vs Blue Bucket

Classic CMS at publish time:
* store content in database
* index content for future retrieval

at request time:
* user generates a request
* request is fielded by a web server
* web server passes request to app server
* app server runs a program to produce the requested page
* the program executes database queries (usually many queries per page)
* the program combines the data with a template to produce HTML, which is
  finally returned to the user.

## Phase 1

Blue Bucket as a system will grow incrementally, using the "minimum viable
product" model to deliver real value even at the earliest stages, and
incrementally improve the value of the system at each successive stage.

In phase 1 we're aiming for core publishing functionality, equivalent to current
static site generators. The feature set for this looks something like this.

* Authors write source files in Markdown syntax.
* The system translates the Markdown source into HTML using a template.

We won't have any fancy content production tools, we'll just be using a text
editor, a command line, and some elbow grease. In the process, we'll learn how
to use several cloud-based services, and we'll erect the skeleton architecture
on which future phases will be built.

At the end of phase 1, the Blue Bucket project will be *self-hosting,* by which
I mean, the system will be managing its own content. At that point, we'll
analyze the system in terms of some key metrics covering performance and cost.

## Phase 2

In phase 2, we will produce a metadata index that allows us to perform queries
over all our data. We'll use that index to generate index pages and feeds.

* The system generates index pages pointing to all the posts.
* The system generates an RSS feed of recent updates.

At the end of phase 2, the core content engine and archive will be complete.
This will form the center of the new system. Further work will bifurcate into
*supply-side* and *demand-side*.

## Supply-side Roadmap

On the supply side, we will examine and experiment with tools for content
creation and curation.

* We will introduce the concept of "curators" to the Blue Bucket system,
  demonstrating how content production tools can be loosely coupled with the
  underlying archive.
* We will create a [PESOS][] curator that will add social media posts to the
  Blue Bucket archive.
* We will select or build an online writing tool that will be useful for posting
  textual content to the archive without the use of client-side tools.
* We will introduce the use of schemas to define the semantic description of
  content items, and the possibility of schema translators.
* We will explore the use of natural language processing techniques to analyze,
  index, and enhance item metadata, with an eye toward better recirculation and
  personalization features on the demand side.

[PESOS]: https://indiewebcamp.com/PESOS

## Demand-side Roadmap

On the demand side, we will develop web-native deliver mechanisms and formats.

* We will introduce the POSH (Plain Old Semantic HTML) template set, a generic
  HTML structure for representing content items.
* We will develop POSH templates for key artifact classes, encoding metadata in
  the HTML to enhance findability on search engines and presentation on social
  media sites.
* We will demonstrate the use of authentication and personalization within the
  static delivery architecture of Blue Bucket.

## Key Metrics

In running any web property, there is a set of key internal metrics that you
want to track to understand your systems operational effectiveness. Here's what
we will be looking at.

* Response time: How long does it take the server to respond to a browser
  request for an asset. Note this is NOT the same as page load time!
* Throughput: How many requests per second can your infrastructure reliably
  serve? Measuring this in S3 could be expensive, so I may defer it.
* Publishing latency: How long does it take to make content changes available to
  the public? This is key for some publishing organizations, and is one of the
  most common trade-offs in large scale systems. For example, using caches can
  improve response time at the expense of publishing latency.
* Cost per Publish: How much money does it cost you to publish an item (or a
  thousand items, since the costs are so small). This number is nearly impossible
  to calculate in most systems, but AWS allows us to do it.
* Cost per View: How much money do you spend serving up your assets to the
  public? Again, in most systems this is almost impossible to measure, but AWS
  allows you to do it, within some parameters.

At various points along the way, we'll pause and take measurements of these key
metrics to see how our system is performing.

# Methods: AWS Cloud Services

## Why S3 and Lambda?

Amazon's Simple Storage Service (S3) is a nearly ideal tool for this application
due to its unique combination of features.

* Cost: S3 has no fixed costs, and the incremental costs are tiny.
* Capacity: While you only pay for what you use, S3 imposes no practical limits
  on storage capacity. You can store one small file, or petabytes of data.
* Durability: S3 stores your data distributed across multiple servers to protect
  against hardware failure.
* Versioning: S3 can track multiple versions of the same object, allowing you to
  "roll back" to a previous version if you make a mistake.
* Event messages: When you add, update, or delete S3 content, you can configure
  S3 to send event messages to external processes via a variety of channels.
* Distribution: An S3 bucket can be configured to expose itself to the Internet
  as a web site. No web servers required.
* Scale: S3 fits our criteria of being efficient at small and large scale. It
  can handle traffic ranging from zero up to several hundred requests per
  second, and can scale even higher by integrating with Cloudfront.

Amazon's Lambda functions are an excellent complement to S3.

* Cost: Lamda has no fixed costs, and the incremental costs are very low.
* Convenience: Lambda functions execute on Amazon's compute grid. No servers
  required.
* Connectedness: Lambda functions can be triggered directly from S3 events,
  obviating the need for complex background job queues.

Using S3 and Lambda, we're going to configure processing pipelines that build
our website as we upload "raw" files into S3.  We don't need any servers or code
to deliver the artifacts to the visitor's web browser, S3 takes care of that for
us.

## How we combine S3 and Lambda to manage our site

As with static site generators, we will edit files in a simple source format and
use software to transform them into the desired outputs. We will start with
Markdown format, but later we can implement other formats. Unlike most static
site generators, we will publish our source files in the same archive as our web
site, making the sources public along with the final outputs.

We will leverage S3 event notifications to trigger Lambda functions (scribes) to
perform our transformations.  Note also that we can use key name filters in the
S3 configuration to call different Lambda functions for different file types or
directories.

Here are some examples of Scribes we may implement.

* YAML source: Scribe will translate to a JSON archetype (useful for site
  configuration).
* Markdown Source: Scribe will translate markdown to HTML and extract content
  metadata for the Archetype.
* JSON Archetype: Scribe will process the Archetype through a template to
  produce an HTML monograph page.
* CSS Source: Scribe will minify to produce a monograph.
* CSS Monograph: Scribe will concatenate with other CSS monographs to create a
  CSS Anthology.

Usually there is an obvious naming convention for various artifacts. If a source
file is a `.markdown` or `.md`, the archetype will always be a `.json` with the
same name. The monograph generated from this archetype would change the
extension to `.html`. There are some cases where this naming convention breaks
down. For example, if we store the HTML *asset* from the markdown as well as the
monograph, we might expect them to have the same name.

To prevent collisions, we will adopt these rules.

* Assets of content type text/html will be stored with the extension `.htm`
  whereas monographs and anthologies will be stored using `.html`.
* Sources in JSON format will be stored with a `.yaml` extension. All correct
  JSON files are also correct YAML files, so this is perfectly legitimate.

## Using DynamoDB to power indexes

DynamoDB has low or no fixed costs depending on reserved throughput
capacity, and the incremental costs are very low. In fact, most web sites will
have such low usage that it will fall under the AWS Free Tier, so DynamoDB is
basically free unless abused.

# Set up an S3 bucket as a web site

We will quickly walk through configuring S3 to be the repository for our Blue
Bucket NoCMS.

FIXME: Almost certainly, all these steps should be consolidated into a single
CloudFormation definition and applied all at once. -- Vince

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
