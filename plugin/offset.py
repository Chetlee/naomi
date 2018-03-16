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

def has_any_scope(view, offset, target_scopes):
  scopes = view.scope_name(offset)
  return any(x in scopes for x in target_scopes)

def has_all_scopes(view, offset, target_scopes):
  scopes = view.scope_name(offset)
  return all(x in scopes for x in target_scopes)

def is_comment(view, offset):
  comment_scopes = [ 'comment.block', 'comment.line' ]
  scopes = view.scope_name(offset)
  return any(x in scopes for x in comment_scopes)

def is_offset_valid(view, offset):
  return 0 <= offset <= view.size() - 1
