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

