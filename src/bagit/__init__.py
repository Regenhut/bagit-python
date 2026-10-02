#!/usr/bin/env python
# -*- coding: utf-8 -*-


from ._common import (  # noqa: F401
    CHECKSUM_ALGOS,
    DEFAULT_CHECKSUMS,
    HASH_BLOCK_SIZE,
    LOGGER,
    MODULE_NAME,
    PACKAGE_DOC,
    PROJECT_URL,
    TRANSLATION_CATALOG,
    VERSION,
    _,
    find_locale_dir,
    open_text_file,
)
from .bag import (  # noqa: F401
    UNICODE_BYTE_ORDER_MARK,
    Bag,
    _is_payload_path,
    make_bag,
)
from .cli import (  # noqa: F401
    BagArgumentParser,
    BagHeaderAction,
    _configure_logging,
    _make_parser,
    main,
)
from .errors import (  # noqa: F401
    BagError,
    BagValidationError,
    ChecksumMismatch,
    FileMissing,
    FileNormalizationConflict,
    ManifestErrorDetail,
    UnexpectedFile,
)
from .fsutils import (  # noqa: F401
    _can_bag,
    _can_read,
    _check_permissions,
    _walk,
    build_unicode_normalized_lookup_dict,
    normalize_unicode,
)
from .hashing import (  # noqa: F401
    _calc_hashes,
    _calculate_file_hashes,
    _multiprocessing_pool_map,
    _update_hashers,
    get_hashers,
    posix_multiprocessing_worker_initializer,
)
from .manifests import (  # noqa: F401
    _decode_filename,
    _encode_filename,
    _find_tag_files,
    _make_tagmanifest_file,
    generate_manifest_lines,
    make_manifests,
)
from .tagfiles import (  # noqa: F401
    STANDARD_BAG_INFO_HEADERS,
    _load_tag_file,
    _make_tag_file,
    _parse_tags,
)

# The package docstring doubles as the description of the command-line help:
__doc__ = PACKAGE_DOC
