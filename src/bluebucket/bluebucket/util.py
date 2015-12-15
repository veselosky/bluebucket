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
from io import BytesIO
from gzip import GzipFile

import datetime
import json


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


def gzip(content, filename=None, compresslevel=9, mtime=None):
    gzbuffer = BytesIO()
    gz = GzipFile(filename, 'wb', compresslevel, gzbuffer, mtime)
    gz.write(content)
    gz.close()
    return gzbuffer.read()


def gunzip(gzcontent):
    gzbuffer = BytesIO(gzcontent)
    return GzipFile(None, 'rb', fileobj=gzbuffer).read()
