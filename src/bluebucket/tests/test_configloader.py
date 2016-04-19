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

# The configloader is responsible for translating a generic dictionary of
# configuration options into usable configuration data for the app. This
# involves setting some default values when fields are missing, and transforming
# some simple strings into more complex Python objects.

###############################################################################
# Load configuration, and set properties based on the configuration.
###############################################################################

# Given config data containing no time zone,
# When I ask for the timezone property,
# Then zone defaults to UTC


# Given config data containing a time zone,
# When I ask for the timezone property,
# Then zone is a correct timezone object


# Given config data containing an invalid time zone string,
# When I ask for the timezone property,
# Then zone defaults to UTC


# Given config data containing unknown keys
# When I inspect the config dict
# Then all input keys are found


# Given config data containing "scribes" as a list of strings each naming a
# module
# When I inspect the config dict
# Then each scribe string will be the loaded module object


