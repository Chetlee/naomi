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

from ..region import *
from sublime_plugin import TextCommand

# def comment_block(view, edit, region):
#   begin = get_non_whitespace_pos(view, region)
#   end = max(begin, region.end())
#   empty_region = False

#   if begin == end and view.substr(begin).isspace():
#     # Added to ensure that the cursor won’t be moved after the comment.
#     view.replace(edit, Region(end), '!')
#     empty_region = True

#   comment_type = get_comment_type(view, begin)

#   if comment_type == 'jsx':
#     if empty_region:
#       view.insert(edit, end + 1, " */}")
#       view.erase(edit, Region(end, end + 1))
#     else:
#       view.insert(edit, end, " */}")

#     view.insert(edit, begin, "{/* ")
#   else:
#     if empty_region:
#       view.insert(edit, end + 1, " */")
#       view.erase(edit, Region(end, end + 1))
#     else:
#       view.insert(edit, end, " */")

#     view.insert(edit, begin, "/* ")

def comment_lines(view, edit, region):
  lines = view.lines(region)
  first_line = lines[0]
  comment_type = get_comment_type(view, get_non_whitespace_pos(view, first_line))

  for line in reversed(lines):
    begin = get_non_whitespace_pos(view, line)
    end = max(begin, line.end())

    empty_line = False
    if begin == end and view.substr(begin).isspace():
      # Added to ensure that the cursor won’t be moved after the comment.
      view.replace(edit, Region(end), '!')
      empty_line = True

    if comment_type == 'jsx':
      # JSX.
      if empty_line:
        view.insert(edit, end + 1, " */}")
        view.erase(edit, Region(end, end + 1))
      else:
        view.insert(edit, end, " */}")

      view.insert(edit, begin, "{/* ")
    else:
      # Normal JS comment.
      view.insert(edit, begin, "// ")

# def expand_closing_block_punctuation(view, offset):
#   begin = offset
#   end = offset

#   # Expand to the left.
#   scopes = view.scope_name(begin)

#   while begin > 0 and 'punctuation.definition.comment.end' in scopes:
#     begin -= 1
#     scopes = view.scope_name(begin)

#   if view.substr(begin) != ' ':
#     begin += 1

#   # Expand to the right.
#   scopes = view.scope_name(end)

#   while end < view.size() and 'punctuation.definition.comment.end' in scopes:
#     end += 1
#     scopes = view.scope_name(end)

#   return Region(begin, end)

# def expand_edge_lines(view, region):
#   begin = region.begin() - 1
#   end = min(view.size(), region.end() + 1)

#   # Expand to the left.
#   char = view.substr(begin)
#   while begin > 0 and char != '\n':
#     begin -= 1
#     char = view.substr(begin)

#   # Expand to the right.
#   char = view.substr(end)
#   while end < view.size() and char != '\n':
#     end -= 1
#     char = view.substr(end)

#   return Region(begin, end)

# def expand_openning_block_punctuation(view, offset):
#   begin = offset
#   end = offset

#   # Expand to the left.
#   scopes = view.scope_name(begin)

#   while begin > 0 and 'punctuation.definition.comment.begin' in scopes:
#     begin -= 1
#     scopes = view.scope_name(begin)
#   begin += 1

#   # Expand to the right.
#   scopes = view.scope_name(end)

#   while end < view.size() and 'punctuation.definition.comment.begin' in scopes:
#     end += 1
#     scopes = view.scope_name(end)

#   if view.substr(end) == ' ':
#     end += 1

#   return Region(begin, end)

# def expand_partial_comments(view, region):
#   begin = region.begin()
#   end = region.end()

#   # This will allow JSX block comments to be toggled when the cursor is at the
#   # openning or closing brace.
#   if is_jsx_open_brace(view, begin): begin += 1
#   if is_jsx_open_brace(view, end): end += 1

#   if is_jsx_close_brace(view, begin): begin -= 1
#   if is_jsx_close_brace(view, end): end -= 1

#   # Expand to the left.
#   scopes = view.scope_name(begin)

#   if 'comment.line' in scopes:
#     while begin > 0:
#       begin -= 1
#       char = view.substr(begin)
#       scopes = view.scope_name(begin)

