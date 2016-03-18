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
from bluebucket.util import is_sequence, gzip, gunzip


#############################################################################
# Test is_sequence
#############################################################################
def test_string_is_sequence():
    assert not is_sequence('test string')


def test_list_is_sequence():
    assert is_sequence(['a list'])


#############################################################################
# Test gzip/gunzip
#############################################################################
def test_gzip_handling():
    text = 'This is my baño. There are many like it but this one is mine.'
    assert text == gunzip(gzip(text.encode('utf-8'))).decode('utf-8')

