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

import os
import re
import sys

from ..region import *
from sublime_plugin import TextCommand

def comment_block(view, edit, region):
  begin = region.begin()
  end = region.end()
  empty_region = False

  if begin == end and view.substr(begin).isspace():
    # Added to ensure that the cursor won’t be moved after the comment.
    view.replace(edit, Region(end), '!')
    empty_region = True

  comment_type = resolve_required_comment_type(view, begin)

  if comment_type == 'jsx':
    if empty_region:
      view.insert(edit, end, " */}")
      view.erase(edit, Region(end, end))
    else:
      view.insert(edit, end, " */}")

    view.insert(edit, begin, "{/* ")
  else:
    if empty_region:
      view.insert(edit, end, " */")
      view.erase(edit, Region(end, end))
    else:
      view.insert(edit, end, " */")

    view.insert(edit, begin, "/* ")

def comment_lines(view, edit, region):
  lines = view.lines(region)

  # Calculate the margin.
  margin = sys.maxsize
  for line in lines:
    margin = min(
      search_non_whitespace(view, line) - line.begin(),
      margin
    )

  # Analyse the type of comment that must be used for the entire block.
  first_line = lines[0]
  comment_type = resolve_required_comment_type(view, first_line.begin() + margin)

  # Comment.
  for line in reversed(lines):
    begin = line.begin() + margin
    end = max(line.end(), begin)
    empty_line = False

    if begin == end and view.substr(begin).isspace():
      # Added to ensure that the cursor won’t be moved after the comment.
      view.replace(edit, Region(end), '!')
      empty_line = True

    if comment_type == 'jsx':
      # JSX.
      if empty_line:
        view.insert(edit, end, " */}")
        view.erase(edit, Region(end, end))
      else:
        view.insert(edit, end, " */}")

      view.insert(edit, begin, "{/* ")
    else:
      # Normal JS comment.
      view.insert(edit, begin, "// ")

# Returns true if the region must be commented or not.
def must_comment(view, region):
  non_whitespace_pos = search_non_whitespace(view, region, stop_on_line_feed = False)

  # The entire line is blank, a comment must be inserted in the region.
  if is_whitespace(view, non_whitespace_pos):
    return True

  # If it is the JSX open brace, we just need to check the next character.
  if is_jsx_open_brace(view, non_whitespace_pos):
    non_whitespace_pos += 1

  # If the cursor is at a comment, it means that the user wants to remove it.
  return not is_comment(view, non_whitespace_pos)

# Returns the comment type that must be applied calculed at the offset.
def resolve_required_comment_type(view, offset):
  scopes = view.scope_name(offset)

  unfenced_scopes = [ 'source.jsx', 'punctuation.definition.tag.begin' ]
  unfenced_tag = all(x in scopes for x in unfenced_scopes) and 'meta.jsx-fence' not in scopes

  meta_tag_scopes = [ 'source.jsx', 'meta.tag' ]
  meta_tag = all(x in scopes for x in meta_tag_scopes)

  comment_type = 'js'
  if unfenced_tag or ('source.jsx' in scopes and not meta_tag):
    comment_type = 'jsx'

  return comment_type

def uncomment_region(view, edit, region):
  begin = region.begin()
  end = region.end() - 1

  # We will loop backwards, this means that it will hit the closing punctuation
  # for block comments first.
  i = end + 1
  while i > begin:
    i -= 1
    scopes = view.scope_name(i)

    # Not a punctuation, ignore it.
    if 'punctuation.definition.comment' not in scopes:
      continue

    # Found the second forward slash for the “// ” comment.
    if 'comment.line' in scopes:
      punctuation_region = generate_comment_punctuation_region(view, i)
      view.erase(edit, punctuation_region)
      i = punctuation_region.begin()
      continue

    # We found the beginning of the block comment first, this means that there’s
    # no end to it and we can easily remove it. It can be “/* ”, “/** ”, “{/* ”
    # or “{/** ”.
    if 'punctuation.definition.comment.begin' in scopes:
      punctuation_region = generate_jsjsx_comment_punctuation_region(view, i)
      view.erase(edit, punctuation_region)
      i = punctuation_region.begin()
      continue

    # We are looping backwards, so it is expected to find the closing punctuation
    # first which can be “ */” or “ */}”.
    possible_jsx_comment = False
    if i < view.size() and is_jsx_close_brace(view, i + 1):
      possible_jsx_comment = True

    closing_punctuation_region = generate_comment_punctuation_region(view, i)

    # Move the cursor 1 character after the beginning punctuation.
    i = scan_reverse(view, i, not_predicate(has_scope_predicate(
      'punctuation.definition.comment.begin'
    )))

    open_punctuation_region = generate_comment_punctuation_region(view, i - 1)

    # Correct the regions to include the JSX braces if necessary.
    if possible_jsx_comment:
      if is_jsx_open_brace(view, open_punctuation_region.begin() - 1):
        open_punctuation_region = Region(
          open_punctuation_region.begin() - 1,
          open_punctuation_region.end()
        )
        closing_punctuation_region = Region(
          closing_punctuation_region.begin(),
          closing_punctuation_region.end() + 1
        )

    view.erase(edit, closing_punctuation_region)
    view.erase(edit, open_punctuation_region)

    # Move the cursor to the beginning of the block to “consume” it.
    i = open_punctuation_region.begin()

# Actual command to toggle the comment lines and blocks.
class NaomiToggleJsxCommentCommand(TextCommand):
  def __init__(self, view):
    self.view = view

  def run(self, edit, block):
    view = self.view

    # Expand regions.
    expanded_regions = []
    for region in self.view.sel():
      scopes = self.view.scope_name(region.begin())
      expanded = expand_partial_comments_with_jsx(view, region)
      expanded_regions.append(expanded)

    # Consolidate regions.
    consolidated_regions = []
    previous_region = None

    for region in expanded_regions:
      if previous_region is None:
        previous_region = region
        continue

      if previous_region.intersects(region):
        previous_region.cover(region)
        continue

      consolidated_regions.append(previous_region)
      previous_region = region

    consolidated_regions.append(previous_region)

    # Toggle comments.
    for region in reversed(consolidated_regions):
      region = trim_region(view, region)

      if not must_comment(view, region):
        uncomment_region(view, edit, region)
        continue

      # This will allow the cursor to be in the middle of the string and still
      # detect correctly if it is possible to comment the region.
      if not block:
        region = expand_partial_lines(view, region)

      # If the beginning of the region is a string but not the beginning of the
      # string, it’ll not be possible to comment this region.
      scopes = view.scope_name(region.begin())

      if 'string' in scopes:
        if 'punctuation.definition.string.begin' not in scopes:
          continue

      # Block comments.
      if block:
        comment_block(view, edit, region)
      else:
      # Line comments.
        comment_lines(view, edit, region)
