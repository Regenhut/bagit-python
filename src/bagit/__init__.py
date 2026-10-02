from ._common import (
    CHECKSUM_ALGOS,
    DEFAULT_CHECKSUMS,
    HASH_BLOCK_SIZE,
    LOGGER,
    MODULE_NAME,
    PACKAGE_DOC,
    PROJECT_URL,
    TRANSLATION_CATALOG,
    VERSION,
    find_locale_dir,
    open_text_file,
)
from .bag import UNICODE_BYTE_ORDER_MARK, Bag, make_bag
from .cli import BagArgumentParser, BagHeaderAction, main
from .errors import (
    BagError,
    BagValidationError,
    ChecksumMismatch,
    FileMissing,
    FileNormalizationConflict,
    ManifestErrorDetail,
    UnexpectedFile,
)
from .fsutils import build_unicode_normalized_lookup_dict, normalize_unicode
from .hashing import get_hashers, posix_multiprocessing_worker_initializer
from .manifests import generate_manifest_lines, make_manifests
from .tagfiles import STANDARD_BAG_INFO_HEADERS

# The package docstring doubles as the description of the command-line help:
__doc__ = PACKAGE_DOC

# The public API. Names starting with an underscore are internal helpers and
# live in the module that defines them (e.g. bagit.manifests._decode_filename).
# Sorted as ruff's RUF022 expects: constants, then classes, then functions.
__all__ = [
    "CHECKSUM_ALGOS",
    "DEFAULT_CHECKSUMS",
    "HASH_BLOCK_SIZE",
    "LOGGER",
    "MODULE_NAME",
    "PROJECT_URL",
    "STANDARD_BAG_INFO_HEADERS",
    "TRANSLATION_CATALOG",
    "UNICODE_BYTE_ORDER_MARK",
    "VERSION",
    "Bag",
    "BagArgumentParser",
    "BagError",
    "BagHeaderAction",
    "BagValidationError",
    "ChecksumMismatch",
    "FileMissing",
    "FileNormalizationConflict",
    "ManifestErrorDetail",
    "UnexpectedFile",
    "build_unicode_normalized_lookup_dict",
    "find_locale_dir",
    "generate_manifest_lines",
    "get_hashers",
    "main",
    "make_bag",
    "make_manifests",
    "normalize_unicode",
    "open_text_file",
    "posix_multiprocessing_worker_initializer",
]
