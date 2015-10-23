# Blue Bucket Architecture Principles

The Blue Bucket architecture principals serve as a decision framework, a guide
to help us design the system correctly. When we need to make a decision about
how (or whether) to do something, we'll refer to these principles to help us
make the right choice.

## Principles

Here are some down-to-earth principles used in Blue Bucket's design:

### Web standards are the instruction manual.

### Cloud services are the magic sauce.
Hardware and software are anti-patterns. Minimize use of infrastructure and custom code.

### Do one thing well.
Small pieces, loosely joined, are better than big, complex tools. Each component
of the system should have only one task, and should perform that task very well.
Also known as the [Single Responsibility Principle][].

### The file system is the canonical repository.
Every artifact of the site is stored in, or derived from, flat files. An end
user should be able to reproduce the entire system given the repository.

* Generating assets at publish time is almost always better than at request
  time.

These are our values, the outcomes we desire from our architecture:

* Portability is paramount. Users must be able to extract their content at any
  time and abandon the software without losing any data.
* Scalability goes in both directions. The system must aim to perform well at
  very small scale as well as very large scale.
* Composability is valuable. The system should be interoperable with existing
  systems, preserving user choice of tools.

[Single Responsibility Principle]: https://en.wikipedia.org/wiki/Single_responsibility_principle
