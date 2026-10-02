"""Exception classes raised when creating, reading or validating bags."""

from ._common import _


class BagError(Exception):
    """Base class for all bag-related errors."""


class BagValidationError(BagError):
    """Validation failure with an optional list of detail errors."""

    def __init__(self, message, details=None):
        super(BagValidationError, self).__init__()

        if details is None:
            details = []

        self.message = message
        self.details = details

    def __str__(self):
        if len(self.details) > 0:
            details = "; ".join([str(e) for e in self.details])
            return "%s: %s" % (self.message, details)
        return self.message


class ManifestErrorDetail(BagError):
    """Base class for problems with a single manifest entry."""

    def __init__(self, path):
        super(ManifestErrorDetail, self).__init__()

        self.path = path


class ChecksumMismatch(ManifestErrorDetail):
    """A file's computed checksum differs from the manifest value."""

    def __init__(self, path, algorithm=None, expected=None, found=None):
        super(ChecksumMismatch, self).__init__(path)

        self.algorithm = algorithm
        self.expected = expected
        self.found = found

    def __str__(self):
        return _(
            '%(path)s %(algorithm)s validation failed: expected="%(expected)s" found="%(found)s"'
        ) % {
            "path": str(self.path),
            "algorithm": self.algorithm,
            "expected": self.expected,
            "found": self.found,
        }


class FileMissing(ManifestErrorDetail):
    """A file listed in a manifest is missing on disk."""

    def __str__(self):
        return _("%s exists in manifest but was not found on filesystem") % str(
            self.path
        )


class UnexpectedFile(ManifestErrorDetail):
    """A payload file on disk is not listed in any manifest."""

    def __str__(self):
        return _("%s exists on filesystem but is not in the manifest") % self.path


class FileNormalizationConflict(BagError):
    """
    Exception raised when two files differ only in normalization and thus
    are not safely portable
    """

    def __init__(self, file_a, file_b):
        super(FileNormalizationConflict, self).__init__()

        self.file_a = file_a
        self.file_b = file_b

    def __str__(self):
        return _(
            'Unicode normalization conflict for file "%(file_a)s" and "%(file_b)s"'
        ) % {"file_a": self.file_a, "file_b": self.file_b}
