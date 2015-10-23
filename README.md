# The Blue Bucket Project: #NoCMS

| | 
| ------------- | ---------------------------------------
| Title:        | The Blue Bucket Project
| Description:  | Cloud-powered web publishing system
| Status:       | Planning — No code available yet.

![Lolrus says I has a bukkit! Nooo they be stealin mah bukkit!](http://i1.kym-cdn.com/photos/images/original/000/000/026/lolrus.jpg)

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

## Copyright and License

Software in the Blue Bucket Project is Licensed under the Apache License,
Version 2.0 (the "License"); you may not use it except in compliance with the
License. You may obtain a copy of the License at

   [http://www.apache.org/licenses/LICENSE-2.0](http://www.apache.org/licenses/LICENSE-2.0)

Unless required by applicable law or agreed to in writing, software distributed
under the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR
CONDITIONS OF ANY KIND, either express or implied.  See the License for the
specific language governing permissions and limitations under the License.

Non-software content in the Blue Bucket Project is licensed under a <a rel="license" href="http://creativecommons.org/licenses/by-sa/4.0/">Creative Commons Attribution-ShareAlike 4.0 International License</a>.


[Indieweb]: https://en.wikipedia.org/wiki/IndieWeb
[open source software]: https://en.wikipedia.org/wiki/Open-source_software
[progressive enhancement]: https://en.wikipedia.org/wiki/Progressive_enhancement
[REST]: https://en.wikipedia.org/wiki/Representational_state_transfer
[static site generation]: https://en.wikipedia.org/wiki/Static_web_page
[systems theory]: https://en.wikipedia.org/wiki/Systems_theory
[cloud computing]: https://en.wikipedia.org/wiki/Cloud_computing
