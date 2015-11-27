# Goals of the Blue Bucket Project

## Why Bother?

Does the world really need yet another CMS? I think it does.

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

With Blue Bucket, I'm aiming to prove that the combination of *simple* open
source software components, pay-as-you-go cloud services, and good system
design, can produce a very scalable, very low-cost publishing system. That
system can be simple enough that it can replace static site generators or
Wordpress, and scalable enough that it can replace the high-end commercial
systems used at large media companies.

## Hypothesis

1. Static generation of browser assets at publish time is superior to dynamic
   generation at request time, in reliability and cost.
2. Digital infrastructure has reached utility scale. Organizations will save
   both time and money leveraging cloud services rather than running their own
   servers and software (like connecting to the grid vs generating your own
   electricity).

### Classic CMS vs Blue Bucket

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

## Phase 3

In phase 3 we will add a publishing API to our system, so that we can use tools
aside from our command line client to get content into our Library. Importantly,
we want to be able to use generic tools, without giving them access to our AWS
credentials. We do, however, want to restrict access to authorized curators, so
we will provide an authentication system.

## Phase 4

With the publishing API in place, we will use it to add some friendlier content
production tools to our system, and we will start to look a little less like a
traditional static site generator, and a little more like a traditional CMS.

## And beyond...

If we make it through the above phases successfully, we'll set some new goals
and keep moving forward.

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

