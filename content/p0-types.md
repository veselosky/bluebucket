# Archetypes

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
comparing various metadata standards][]. From that, I culled the common parts
and things I know from experience will be needed. The result is the following
(important/common fields in **bold**).

* **author**
* **category (alias: section)**
* contributor
* **description (alias: summary)**
* expires
* **guid (alias: id, identifier)**
* **itemtype**
* language
* leadimage
* **link**
* provider
* **published (alias: date)**
* rights
* **source**
* **title (alias: name)**
* updated

This is a pretty good start at a metadata vocabulary, which we will extend later
as we need to.

Because web standards are our instruction manual, we want to store the
archetypes in a standard format. I chose JSON. I could have chosen XML, but JSON
is easier to work with in JavaScript, and that will come in handy later if we
want to expose our archetypes tot he browser as a kind of API.

[spreadsheet comparing various metadata standards]: https://docs.google.com/spreadsheets/d/1RjlgDBhFIl8uFsZPqz9pD4slwg1H_yJ6ZxApWxcD52Q/edit?usp=sharing
