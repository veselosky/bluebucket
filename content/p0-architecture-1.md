# Blue Bucket Architecture

The Blue Bucket architecture principals serve as a decision framework, a guide
to help us design the system correctly. When we need to make a decision about
how (or whether) to do something, we'll refer to these principles to help us
make the right choice.

Here are some down-to-earth principles used in Blue Bucket's design:

* Web standards are the instruction manual.
* Cloud services are the magic sauce. Hardware and software are anti-patterns.
  Minimize use of infrastructure and custom code.
* Small pieces, loosely joined, are better than big, complex tools. Each
  component of the system should have only one task, and should perform that
  task very well.
  Also known as the [Single Responsibility Principle][].
* The file system is the canonical repository. Every artifact of the site is
  stored in, or derived from, flat files. An end
  user should be able to reproduce the entire system given the repository.

These are our values, the outcomes we desire from our architecture:

* Portability is paramount. Users must be able to extract their content at any
  time and abandon the software without losing any data.
* Scalability goes in both directions. The system must aim to perform well at
  very small scale as well as very large scale.
* Composability is valuable. The system should be interoperable with existing
  systems, preserving user choice of tools.

## Some definitions

For this discussion we will be using the metaphor of our system as a
**library**, and the software processes as **agents** or employees in our
library.

I apologize in advance to professionals in the library science field. The
metaphors I have adopted to describe the Blue Bucket architecture misuse and
abuse the language of that field. Nevertheless I find the library metaphor, if
sometimes misapplied, still eases communication and understanding, because it is
so much easier to talk about Archivists and Scribes than about "repository
manager" and "format transformer."

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

[Single Responsibility Principle]: https://en.wikipedia.org/wiki/Single_responsibility_principle

## The Archive, Artifacts, and Scribes

At the center of the blue bucket architecture is the Archive, the S3 bucket (or
directory) where the content is kept. The things we store in the Archive we
shall call Artifacts. Artifacts come in several types, defining their role in
the system.

The most important Artifact in the Blue Bucket system is the Archetype. The
Archetype is a JSON-formatted file representing each page, article, photo, or
other content item on our web site. We use the JSON format because 1) we want to
store structured data about our content as well as unstructured content itself,
and 2) we want a format that will be usable by our client JavaScript
applications.

Our web site will be produced by AWS Lambda functions following rules that we
set up. The key rule is that each Archetype added to the archive will be
combined with a Template to produce a Monograph.

## Indexes

Aside from data storage, another useful function of a database is to create
indexes over all the objects in your archive. However, just like web pages,
indexes can be pre-generated at publish time and stored in the archive in a
static file. We're going to do exactly that, storing our indexes as JSON files,
and making them available to our JavaScript clients just like the rest of our
data.

Useful indexes for a personal blog might include:

* All objects by date
* Objects by category, then by date
* Objects by item type, then by date

For a multi-author media site, you might add other indexes, such as by author.

If you have a very high publishing velocity (periods where you are publishing
more than one item per second) you may find that the index files become a
bottleneck, because more than one Lambda function may be trying to update them
at once. If this happens, you will want to resolve it by sharding the index;
that is, by splitting the index across more than one file. (You'll want to do
this anyway, as your index files may become very large and start to present a
performance problem.) An alternative would be to rebuild indexes on a schedule
instead of on every change (e.g. once per minute).
