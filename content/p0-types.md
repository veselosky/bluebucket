# Content types and metadata attributes

## Content types vs Item types

The term "content type" seems natural to use in a content publishing system, but
it can get overused. The HTTP header field of the same name defines the MIME
type of the HTTP message payload, and we want to preserve that data. But there
is also a higher-order "type." An item could be an Article, an Event, a Person,
a Photo Gallery, a Shared Link, and so on. To reduce confusion, we will refer to
this level of type as "item type" and reserve "content type" to refer to the
MIME type.

For the first phase of our project we will focus on implementing just a simple
Article item type. Later, we will extend the Blue Bucket project to support
additional item types.

## Metadata

Here's a little secret about content management systems: they don't actually
spend much of their time and effort managing content. In real life, mostly what
they manage is *metadata* about the content that they manage. One of the things
that makes content management systems so complex is that nobody seems to be able
to agree on *what* metadata should be managed. As a result, every system for
managing content seems to reinvent the metadata wheel in a slightly different
way from the previous one, and every organization has its own subtle
customizations it wants for its own implementation.

For our system, following the mantra that web standards are our instruction
manual, we turn to standards to define our metadata scheme. Unfortunately (or
fortunately) there is no single standard that is universally applied, but there
are many which are broadly adopted. As it happens, I have done a fairly
extensive study of such schemes in my work, and I put together this [spreadsheet
comparing various metadata standards][].

Some key standards that any web publishing system should be aware of are these.

* [Dublin Core][]: This metadata vocabulary is widely used on the web, both in
  HTML and as an XML namespace in RSS feeds.
* [OpenGraph Protocol][]: Introduced by Facebook, this metadata vocabulary is
  used by social media sites to improve discovery and presentation of content.
* [Schema.org][]: This metadata vocabulary is used by web search engines to
  improve discovery and presentation of content in search results pages.
* [RSS2][]: The de facto standard syndication format used by many blog engines.
* [Atom][]: An alternate syndication format used by blog engines.
* [Microformats2][]: An ad hoc vocabulary for encoding metadata into HTML.

 From that, I culled the common parts and things I know from experience will be
 needed. Then, I pared the list down to the essentials to support the
 functionality in our first two phases of development for Blue Bucket.

The result is the following short list. We will extend this list of supported
metadata fields in later phases of the project.

* author
* category (alias: section)
* description (alias: summary)
* guid (alias: id, identifier)
* itemtype
* published (alias: date)
* title (alias: name)
* updated

This is a pretty good start at a metadata vocabulary, which we will extend later
as we need to. Always, when we need to expand our metadata vocabulary, we will
return to our standards spreadsheet.

Because web standards are our instruction manual, we want to store the
archetypes in a standard format. I chose JSON. I could have chosen XML, but JSON
is easier to work with in JavaScript, and that will come in handy later if we
want to expose our archetypes to the browser as a kind of API.

[spreadsheet comparing various metadata standards]: https://docs.google.com/spreadsheets/d/1RjlgDBhFIl8uFsZPqz9pD4slwg1H_yJ6ZxApWxcD52Q/edit?usp=sharing

[Dublin Core]: http://dublincore.org/documents/dcmi-terms/
[OpenGraph Protocol]: http://ogp.me/
[Schema.org]: https://schema.org/
[RSS2]: http://www.rssboard.org/rss-specification
[Atom]: http://tools.ietf.org/html/rfc4287
[Microformats2]: http://microformats.org/wiki/microformats-2

