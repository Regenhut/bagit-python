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

#: Package docstring, also used as the description of the command-line help:
PACKAGE_DOC = _(
    """
BagIt is a directory, filename convention for bundling an arbitrary set of
files with a manifest, checksums, and additional metadata. More about BagIt
can be found at:

    http://purl.org/net/bagit

bagit.py is a pure python drop in library and command line tool for creating,
and working with BagIt directories.


Command-Line Usage:

Basic usage is to give bagit.py a directory to bag up:

    $ bagit.py my_directory

This does a bag-in-place operation where the current contents will be moved
into the appropriate BagIt structure and the metadata files will be created.

You can bag multiple directories if you wish:

    $ bagit.py directory1 directory2

Optionally you can provide metadata which will be stored in bag-info.txt:

    $ bagit.py --source-organization "Library of Congress" directory

You can also select which manifest algorithms will be used:

    $ bagit.py --sha1 --md5 --sha256 --sha512 directory


Using BagIt from your Python code:

    import bagit
    bag = bagit.make_bag('example-directory', {'Contact-Name': 'Ed Summers'})
    print(bag.entries)

For more information or to contribute to bagit-python's development, please
visit %(PROJECT_URL)s
"""
) % {"PROJECT_URL": PROJECT_URL}

CHECKSUM_ALGOS = hashlib.algorithms_guaranteed
DEFAULT_CHECKSUMS = ["sha256", "sha512"]

#: Block size used when reading files for hashing:
HASH_BLOCK_SIZE = 512 * 1024

#: Convenience function used everywhere we want to open a file to read text
#: rather than undecoded bytes:
open_text_file = partial(open, encoding="utf-8", errors="strict")
