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

# Test cases for Scribe
from __future__ import print_function, unicode_literals


###############################################################################
# Test the handle_event logic that dispatches to the specific event handling
# methods. This performs checks against the event itself, without any S3 I/O.
###############################################################################


# Given a Scribe with extensions in accepts_suffixes
# And a key having an extension in accepts_suffixes
# When can_handle_path(key) is called
# Then can_handle_path will return true
def test_suffix_matches():
    from bluebucket.scribe import Scribe
    scribe = Scribe(accepts_suffixes=['.htm', '.html'])
    assert scribe.can_handle_path('index.html')


# Given a Scribe with extensions in accepts_suffixes
# And a key having an extension not in accepts_suffixes
# When can_handle_path(key) is called
# Then can_handle_path will return false
def test_suffix_does_not_match():
    from bluebucket.scribe import Scribe
    scribe = Scribe(accepts_suffixes=['.htm', '.html'])
    assert not scribe.can_handle_path('index.txt')


# Given a Scribe with extensions in accepts_suffixes
# And an object key that has no extension
# When can_handle_path(key) is called
# Then can_handle_path will return false
def test_path_has_no_extension():
    from bluebucket.scribe import Scribe
    scribe = Scribe(accepts_suffixes=['.htm', '.html'])
    assert not scribe.can_handle_path('index')


# Given a Scribe with empty string in accepts_suffixes
# And an object key that has no extension
# When can_handle_path(key) is called
# Then can_handle_path will return true
def test_empty_string_matches_no_extension():
    from bluebucket.scribe import Scribe
    scribe = Scribe(accepts_suffixes=['', '.htm', '.html'])
    assert scribe.can_handle_path('index')


# Given a Scribe with extensions in accepts_prefixes
# And a key having an extension in accepts_prefixes
# When can_handle_path(key) is called
# Then can_handle_path will return true
def test_prefix_matches():
    from bluebucket.scribe import Scribe
    scribe = Scribe(accepts_prefixes=['no/', 'yes/'])
    assert scribe.can_handle_path('yes/index.html')


# Given a Scribe with prefix in accepts_prefixes
# And a key having a prefix not in accepts_prefixes
# When can_handle_path(key) is called
# Then can_handle_path will return false
def test_prefix_does_not_match():
    from bluebucket.scribe import Scribe
    scribe = Scribe(accepts_prefixes=['no/', 'yes/'])
    assert not scribe.can_handle_path('maybe/index.html')

