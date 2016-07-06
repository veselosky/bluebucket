# vim: set fileencoding=utf-8 :
#
#   Copyright 2015 Vince Veselosky and contributors
#
#   Licensed under the Apache License, Version 2.0 (the "License");
#   you may not use this file except in compliance with the License.
#   You may obtain a copy of the License at
#
#       http://www.apache.org/licenses/LICENSE-2.0
#
#   Unless required by applicable law or agreed to in writing, software
#   distributed under the License is distributed on an "AS IS" BASIS,
#   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#   See the License for the specific language governing permissions and
#   limitations under the License.
#
from __future__ import absolute_import, print_function, unicode_literals
import datetime
from gzip import GzipFile
from io import BytesIO
import json
import posixpath as path
import slugify as sluglib


class SmartJSONEncoder(json.JSONEncoder):
    """
    JSONEncoder subclass that knows how to encode date/time.
    """
    def default(self, o):
        if isinstance(o, datetime.datetime):
            r = o.isoformat()
            if o.microsecond:
                r = r[:23] + r[26:]
            if r.endswith('+00:00'):
                r = r[:-6] + 'Z'
            return r
        elif isinstance(o, datetime.date):
            return o.isoformat()
        elif isinstance(o, datetime.time):
            r = o.isoformat()
            if o.microsecond:
                r = r[:12]
            return r
        else:
            return super(SmartJSONEncoder, self).default(o)


def change_ext(key, ext):
    if not ext.startswith('.'):
        ext = '.' + ext
    return path.splitext(key)[0] + ext


def gzip(content, filename=None, compresslevel=9, mtime=None):
    gzbuffer = BytesIO()
    gz = GzipFile(filename, 'wb', compresslevel, gzbuffer, mtime)
    gz.write(content)
    gz.close()
    return gzbuffer.getvalue()


def gunzip(gzcontent):
    gzbuffer = BytesIO(gzcontent)
    return GzipFile(None, 'rb', fileobj=gzbuffer).read()


def is_sequence(arg):
    return (not hasattr(arg, "strip") and
            (hasattr(arg, "__getitem__") or
            hasattr(arg, "__iter__")))


# Consistent slugify. Lots of stupid edge cases here but whatever. -VV
default_stopwords = ['a', 'an', 'and', 'as', 'but', 'for', 'in', 'is', 'of',
                     'on', 'or', 'than', 'the', 'to', 'with']


def slugify(instring, stopwords=default_stopwords):
    return sluglib.slugify(instring, stopwords=stopwords)

