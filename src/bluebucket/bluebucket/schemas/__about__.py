# vim: set fileencoding=utf-8 :
#
#   Copyright 2016 Vince Veselosky and contributors
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
# BUG in setuptools:
# in Python 2, setuptools hates unicode, requires bytestring args. ugh.
# https://stackoverflow.com/questions/23174738/setup-py-packages-and-unicode-literals
# https://bugs.python.org/issue13943
from __future__ import absolute_import, print_function  # , unicode_literals
__all__ = [
    "__author__",
    "__author_email__",
    "__copyright__",
    "__description__",
    "__license__",
    "__name__",
    "__url__",
    "__version__",
]

__author__ = "Vince Veselosky"
__author_email__ = "vince@veselosky.com"
__copyright__ = "2016 Vince Veselosky and contributors"
__description__ = "JSON Schemas for Blue Bucket architecture"
__license__ = "Apache 2.0"
__name__ = "bluebucket-schemas"
__title__ = "Blue Bucket Schemas"
__url__ = 'https://github.com/veselosky/bluebucket'
__version__ = "0.1.0"

