# Notes on Phase 1

At this point we have achieved a very basic static site generator.

## Errors to correct

I can already see that I have factored some things incorrectly in the software
design.

First, I have used the wrong composition strategy with the Scribe class. A
Scribe has too many responsibilities. It inherits two responsibilities from the
base class: I/O, and Event handling. The subclass then adds a third
responsibility, transformation. Because it composes the I/O via inheritance, it
will be difficult later to replace the I/O functions to use a non-S3 archive.

Second, the Phase 1 model makes a bad assumption that a scribe always has
exactly one output. The MarkdownSource scribe proves that scribes can have more
than one output. In the Phase 1 design, that scribe writes a second output to S3
directly inside its transform method. This will completely fail if we decide to
change to a non-S3 archive.

Third, the Phase 1 model assumes that a single scribe can handle a given event.
This comes from commingling the event handling function with the transformation
function. But events from S3 can only be filtered by name, whereas a scribe
filters not just by name but also by artifact. If we want to handle two kinds of
artifacts that have similar file name patterns, we are going to run into
trouble. We use JSON for both configuration data and for archetypes.

We should separate these concerns. An Archivist class should manage the archive
and provide an abstraction layer that can be replaced, so that we can configure
non-S3 archives in the future. The Archivist therefore should not be a
superclass of the Scribe, but a composed member.

## Missing Features

* The Archivist should handle automatic gzip compression and decompression of
  text objects, adding the appropriate metadata headers for browsers, and
  detecting same.
* The Archivist should handle decoding the byte stream to unicode text for text
  objects, because doing read().decode('utf-8') in every transformer just feels
  wrong.
* We still have the problem that we do not attempt to detect encodings other
  than UTF-8. Should we bother? Or just make it a constraint?

## Design Issues

In the old (improperly decomposed) design, the event dispatcher on the Scribe
dispatches to `self`. When factoring out the archivist, the event dispatcher
should move to the archivist (since the event format will vary with the
underlying archive provider). How should the archivist's event dispatcher
discover the scribe's event handlers?
