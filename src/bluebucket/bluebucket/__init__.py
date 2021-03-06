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
"""
This bluebucket module is a library of functions and classes factored out from
the Blue Bucket Project Lambda function handlers.

For fields expecting a resourcetype, valid resourcetype values are:
    [None, 'archetype', 'artifact', 'asset', 'config']

"""
from __future__ import absolute_import, print_function, unicode_literals
from .__about__ import *  # noqa

