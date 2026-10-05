Changelog
=========

This file lists behavior-relevant changes. It starts with the
``refactor/split-into-modules`` branch; nothing before that point has been
backfilled.

Unreleased
----------

Internal restructuring
~~~~~~~~~~~~~~~~~~~~~~~

``bagit.py`` was split from a single file into several modules under
``src/bagit/`` (``bag.py``, ``cli.py``, ``fsutils.py``, ``hashing.py``,
``manifests.py``, ``tagfiles.py``, ``errors.py``, ``_common.py``).
``import bagit`` and the documented public API (``bagit.Bag``,
``bagit.make_bag``, the exception classes, ...) are unaffected. See
"Internal module layout" in README.rst if you patch internal names in your
own tests.

Fixed
~~~~~

- ``Bag.save()`` now restores the process's working directory even if the
  save fails partway through (for example because a tag file is read-only).
  Previously, a failed ``save()`` left the working directory inside the bag
  for the rest of the process's lifetime.
- ``make_bag()`` no longer refuses to bag a directory whose name happens to
  be a prefix of the current working directory's name (e.g. running from a
  sibling directory ``bag2`` while bagging ``bag``).
- The same parent-directory guard in ``make_bag()`` now also works correctly
  when the path to the bag contains a symlink (the working directory is
  always reported with symlinks resolved; the bag path might not be).
- Regenerating tagmanifests (``Bag.save(manifests=True)``) no longer depends
  on the current working directory. Calling it from outside the bag
  directory, or through a symlinked path, previously could silently write an
  empty tagmanifest (dropping checksums for tag files) or raise
  ``FileNotFoundError``.
- The ``DeprecationWarning``\\ s for the deprecated ``checksum=`` argument to
  ``make_bag()``, and for ``Bag.algs`` / ``Bag.version``, now point at the
  calling code instead of ``bagit``'s own internals. Python hides
  ``DeprecationWarning``\\ s that appear to come from library code by
  default, so these were previously invisible to callers.

Changed (affects tests/tooling that patch internals only)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

As a consequence of the module split, values and functions that used to
live in the single ``bagit`` module now have one canonical home that code
elsewhere looks up at call time. If your tests use ``mock.patch`` on any of
these, update the patch target:

======================================  =======================================
Old patch target                        New patch target
======================================  =======================================
``bagit.VERSION``                       ``bagit._common.VERSION``
``bagit.make_bag`` (to affect the CLI)  ``bagit.bag.make_bag``
``bagit.Bag`` (to affect the CLI)       ``bagit.bag.Bag``
======================================  =======================================

Patching ``bagit.make_bag`` / ``bagit.Bag`` directly (not through the CLI)
is unaffected, since ``bagit.make_bag`` and ``bagit.bag.make_bag`` are the
same function object.
