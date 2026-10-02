"""Reading and writing tag files such as bagit.txt and bag-info.txt."""

import os
import re

from ._common import _, open_text_file
from .errors import BagValidationError


def _load_tag_file(tag_file_name, encoding="utf-8-sig"):
    """Read a tag file into a dict; repeated tags become lists."""
    with open_text_file(tag_file_name, "r", encoding=encoding) as tag_file:
        # Store duplicate tags as list of vals
        # in order of parsing under the same key.
        tags = {}
        for name, value in _parse_tags(tag_file):
            if name not in tags:
                tags[name] = value
                continue

            if not isinstance(tags[name], list):
                tags[name] = [tags[name], value]
            else:
                tags[name].append(value)

        return tags


def _parse_tags(tag_file):
    """Parses a tag file, according to RFC 2822.  This
    includes line folding, permitting extra-long
    field values.

    See http://www.faqs.org/rfcs/rfc2822.html for
    more information.
    """

    tag_name = None
    tag_value = None

    # Line folding is handled by yielding values only after we encounter
    # the start of a new tag, or if we pass the EOF.
    for num, line in enumerate(tag_file):
        # Skip over any empty or blank lines.
        if len(line) == 0 or line.isspace():
            continue
        elif line[0].isspace() and tag_value is not None:  # folded line
            tag_value += line
        else:
            # Starting a new tag; yield the last one.
            if tag_name:
                yield (tag_name, tag_value.strip())

            if ":" not in line:
                raise BagValidationError(
                    _("%(filename)s contains invalid tag: %(line)s")
                    % {
                        "line": line.strip(),
                        "filename": os.path.basename(tag_file.name),
                    }
                )

            parts = line.strip().split(":", 1)
            tag_name = parts[0].strip()
            tag_value = parts[1]

    # Passed the EOF.  All done after this.
    if tag_name:
        yield (tag_name, tag_value.strip())


def _make_tag_file(bag_info_path, bag_info):
    """Write a dict of tags (values may be lists) as a sorted tag file."""
    headers = sorted(bag_info.keys())
    with open_text_file(bag_info_path, "w") as f:
        for h in headers:
            values = bag_info[h]
            if not isinstance(values, list):
                values = [values]
            for txt in values:
                # strip CR, LF and CRLF so they don't mess up the tag file
                txt = re.sub(r"\n|\r|(\r\n)", "", str(txt))
                f.write("%s: %s\n" % (h, txt))