#       if char == '\n' or 'comment.line' not in scopes:
#         begin += 1
#         break
#   elif 'comment.block' in scopes:
#     char = view.substr(begin)
#     # It won’t be expaned if it is already at the beginning of the block.
#     if char != '/' or 'punctuation.definition.comment.begin' not in scopes:
#       while begin > 0:
#         begin -= 1
#         char = view.substr(begin)
#         scopes = view.scope_name(begin)

#         if char == '/' and 'punctuation.definition.comment.begin' in scopes:
#           break

#   # Expand to the right.
#   scopes = view.scope_name(end)

#   if 'comment.line' in scopes:
#     char = view.substr(end)
#     # If it’s a new line character, it does not need to be expanded.
#     if char != '\n':
#       while end < view.size():
#         end += 1
#         char = view.substr(end)
#         scopes = view.scope_name(end)

#         if char == '\n':
#           break

#         if 'comment.line' not in scopes:
#           end -= 1
#           break
#   elif 'comment.block' in scopes:
#     char = view.substr(end)
#     # It won’t be expaned if it is already at the end of the block.
#     if char != '/' or 'punctuation.definition.comment.end' not in scopes:
#       while end < view.size():
#         end += 1
#         char = view.substr(end)
#         scopes = view.scope_name(end)

#         if char == '/' and 'punctuation.definition.comment.end' in scopes:
#           end += 1
#           break
#     else:
#       # We are at the end of the block already, this will correct the region to
#       # include the forward slash.
#       end += 1

#   return Region(begin, end)

# Scan from the right to the left.
# def get_comment_beginning_pos(view, offset):
#   scopes = view.scope_name(offset)
#   not_comment_scopes = [ 'comment.line', 'comment.block' ]

#   while offset > 0:
#     comment = any(x in scopes for x in not_comment_scopes)

#     # Not a comment or end of a block comment.
#     if not comment or 'punctuation.definition.comment.end' in scopes:
#       offset += 1
#       break

#     # New line at the end of a line comment.
#     char = view.substr(offset)
#     if char == '\n' and 'comment.line' in scopes:
#       offset += 1
#       break

#     offset -= 1
#     scopes = view.scope_name(offset)

#   return offset

# Scan from the left to the right.
# def get_comment_content_beginning(view, offset):
#   scopes = view.scope_name(offset)
#   while 'punctuation.definition.comment.begin' in scopes:
#     offset += 1
#     scopes = view.scope_name(offset)

#   char = view.substr(offset)

#   # The first space will be considered as part of the punctuation because it
#   # might have been inserted by this script.
#   if char == ' ':
#     offset += 1

#   return offset

# Returns the comment type that must be applied calculed at the offset.
# def get_comment_type(view, offset):
#   scopes = view.scope_name(offset)

#   unfenced_scopes = [ 'source.jsx', 'punctuation.definition.tag.begin' ]
#   unfenced_tag = all(x in scopes for x in unfenced_scopes) and 'meta.jsx-fence' not in scopes

#   meta_tag_scopes = [ 'source.jsx', 'meta.tag' ]
#   meta_tag = all(x in scopes for x in meta_tag_scopes)

#   comment_type = 'js'
#   if unfenced_tag or ('source.jsx' in scopes and not meta_tag):
#     comment_type = 'jsx'

#   return comment_type

# Returns the position for the first non whitespace character on the target line
# or the line’s beginning if none is found.
# def get_non_whitespace_pos(view, region, stop_on_new_line = True):
#   begin = region.begin()
#   end = region.end()

#   while begin < end:
#     char = view.substr(begin)
#     if stop_on_new_line and char == '\n':
#       break
#     if not char.isspace():
#       break
#     begin += 1

#   return begin


# # Returns true if the region must be commented or not.
# def must_comment(view, region):
#   # Comments will begin with “//”, “/*” or “{/*”, to simplify the detection
#   # on the first line, we can ignore the first character.
#   scopes = view.scope_name(get_non_whitespace_pos(view, region) + 1)
#   return 'comment' not in scopes

# def trim_whitespace(view, region):
#   begin = region.begin()
#   end = region.end()

