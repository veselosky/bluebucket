#!/usr/bin/env python
"""
Jinja2 template renderer.

This script will render a jinja2 template to STDOUT. The template context is
constructed from data files fed to the script.

Usage:
    j2.py [options] TEMPLATE [VARFILES...]

Options:
    -r --root ROOT          The path to the "document root" of the web site.
                            Used to calculate relative URLs.
    -t --templatedir DIR    Directory where templates are stored. TEMPLATE
                            path should be relative to this.

Other VARFILES will be merged into the top level template context. They will
be processed in order, so duplicates are last value wins.
"""
from __future__ import absolute_import, print_function, unicode_literals
from docopt import docopt
from os import path

import jinja2
import logging
import yaml

logging.basicConfig(level=logging.INFO)
arguments = docopt(__doc__)
logging.debug(arguments)


def loadfile(filename):
    # json is a subset of yaml, so the yaml parser can handle both! yay!
    try:
        with open(filename) as fp:
            data = yaml.load(fp)
    except yaml.scanner.ScannerError:
        logging.error("Unrecognized file type. Data files must be JSON or YAML.")  # noqa
        exit(1)
    return data


# load up the template context
context = {}

for varfile in arguments['VARFILES']:
    context.update(loadfile(varfile))

docroot = './'
if arguments['--root']:
    docroot = path.abspath(arguments['--root'])

logging.debug(context)
try:
    numslashes = path.relpath(context['path'], docroot).count("/")
    context['siteroot'] = "../" * numslashes
except KeyError:
    pass

# Okay we have our context, now let's load the template
jinja = jinja2.Environment(
    loader=jinja2.FileSystemLoader(arguments['--templatedir'])
)
template = jinja.get_template(arguments['TEMPLATE'])
output = template.render(context)
print(output.encode('utf-8'))
