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