#   # Trim from the left.
#   char = view.substr(begin)
#   while char.isspace():
#     begin += 1
#     char = view.substr(begin)

#   # Trim from the right.
#   char = view.substr(end)
#   while char.isspace():
#     end -= 1
#     char = view.substr(end)

#   # The region got inverted, this means that it contains only whitespace.
#   if begin > end:
#     return region

#   return Region(begin, end + 1)

def uncomment_lines(view, edit, region):
  begin = region.begin()
  end = region.end()

  # We will loop backwards, this means that it will hit the closing punctuation
  # for block comments.
  i = end + 1
  while i > begin:
    i -= 1
    scopes = view.scope_name(i)

    if 'punctuation.definition.comment' not in scopes:
      continue

    # Found the second forward slash for the “// ” comment.
    if 'comment.line' in scopes:
      i = get_comment_beginning_pos(view, i)
      content_begin = get_comment_content_beginning(view, i)
      view.erase(edit, Region(i, content_begin))
      continue

    # We found the beginning of the block comment first which means that there’s
    # no end to it and we can easily remove it. It can be “/* ”, “/** ”, “{/* ”
    # or “{/** ”.
    if 'punctuation.definition.comment.begin' in scopes:
      i = get_comment_beginning_pos(view, i)
      content_begin = get_comment_content_beginning(view, i)

      # We need to check the braces for possible JSX interpolation.
      if i > 0 and is_jsx_open_brace(view, i - 1):
        # It was a JSX block comment.
        i -= 1

      # We have “i” positioned at the beginning of the comment or the brace if
      # it is a JSX comment.
      view.erase(edit, Region(i, content_begin))
      continue

    # We are looping backwards, so it is expected to find the closing punctuation
    # first which can be “ */” or “ */}”.
    possible_jsx_comment = False

    if i < view.size() and is_jsx_close_brace(view, i + 1):
      possible_jsx_comment = True

    close_block = i

    # Now, we need to find the the openning of the block.
    while 'punctuation.definition.comment.begin' not in scopes:
      i -= 1
      scopes = view.scope_name(i)

    open_block = i

    # This will generate a region that allows us to remove the block punctuation.
    open_block = expand_openning_block_punctuation(view, open_block)
    close_block = expand_closing_block_punctuation(view, close_block)

    # Correct the regions to include the JSX braces if necessary.
    if possible_jsx_comment:
      if open_block.begin() > 0 and is_jsx_open_brace(view, open_block.begin() - 1):
        open_block = Region(open_block.begin() - 1, open_block.end())
        close_block = Region(close_block.begin(), close_block.end() + 1)

    view.erase(edit, close_block)
    view.erase(edit, open_block)

    # Move the cursor to the beginning of the block to “consume” it.
    i = open_block.begin()

# Actual command to toggle the comment lines and blocks.
class NaomiToggleJsxCommentCommand(TextCommand):
  def __init__(self, view):
    self.view = view

  def run(self, edit, block):
    view = self.view
    for region in reversed(self.view.sel()):
      scopes = self.view.scope_name(region.begin())

      # If the region is just the cursor and is not in a comment, we will expand
      # it to affect the entire line.
      if region.size() < 1 and 'comment' not in scopes:
        region = expand_partial_lines(view, region)

      # If the beginning of the region is a string but not the beginning of the
      # string, it’ll not be possible to comment this region.
      scopes = self.view.scope_name(region.begin())

      if 'string' in scopes:
        if 'punctuation.definition.string.begin' not in scopes:
          continue

      region = expand_partial_comments_with_jsx(self.view, region)

      print(view.substr(region))

      # # Block comments.
      # if block:
      #   region = trim_whitespace(self.view, region)

      #   if must_comment(self.view, region):
      #     comment_block(self.view, edit, region)
      #   else:
      #     uncomment_lines(self.view, edit, region)

      #   continue

      # # Line comments.
      # region = expand_edge_lines(self.view, region)
      # region = trim_whitespace(self.view, region)

      # if must_comment(self.view, region):
      #   comment_lines(self.view, edit, region)
      # else:
      #   uncomment_lines(self.view, edit, region)
