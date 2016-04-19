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
import mock
from bluebucket import handle_event
import stubs


###############################################################################
# Dispatch events to the correct scribes
###############################################################################

# Given config containing scribes
# When an event is received that is not a valid S3 event
# Then dispatcher ignores the event without calling any scribe methods
def test_non_s3_event():
    evs = stubs.generate_event(source="not:s3", method="somethingelse")
    ev = evs['Records'][0]
    del(ev['s3'])
    scribe1 = mock.Mock()

    scribe_map = {'.html': [scribe1]}
    archivist = mock.Mock()
    rval = handle_event(scribe_map, ev, None, archivist)
    assert rval == []
    archivist.assert_not_called()
    scribe1.on_save.assert_not_called()
    scribe1.on_delete.assert_not_called()


# Given config containing scribes
# When an event key has an extenstion that is not configured
# Then dispatcher ignores the event without calling any scribe methods
def test_non_configured_extension():
    evs = stubs.generate_event(key='test.notconfigured')
    ev = evs['Records'][0]
    scribe1 = mock.Mock()

    scribe_map = {'.html': [scribe1]}
    archivist = mock.Mock()
    rval = handle_event(scribe_map, ev, None, archivist)
    assert rval == []
    scribe1.on_save.assert_not_called()
    scribe1.on_delete.assert_not_called()


# Given many scribes
# When a save event is received
# Then dispatcher calls on_save() on ALL scribes
def test_on_save():
    evs = stubs.generate_event()
    ev = evs['Records'][0]
    archivist = mock.Mock()
    scribe1 = stubs.fake_scribe(on_save=['scribe1'])
    scribe2 = stubs.fake_scribe(on_save=['scribe2'])
    scribe_map = {'.html': [scribe1, scribe2]}

    rval = handle_event(scribe_map, ev, None, archivist)
    assert rval == ['scribe1', 'scribe2']
    scribe1.on_save.assert_called_once_with(mock.ANY, mock.ANY)
    scribe2.on_save.assert_called_once_with(mock.ANY, mock.ANY)


# Given many scribes
# When a delete event is received
# Then Dispatcher calls scribe.on_delete(key)
def test_on_delete():
    evs = stubs.generate_event(method='ObjectRemoved:Delete')
    ev = evs['Records'][0]
    archivist = mock.Mock()
    scribe1 = stubs.fake_scribe(on_delete=['scribe1'])
    scribe2 = stubs.fake_scribe(on_delete=['scribe2'])
    scribe_map = {'.html': [scribe1, scribe2]}

    rval = handle_event(scribe_map, ev, None, archivist)
    assert rval == ['scribe1', 'scribe2']
    key = ev['s3']['object']['key']
    scribe1.on_delete.assert_called_once_with(mock.ANY, key)
    scribe2.on_delete.assert_called_once_with(mock.ANY, key)


# Given many scribes
# When a save event is received and a scribe raises an exception
# Then dispatcher calls on_save() on ALL scribes
# And the output reflects actions for all scribes that succeeded
def test_scribe_raises_exception_on_save():
    evs = stubs.generate_event()
    ev = evs['Records'][0]
    archivist = mock.Mock()
    scribe0 = stubs.fake_scribe(on_save=['scribe0'])
    scribe1 = stubs.fake_scribe(on_save=Exception('FAIL'))
    scribe2 = stubs.fake_scribe(on_save=['scribe2'])
    scribe_map = {'.html': [scribe0, scribe1, scribe2]}

    rval = handle_event(scribe_map, ev, None, archivist)
    assert rval == ['scribe0', 'scribe2']
    scribe0.on_save.assert_called_once_with(mock.ANY, mock.ANY)
    scribe1.on_save.assert_called_once_with(mock.ANY, mock.ANY)
    scribe2.on_save.assert_called_once_with(mock.ANY, mock.ANY)


# Given many scribes
# When a delete event is received and a scribe raises an exception
# Then dispatcher calls on_delete() on ALL scribes
# And the output reflects actions for all scribes that succeeded
def test_scribe_raises_exception_on_delete():
    evs = stubs.generate_event(method='ObjectRemoved:Delete')
    ev = evs['Records'][0]
    archivist = mock.Mock()
    scribe0 = stubs.fake_scribe(on_delete=['scribe0'])
    scribe1 = stubs.fake_scribe(on_delete=Exception('FAIL'))
    scribe2 = stubs.fake_scribe(on_delete=['scribe2'])
    scribe_map = {'.html': [scribe0, scribe1, scribe2]}

    rval = handle_event(scribe_map, ev, None, archivist)
    assert rval == ['scribe0', 'scribe2']
    scribe0.on_delete.assert_called_once_with(mock.ANY, mock.ANY)
    scribe1.on_delete.assert_called_once_with(mock.ANY, mock.ANY)
    scribe2.on_delete.assert_called_once_with(mock.ANY, mock.ANY)

