"""Hashing helpers: hasher creation, block-wise file hashing and multiprocessing pools."""

import hashlib
import multiprocessing
import os
import signal

from ._common import HASH_BLOCK_SIZE, LOGGER, _
from .errors import BagValidationError


def posix_multiprocessing_worker_initializer():
    """Ignore SIGINT in multiprocessing workers on POSIX systems"""
    signal.signal(signal.SIGINT, signal.SIG_IGN)


def get_hashers(algorithms):
    """
    Given a list of algorithm names, return a dictionary of hasher instances

    This avoids redundant code between the creation and validation code where in
    both cases we want to avoid reading the same file more than once. The
    intended use is a simple for loop:

        for block in file:
            for hasher in hashers.values():
                hasher.update(block)
    """

    hashers = {}

    for alg in algorithms:
        try:
            hasher = hashlib.new(alg)
        except ValueError:
            LOGGER.warning(
                _("Disabling requested hash algorithm %s: hashlib does not support it"),
                alg,
            )
            continue

        hashers[alg] = hasher

    if not hashers:
        raise ValueError(
            _(
                "Unable to continue: hashlib does not support any of the requested algorithms!"
            )
        )

    return hashers


def _multiprocessing_pool_map(func, iterable, processes, initializer=None):
    """Run ``Pool.map()`` and always clean up the pool.

    This ensures worker processes are closed or terminated, then joined, under
    all conditions.
    """
    pool = multiprocessing.Pool(processes=processes, initializer=initializer)
    try:
        results = pool.map(func, iterable)
    except BaseException:
        pool.terminate()
        raise
    else:
        pool.close()
        return results
    finally:
        pool.join()


def _update_hashers(f, hashers):
    """Feed file object f block by block into all hashers; return bytes read."""
    total_bytes = 0
    while True:
        block = f.read(HASH_BLOCK_SIZE)
        if not block:
            break
        total_bytes += len(block)
        for hasher in hashers:
            hasher.update(block)
    return total_bytes


def _calc_hashes(args):
    """Worker: compute hashes of one manifest entry for validation."""
    # auto unpacking of sequences illegal in Python3
    (base_path, rel_path, hashes, algorithms) = args
    full_path = os.path.join(base_path, rel_path)

    # Create a clone of the default empty hash objects:
    f_hashers = {alg: hashlib.new(alg) for alg in hashes if alg in algorithms}

    try:
        f_hashes = _calculate_file_hashes(full_path, f_hashers)
    except BagValidationError as e:
        f_hashes = {alg: str(e) for alg in f_hashers}

    return rel_path, f_hashes, hashes


def _calculate_file_hashes(full_path, f_hashers):
    """
    Returns a dictionary of (algorithm, hexdigest) values for the provided
    filename
    """
    LOGGER.info(_("Verifying checksum for file %s"), full_path)

    try:
        with open(full_path, "rb") as f:
            _update_hashers(f, f_hashers.values())
    except (OSError, IOError) as e:
        raise BagValidationError(
            _("Could not read %(filename)s: %(error)s")
            % {"filename": full_path, "error": str(e)}
        )

    return dict((alg, h.hexdigest()) for alg, h in f_hashers.items())
