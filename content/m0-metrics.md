# Key Metrics

In running any web property, there is a set of key internal metrics that you
want to track to understand your system's operational effectiveness. Here's what
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

