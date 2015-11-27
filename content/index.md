# Blue Bucket Project: #NoCMS

What if you could eliminate 99% of the cost of running your online presence, and
at the same time make it bulletproof against traffic spikes, software bugs,
infrastructure failures, and most kinds of attacks?

The Blue Bucket Project aims to show that the existing pattern used to build web
content management systems is broken, or at least, that the most common
publishing use cases are better served by a different implementation pattern.
My contention is that traditional dynamic, vertically-integrated content
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
wrong trade-offs in cost and scalability. As a result, small operations may be
paying 100x more than they need to, for a system that is prone to crashing and
vulnerable to denial of service attacks. Large operations are losing millions.

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
worldwide communication capabilities of the web while putting every dollar of of
their limited funds to the most efficient use.

It is a major problem for small enterprises whose business is driven more and
more by digital channels, where downtime or availability problems can have
direct impact on revenues, and IT costs make up a significant portion of
overhead and/or cost of goods sold.

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

## Contents

### Architecture, Design, and Theory of Operation

* [Jobs of an Integrated CMS]()
* [Static Site Generators]()
* [Design of a Static CMS]()
* [Design of a Typical Dynamic CMS]()
* [Common Modifications to the Dynamic Model for Scalability and Reliability]()
* [Blue Bucket architecture](p0-architecture-1.html)
* [Content types and metadata attributes](p0-types.html)

### Methods
* [Implementation Outline](p0-goals.html)
* [AWS Services](m0-aws.html)
* [Key Metrics](m0-metrics.html)

### Phase 1: Archive and Basic Transformation
* [Setting up an S3 bucket as a web site](p1-setup-s3.html)
* A Site Configuration File for Blue Bucket Sites
* Implement a Scribe for YAML->JSON.
* Implement a Scribe for Markdown->JSON.
* Utilities for S3 and Lambda.
* Implement a Scribe that produces HTML using Jinja2 templates.
* Introduce the POSH template set and style sheet.

### Phase 2: Content Index and Site Structure
* Producing a Catalogue of the content.
* Generate a "recently published" index page.
* Generate an Atom/RSS feed.
* Generate a category index page.

