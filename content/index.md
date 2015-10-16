# Blue Bucket Project: #NoCMS

The Blue Bucket Project aims to show that the existing pattern used to build web
content management systems is broken, or at least, that the most common
publishing use cases are better served by a different implementation pattern.
My contention is that traditional, vertically-integrated content management
systems are an anti-pattern for web publishing, and are as much hindrance as
help to publishing operations at many scales.

If new data storage technologies like document stores and column stores contrast
themselves with traditional patterns using the term *NoSQL*, then Blue Bucket
could reasonably apply to itself the term *NoCMS.*

The Blue Bucket Project finds its inspiration at the confluence of the
philosophies of [open source software][] and the [Indieweb][], the techniques of
[progressive enhancement][], [static site generation][], and [cloud computing][]
and architecture inspired by [REST][] and [systems theory][].

Enough buzzwords?

Here are some desired properties of the system:

* Portability is paramount. Users must be able to extract their content at any
  time and abandon the software without losing any data.
* Scalability goes in both directions. The system must aim to perform well at
  very small scale as well as very large scale.
* Composability is valuable. The system should be interoperable with existing
  systems, preserving user choice of tools.

Here are some down-to-earth principles used in Blue Bucket's design:

* Web standards are the instruction manual.
* Cloud services are the magic sauce. Hardware and software are anti-patterns.
  Minimize use of infrastructure and custom code.
* Small pieces, loosely joined, are better than big, complex tools.
* The file system is the canonical repository. Every artifact of the site is
  stored in, or derived from, flat files.
* Generating assets at publish time is almost always better than at request
  time.

I (Vince) put the Blue Bucket Project together to prove out some design
principles I have developed over the course of my career implementing content
management systems. The project has two parts which I am developing in parallel:
the software used to implement the Blue Bucket publishing system, and the
content of the web site that documents the processes and technologies used to
build it. Although I'm not in academia, I think of this project as my
master's thesis.

## Contents

* [Goals of the project](p0-goals.html)
* [High-level architecture](p0-architecture-1.html)
* [A metadata format for Archetypes](p0-archetypes.html)
* [Setting up an S3 bucket as a web site](p1-setup-s3.html)
* Utilities for S3 and Lambda.
* Implement an Archivist for Markdown files.
* Implement a Scribe that produces HTML using Jinja2 templates.
* Introduce the POSH template set and style sheet.
* Producing a Catalogue of the content.
* Generate a "recently published" index page.
* Generate an Atom/RSS feed.
* Generate a category index page.

