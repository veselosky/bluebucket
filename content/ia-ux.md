# Blue Bucket Information Architecture

One of the challenging aspects of a web content management system is that the
information architecture of the web is wide open. There are few guidelines or
guardrails to help define the shape of a web page or a website. There are many,
many "standards" both formal and de facto, but none are universal. Additionally,
almost everyone who implements a content management systems sees their own
situation as somehow "special" and insists on customizing their system to their
own particular perceived needs.

To design our own information architecture, we therefore want to be compatible
with the standards in practical use on the web today, but sufficiently flexible
that we can easily adapt to new emerging standards, or customize for specialized
uses.

Some key standards that any web publishing system should be aware of are these.

* [HTML5](https://www.w3.org/TR/html5/): Obviously the gold standard, since we
  are managing web content. However, it is not terribly helpful in designing our
  information architecture.
* [OpenGraph Protocol][]: Introduced by Facebook, this metadata vocabulary is
  used by social media sites to improve discovery and presentation of content.
* [Schema.org][]: This metadata vocabulary is used by web search engines to
  improve discovery and presentation of content in search results pages.
* [RSS2][]: The de facto standard syndication format used by many blog engines.
* [Atom][]: An alternate syndication format used by many blog engines.
* [Microformats2][]: An ad hoc vocabulary for encoding metadata into HTML.
* [Dublin Core][]: This metadata vocabulary is widely used on the web, both in
  HTML and as an XML namespace in RSS feeds.

## High Level Overview

At the highest level, our system will manage *websites*. A *website,* for our
purpose, is a collection of web resources associated with a domain. The web
resources that are managed by our system we will generically call *Items.* Items
come in lots of shapes and sizes and formats. Some classes of item will require
special handling by our system, so we'll want to understand the differences.

The key things we care about are things that will be represented on our website
as web pages. We will generically call these *Pages*. These Pages will have an
Internet media type of `text/html` and some basic metadata.  There is an
infinite number of things that could be represented by a web page, so we will
add some structure to this by creating *item types* below.

The list of types will expand in the future, but we'll start with a small set of
common patterns. 

*Articles* are the primary content items we want to track. These are also
called item detail pages, and typically there is one item per page, or a single
item is the main focus of the page.

*Catalogs* are pages *not* focused on a single item, but containing pointers to
multiple items, built from Indexes rather than item Archetypes. Some examples
of Catalogs include the site home page (usually), a table of contents page, or
a date-based archive page.

*Utility pages* do not expose content, but rather expose a function to the site
visitor. In a pure static architecture, these pages will typically deliver a
JavaScript application. A site search results page is an example of a Utility
page. In more advanced sites, these may be dynamic pages.

Other things won't be web pages on our site, but will be used by or embedded in
web pages. These include images, audio files, video files, and JavaScript
embeds. It may also include small text objects that don't really rate their own
web page, but that might be useful in a website; things like notes and tweets.
We will generically call these *Assets*.

In summary, our high-level classes of items are:

* Page
    * Article
    * Catalog
    * Utility
* Asset
    * Image
    * Embed
    * Audio
    * Video
    * File

## Metadata

Here's a little secret about content management systems: they don't actually
spend much of their time and effort managing content. In real life, mostly what
they manage is *metadata* about the content that they manage. One of the things
that makes content management systems so complex is that nobody seems to be able
to agree on *what* metadata should be managed. As a result, every system for
managing content seems to reinvent the metadata wheel in a slightly different
way from the previous one, and every organization has its own subtle
customizations it wants for its own implementation.

All our assets will need some metadata for our system to track them. We will
build a core metadata schema that represents a minimal set of data to be useful
in our system. Then we will allow extensions to that schema to define additional
metadata required by specific item types or asset types.

Following the mantra that web standards are our instruction manual, we turn to
the standards identified above to define our metadata scheme. Unfortunately (or
fortunately) there is no single standard that is universally applied, but there
are many which are broadly adopted. As it happens, I have done a fairly
extensive study of such schemes in my work, and I put together this [spreadsheet
comparing various metadata standards][].

From that, I culled the common parts and things I know from experience will be
needed. Then, I pared the list down to the essentials to support the
functionality in our first two phases of development for Blue Bucket.

The result is the following short list. We will extend this list of supported
metadata fields in later phases of the project.

### Core Item Metadata

guid (alias: id, identifier; **required** **automatic**)
: Every asset needs a globally unique identifier as a "handle" by which the CMS
  can "grab" it. No two items can have the same identifier, and the identifier
  should permanent. This makes the URL a poor identifier, because even though
  [cool URLs don't change][], in the real world not all URLs are cool. Sometimes
  you will need to reorganize your site to accommodate changes and files will
  move. So we use [URIs, but not necessarily URLs][]. The system will generate a
  UUID for every asset it needs to track.

archetype-key (**required** **automatic**)
: The archetype key is the S3 key within the bucket where the archetype may be
  found. This value is automatically generated by the system, and cannot be
  manually set. It is not especially useful within the archetype record, but it
  is necessary for index records.

asset-key (**required** **automatic**)
: The asset key is the S3 key within the bucket where the (main) content asset
  for this archetype may be found. This value is automatically generated by the
  system, and cannot be manually set. Note, however, that the system can store
  archetypes for assets it does not manage. In that case, the asset-key would be
  the URL of the asset.

content-type (**required**)
: The Internet MIME type describing the format of the asset, e.g. "text/html".
  This value is needed for all web assets so that browsers know how to display
  them.

asset-type (**required**)
: In many circumstances our system will need to know what type an asset
  is. This can be used to look up a schema for validation, or to select a 
  layout template for presentation. This is separate from the content-type (e.g.
  "image/jpeg"), because the asset-type can imply something about the role of
  the asset as well as its format (is that image a company logo, or a profile
  photo?).

title (alias: name; **required**)
: Just as the system needs a handle, so do the humans using the system. The
  title serves as the human-readable representation of the asset in lists and
  any point of display within the system where a short handle is needed. For
  content items (which become web pages) this is the page title.

author
: We use the author field to ensure proper attribution. This field is not
  required, because there are many cases where the author is unknown, anonymous,
  or does not want attribution, but best practice is to populate this field.

copyright (**required**)
: We track the copyright details to ensure proper attribution, and to track
  permissions for assets that came from third parties. If you do not know the
  copyright status of an asset, you have no business publishing it on your
  website, and in doing so you might break the law!

description (alias: summary)
: Practically all of our metadata standards provide for a summary, description,
  or abstract, some small bit of text that gives a reader some idea of what the
  asset contains. We use the term "description" internally. This field is not
  required, but is strongly encouraged to be populated.

published (alias: date; **required**)
: The published field indicates the datetime when the asset was first published
  (that is, made available to the public). This is required because almost every
  view of web content takes this into account. Lists are typically sorted in a
  reverse chronological order, search engines are more interested in recent
  content, and readers like to know how up-to-date is the content they are
  reading.

updated (**required**)
: The updated field indicates the datetime of the last significant editorial
  update. We have made it required, but we will automatically populate it with
  the published date if it is not explicitly provided. It is typically used to
  indicate a correction or addition to the content that makes it worthy of a
  second look, even if a reader saw the original before the update.

created
: The created date indicates the date when the asset was created, as opposed to
  when it was published. This distinction is useful for some asset types, such
  as photographs, where the date the photograph was taken is perhaps more
  interesting than the date it was posted to the web. It is not required,
  because many asset types do not need to make such a distinction.

A note on date fields: there is a seemingly infinite number of potential events
in the lifecycle of an asset that might warrant tracking by date and time. The
core fields we selected above are include because they are commonly accepted
across multiple metadata standards, and they are frequently used or expected by
readers and external systems. Internally, our system should keep an *event log*
that tracks individual events for audit purposes. An event log is much more
useful than simple metadata labels, because it allows us to capture all actions,
not just the most recent (an asset might be published, the *unpublished*, then
published again).

The above is a pretty good start at a core metadata vocabulary for our assets.
In future, we may extend the core if needed. Certainly, we will expand upon it
to add additional metadata for specific types of assets.  Always, when we need
to expand our metadata vocabulary, we will return to our standards spreadsheet
to ensure we are being as compatible as possible with the broader web.

Because web standards are our instruction manual, we want to store our metadata
in a standard format. I chose JSON. I could have chosen XML, but JSON
is easier to work with in JavaScript, and that will come in handy later when we
want to expose our data directly to the browser as a kind of API. To ensure the
integrity of our data, we will create a [JSON Schema][] to validate our core
metadata, and any additional asset types we define.

## Structure of an Archetype

The JSON structure of an archetype is arranged in such a way that it can both be
validated and extended. For each step of the item type hierarchy, a top-level
key is created to hold metadata for that specific type. Each of these top level
keys will have a corresponding schema to validate it.

Example:

    {
        "item": {
            "guid": "asdf",
            "archetype-key": "index.html",
            "asset-key": "asdf.htm",
            "content-type": "text/html; charset=utf-8",
            "asset-type": "Page",
            "title": "Site Home Page",
            "copyright": "2016 Vince Veselosky. CC-BY-SA",
            "published": "2016-05-11T16:00Z",
            "updated": "2016-05-11T16:00Z"
        },
        "item/Page": {
            "image": {"src":"/site-logo.jpg", alt="Site Logo"}
        }
    }

[spreadsheet comparing various metadata standards]: https://docs.google.com/spreadsheets/d/1RjlgDBhFIl8uFsZPqz9pD4slwg1H_yJ6ZxApWxcD52Q/edit?usp=sharing

[Dublin Core]: http://dublincore.org/documents/dcmi-terms/
[OpenGraph Protocol]: http://ogp.me/
[Schema.org]: https://schema.org/
[RSS2]: http://www.rssboard.org/rss-specification
[Atom]: http://tools.ietf.org/html/rfc4287
[Microformats2]: http://microformats.org/wiki/microformats-2
[cool URLs don't change]: https://www.w3.org/Provider/Style/URI
[URIs, but not necessarily URLs]: https://www.w3.org/TR/uri-clarification/
[JSON Schema]: http://json-schema.org/
