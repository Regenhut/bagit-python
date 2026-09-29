"""Shared basics used by all bagit modules: translations, logging, version, constants."""

import gettext
import hashlib
import logging
import os
import sys
from functools import partial
from importlib.metadata import version


def find_locale_dir():
    """Return the first existing locale directory next to this module or in sys.prefix."""
    for prefix in (os.path.dirname(__file__), sys.prefix):
        locale_dir = os.path.join(prefix, "locale")
        if os.path.isdir(locale_dir):
            return locale_dir


TRANSLATION_CATALOG = gettext.translation(
    "bagit-python", localedir=find_locale_dir(), fallback=True
)

_ = TRANSLATION_CATALOG.gettext

MODULE_NAME = "bagit"

LOGGER = logging.getLogger(MODULE_NAME)

VERSION = version(MODULE_NAME)
if not VERSION:
    VERSION = "0.0.dev0"

PROJECT_URL = "https://github.com/LibraryOfCongress/bagit-python"

CHECKSUM_ALGOS = hashlib.algorithms_guaranteed
DEFAULT_CHECKSUMS = ["sha256", "sha512"]

#: Block size used when reading files for hashing:
HASH_BLOCK_SIZE = 512 * 1024

#: Convenience function used everywhere we want to open a file to read text
#: rather than undecoded bytes:
open_text_file = partial(open, encoding="utf-8", errors="strict")
