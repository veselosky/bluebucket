# POSH: Plain Old Semantic HTML

Posh is a simple template set for Blue Bucket sites.

Static files that go with the set live in the `project` directory. They should be
copied to the root of your bucket.

Templates are stored under a directory named for the template system. For the
moment, I'm only creating Jinja2 templates, but I'm not in love with any
template system, so in future I would like to try some others. These too should
be copied to your S3 bucket, and its location should be configured in your
bucket configuration.

The tests directory currently contains some rough files for manual testing only.
Someday when it grows up maybe there will be some automated tests.

Note: HTML5 Boilerplate includes several examples of files that will be
site-specific, but should be included in the project. If you don't have some of
these, you waste a lot of bandwidth repeatedly serving 404s for them.  Create
them and let the client cache them for a long time. These include:

* favicon.ico
* apple-touch-icon.png
* browserconfig.xml
* tile.png
* tile-wide.png

