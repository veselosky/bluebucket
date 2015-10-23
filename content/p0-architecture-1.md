# Blue Bucket Architecture

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
represented as a PNG image file, *and* as an HTML page that features that image in
its body content, *and* as a JSON file storing metadata about the picture. All
these artifacts represent the same item, the picture.

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
Markdown format, but later we can implement  Unlike most static site
generators, we will publish our source files in the same archive as our web
site, making the sources public along with the final outputs.

We will leverage S3 event notifications to trigger Lambda functions (scribes) to
perform our transformations.  Note also that we can use key name filters in the
S3 configuration to call different Lambda functions for different file types or
directories.

Here are some examples of Scribes we may implement.

* YAML source: Scribe will translate to a JSON archetype (useful for site
  configuration).
* Markdown Source: Scribe will translate markdown to HTML and extract content metadata for the Archetype.
* JSON Archetype: Scribe will process the Archetype through a template to produce an HTML monograph page.
* CSS Source: Scribe will minify to produce a monograph.
* CSS Monograph: Scribe will concatenate with other CSS monographs to create a CSS Anthology.

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
