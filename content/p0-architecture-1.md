# Blue Bucket Architecture

I apologize in advance to professionals in the library science field. The
metaphors I have adopted to describe the Blue Bucket architecture misuse and
abuse the language of that field. Nevertheless I find the library metaphor, if
sometimes misapplied, still eases communication and understanding, because it is
so much easier to talk about Archivists and Scribes than about "inbound format
transformer" and "outbound format transformer."

For this discussion we will be using the metaphor of our CMS as a **library**,
and the software processes as **agents** or employees in our library.  In
systems theory, a system is typically discussed in terms of *stocks* and
*flows,* stocks being some buffer, sink, or collection of stuff in the system,
and flows being the movement of that stuff into or out of a stock. Some flows
happen naturally (water flowing down the drain of the sink) while others require
an agent to facilitate the flow (you need to turn the faucet on to get water
into the sink).

## The classic CMS

DIAGRAM: Traditional CMS in Three Tiers

## The Blue Bucket design

DIAGRAM: Blue Bucket Architecture

## Why AWS S3 and Lambda

Amazon's Simple Storage Service (S3) is a nearly ideal tool for this application
due to its unique combination of features.

* Cost: S3 has no fixed costs, and the incremental costs are tiny.
* Storage: While you only pay for what you use, S3 imposes no practical limits
  on storage capacity. You can store one small file, or petabytes of data.
* Durability: S3 stores your data distributed across multiple servers to protect
  against hardware failure.
* Versioning: S3 supports versioned objects, a very handy feature for a CMS.
* Event messages: When you add, update, or delete S3 content, you can configure
  S3 to send event messages to external processes via a variety of channels.
* Distribution: An S3 bucket can be configured to expose itself to the Internet
  as a web site. No web servers required.
* Permissions: Even when configured as a public web site, S3 allows you to
  restrict access to some objects (like drafts).

In short, S3 is pretty close to being the ideal content repository for this
architecture.

Amazon's Lambda functions are an excellent complement to S3.

* Cost: Lamda has no fixed costs, and the incremental costs are very low.
* Convenience: Lambda functions execute on Amazon's compute grid. No servers
  required.
* Connectedness: Lambda functions can be triggered directly from S3 events,
  obviating the need for complex background job queues.

## Walking through

If we think of this system as the digital library of your content, in the Blue
Bucket architecture S3 is the **stacks**, the repository where all your
materials are kept. In systems language, this is our stock. We're going to try
to make this the only place where we store anything. Conveniently, S3 stores
items in what it calls "buckets." We'll just paint ours blue!

Later on, we'll add a **catalogue** to our library to make it easier to find
things in the stacks, but for now we'll focus only on the content delivery
pipeline. Our agents, who facilitate the flow through the pipeline, will be
implemented using AWS Lambda functions.

We'll talk about the specifics of the [metadata model for Blue Bucket][] in a
separate article. For purposes of this architecture discussion, we need to know
that there is a single, consistent metadata model for all items in the
repository. Content comes in as a **source item** of some kind. We want to store
this source item for future reference, but we also want to store its
**archetype**. The archetype of an item is the "ideal" version of that item, the
canonical representation of its metadata in the approved format.

The core content delivery pipeline takes a source item, converts that to an
archetype, then takes the archetype and converts that into one or more artifacts
in various formats. In our CMS, the key artifact generated this way is a web
page, the HTML representation of the item. There may be other artifacts produced
as well, such as an XML version of the same item.

Source items are added to the stacks by a **curator**. We will eventually have
different kinds of curators, but for phase 1 of Blue Bucket will just write a
small script to upload files. This is not a Lambda agent, just a lowly bit of
local code.

Whenever a curator uploads an item to our bucket, our S3 configuration will
trigger the **archivist**. The job of the archivist is to take a source item and
produce its archetype, which is then stored beside the item in the stacks. 

When the archivist stores the archetype into the bucket, our S3 configuration
will trigger the next agent, the **scribe**. The scribe reads the archetype for
the item and uses it to produce whatever artifacts have been configured. The
scribe then stores these artifacts back to the stacks, our S3 bucket. No agent
is yet configured to be notified when the artifacts are stored, but we may add
one later.

We don't need any servers or code to deliver the artifacts to the visitor's web
browser, S3 takes care of that for us.


[metadata model for Blue Bucket]: p0-archetypes.html

