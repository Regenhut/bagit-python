"""Creating manifest and tag manifest files and encoding filenames for them."""

import hashlib
import os
import re
from collections import defaultdict
from functools import partial

from ._common import DEFAULT_CHECKSUMS, LOGGER, _, open_text_file
from .fsutils import _walk
from .hashing import _multiprocessing_pool_map, _update_hashers, get_hashers


def make_manifests(data_dir, processes, algorithms=DEFAULT_CHECKSUMS, encoding="utf-8"):
    """Write payload manifests for data_dir; return (total_bytes, file_count)."""
    LOGGER.info(
        _("Using %(process_count)d processes to generate manifests: %(algorithms)s"),
        {"process_count": processes, "algorithms": ", ".join(algorithms)},
    )

    manifest_line_generator = partial(generate_manifest_lines, algorithms=algorithms)

    if processes > 1:
        checksums = _multiprocessing_pool_map(
            manifest_line_generator, _walk(data_dir), processes=processes
        )
    else:
        checksums = [manifest_line_generator(i) for i in _walk(data_dir)]

    # At this point we have a list of tuples which start with the algorithm name:
    manifest_data = {}
    for batch in checksums:
        for entry in batch:
            manifest_data.setdefault(entry[0], []).append(entry[1:])

    # These will be keyed on the algorithm name so we can perform sanity checks
    # below to catch failures in the hashing process:
    num_files = defaultdict(lambda: 0)
    total_bytes = defaultdict(lambda: 0)

    for algorithm, values in manifest_data.items():
        manifest_filename = "manifest-%s.txt" % algorithm

        with open_text_file(manifest_filename, "w", encoding=encoding) as manifest:
            for digest, filename, byte_count in values:
                manifest.write("%s  %s\n" % (digest, _encode_filename(filename)))
                num_files[algorithm] += 1
                total_bytes[algorithm] += byte_count

    # We'll use sets of the values for the error checks and eventually return the payload oxum values:
    byte_value_set = set(total_bytes.values())
    file_count_set = set(num_files.values())

    # allow a bag with an empty payload
    if not byte_value_set and not file_count_set:
        return 0, 0

    if len(file_count_set) != 1:
        raise RuntimeError(_("Expected the same number of files for each checksum"))

    if len(byte_value_set) != 1:
        raise RuntimeError(_("Expected the same number of bytes for each checksums"))

    return byte_value_set.pop(), file_count_set.pop()


def generate_manifest_lines(filename, algorithms=DEFAULT_CHECKSUMS):
    """Hash one file; return a list of (algorithm, digest, filename, size) tuples."""
    LOGGER.info(_("Generating manifest lines for file %s"), filename)

    # For performance we'll read the file only once and pass it block
    # by block to every requested hash algorithm:
    hashers = get_hashers(algorithms)

    with open(filename, "rb") as f:
        total_bytes = _update_hashers(f, hashers.values())

    decoded_filename = _decode_filename(filename)

    # We'll generate a list of results in roughly manifest format but prefixed with the algorithm:
    results = [
        (alg, hasher.hexdigest(), decoded_filename, total_bytes)
        for alg, hasher in hashers.items()
    ]

    return results


def _make_tagmanifest_file(alg, bag_dir, encoding="utf-8"):
    """Write tagmanifest-<alg>.txt covering all tag files of the bag."""
    tagmanifest_file = os.path.join(bag_dir, "tagmanifest-%s.txt" % alg)
    LOGGER.info(_("Creating %s"), tagmanifest_file)

    checksums = []
    # _find_tag_files() already skips existing tagmanifest-*.txt files
    for f in _find_tag_files(bag_dir):
        with open(os.path.join(bag_dir, f), "rb") as fh:
            m = hashlib.new(alg)
            _update_hashers(fh, (m,))
            checksums.append((m.hexdigest(), f))

    with open_text_file(tagmanifest_file, mode="w", encoding=encoding) as tagmanifest:
        for digest, filename in checksums:
            tagmanifest.write("%s %s\n" % (digest, filename))


def _find_tag_files(bag_dir):
    """Yield relative paths of all tag files (everything except data/ and tagmanifests)."""
    for name in os.listdir(bag_dir):
        if name == "data":
            continue

        # Build every path from bag_dir so that the result does not depend on
        # the current working directory:
        full_path = os.path.join(bag_dir, name)

        if os.path.isfile(full_path) and not name.startswith("tagmanifest-"):
            yield name

        for dir_name, dirnames, filenames in os.walk(full_path):
            for filename in filenames:
                if filename.startswith("tagmanifest-"):
                    continue
                path = os.path.join(dir_name, filename)
                yield os.path.relpath(path, bag_dir)


def _encode_filename(s):
    """Percent-encode CR and LF in a filename for manifest output."""
    s = s.replace("\r", "%0D")
    s = s.replace("\n", "%0A")
    return s


def _decode_filename(s):
    """Decode percent-encoded CR and LF in a manifest filename."""
    s = re.sub(r"%0D", "\r", s, flags=re.IGNORECASE)
    s = re.sub(r"%0A", "\n", s, flags=re.IGNORECASE)
    return s
