"""Filesystem helpers: directory walking, permission checks, Unicode-normalized names."""

import os
import unicodedata

from ._common import LOGGER, _
from .errors import BagError, FileNormalizationConflict


# The Unicode normalization form used here doesn't matter – all we care about
# is consistency since the input value will be preserved:


def normalize_unicode(s):
    """Return s in Unicode normalization form NFC."""
    return unicodedata.normalize("NFC", s)


def build_unicode_normalized_lookup_dict(filenames):
    """
    Return a dictionary mapping unicode-normalized filenames to as-encoded
    values to efficiently detect conflicts between the filesystem and manifests.

    This is necessary because some filesystems and utilities may automatically
    apply a different Unicode normalization form to filenames than was applied
    when the bag was originally created.

    The best known example of this is when a bag is created using a
    normalization form other than NFD and then transferred to a Mac where the
    HFS+ filesystem will transparently normalize filenames to a variant of NFD
    for every call:

    https://developer.apple.com/legacy/library/technotes/tn/tn1150.html#UnicodeSubtleties

    Windows is documented as storing filenames exactly as provided:

    https://msdn.microsoft.com/en-us/library/windows/desktop/aa365247%28v=vs.85%29.aspx

    Linux performs no normalization in the kernel but it is technically
    valid for a filesystem to perform normalization, such as when an HFS+
    volume is mounted.

    See http://www.unicode.org/reports/tr15/ for a full discussion of
    equivalence and normalization in Unicode.
    """

    output = dict()

    for filename in filenames:
        normalized_filename = normalize_unicode(filename)
        if normalized_filename in output:
            raise FileNormalizationConflict(filename, output[normalized_filename])
        else:
            output[normalized_filename] = filename

    return output


def _walk(data_dir):
    """Yield all file paths below data_dir in sorted order with '/' separators."""
    for dirpath, dirnames, filenames in os.walk(data_dir):
        # if we don't sort here the order of entries is non-deterministic
        # which makes it hard to test the fixity of tagmanifest-md5.txt
        filenames.sort()
        dirnames.sort()
        for fn in filenames:
            path = os.path.join(dirpath, fn)
            # BagIt spec requires manifest to always use '/' as path separator
            if os.path.sep != "/":
                parts = path.split(os.path.sep)
                path = "/".join(parts)
            yield path


def _can_bag(test_dir):
    """Scan the provided directory for files which cannot be bagged due to insufficient permissions"""
    unbaggable = []

    if not os.access(test_dir, os.R_OK):
        # We cannot continue without permission to read the source directory
        unbaggable.append(test_dir)
        return unbaggable

    if not os.access(test_dir, os.W_OK):
        unbaggable.append(test_dir)

    for dirpath, dirnames, filenames in os.walk(test_dir):
        for directory in dirnames:
            full_path = os.path.join(dirpath, directory)
            if not os.access(full_path, os.W_OK):
                unbaggable.append(full_path)

    return unbaggable


def _can_read(test_dir):
    """Return a tuple (unreadable_dirs, unreadable_files) for test_dir."""
    unreadable_dirs = []
    unreadable_files = []

    if not os.access(test_dir, os.R_OK):
        unreadable_dirs.append(test_dir)
    else:
        for dirpath, dirnames, filenames in os.walk(test_dir):
            for dn in dirnames:
                full_path = os.path.join(dirpath, dn)
                if not os.access(full_path, os.R_OK):
                    unreadable_dirs.append(full_path)
            for fn in filenames:
                full_path = os.path.join(dirpath, fn)
                if not os.access(full_path, os.R_OK):
                    unreadable_files.append(full_path)
    return (tuple(unreadable_dirs), tuple(unreadable_files))


def _check_permissions(bag_dir):
    """Raise BagError if bag_dir contains anything not writable or readable."""
    # TODO: These two checks are currently redundant since an unreadable directory will also
    #       often be unwritable, and this code will require review when we add the option to
    #       bag to a destination other than the source. It would be nice if we could avoid
    #       walking the directory tree more than once even if most filesystems will cache it
    unbaggable = _can_bag(bag_dir)
    if unbaggable:
        LOGGER.error(
            _("Unable to write to the following directories and files:\n%s"),
            unbaggable,
        )
        raise BagError(_("Missing permissions to move all files and directories"))

    unreadable_dirs, unreadable_files = _can_read(bag_dir)
    if unreadable_dirs:
        LOGGER.error(
            _("The following directories do not have read permissions:\n%s"),
            unreadable_dirs,
        )
    if unreadable_files:
        LOGGER.error(
            _("The following files do not have read permissions:\n%s"),
            unreadable_files,
        )
    if unreadable_dirs or unreadable_files:
        raise BagError(_("Read permissions are required to calculate file fixities"))
