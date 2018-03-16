# Licensed under the Apache License, Version 2.0 (the “License”); you may not
# use this file except in compliance with the License. You may obtain a copy of
# the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an “AS IS” BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations under
# the License.

import re

# Returns the position for the first non whitespace character or the region’s
# beginning if none is found.
def search_non_whitespace(view, region, stop_on_line_feed = True):
  def __predicate(view, offset):
    char = view.substr(offset)
    if stop_on_line_feed and char == '\n':
      return False
    return char.isspace()

  begin = region.begin()
  end = region.end() - 1

  if end < begin:
    end = begin

  result = scan(view, begin, __predicate, end) + 1
  if result > end:
    result = begin

  return result

def search_scope(view, offset, pattern):
  scopes = view.scope_name(offset)
  matched = re.search(pattern, scopes)
  return None if matched is None else matched.group(0)
