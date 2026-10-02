"""Command-line interface: argument parsing, logging setup and main()."""

import argparse
import logging
import re
import sys

from ._common import CHECKSUM_ALGOS, DEFAULT_CHECKSUMS, LOGGER, PACKAGE_DOC, VERSION, _
from .bag import Bag, make_bag
from .errors import BagError
from .tagfiles import STANDARD_BAG_INFO_HEADERS


class BagArgumentParser(argparse.ArgumentParser):
    """ArgumentParser that collects bag-info metadata in args.bag_info."""

    def __init__(self, *args, **kwargs):
        argparse.ArgumentParser.__init__(self, *args, **kwargs)
        self.set_defaults(bag_info={})


class BagHeaderAction(argparse.Action):
    """Store a --some-header option as 'Some-Header' in namespace.bag_info."""

    def __call__(self, parser, namespace, values, option_string=None):
        opt = option_string.lstrip("--")
        opt_caps = "-".join([o.capitalize() for o in opt.split("-")])
        namespace.bag_info[opt_caps] = values


def _make_parser():
    """Build the command-line argument parser."""
    parser = BagArgumentParser(
        formatter_class=argparse.RawDescriptionHelpFormatter,
        description="bagit-python version %s\n\n%s\n" % (VERSION, PACKAGE_DOC.strip()),
    )
    parser.add_argument(
        "--processes",
        type=int,
        dest="processes",
        default=1,
        help=_(
            "Use multiple processes to calculate checksums faster (default: %(default)s)"
        ),
    )
    parser.add_argument("--log", help=_("The name of the log file (default: stdout)"))
    parser.add_argument(
        "--quiet",
        action="store_true",
        help=_("Suppress all progress information other than errors"),
    )
    parser.add_argument(
        "--validate",
        action="store_true",
        help=_(
            "Validate existing bags in the provided directories instead of"
            " creating new ones"
        ),
    )
    parser.add_argument(
        "--fast",
        action="store_true",
        help=_(
            "Modify --validate behaviour to only test whether the bag directory"
            " has the number of files and total size specified in Payload-Oxum"
            " without performing checksum validation to detect corruption."
        ),
    )
    parser.add_argument(
        "--completeness-only",
        action="store_true",
        help=_(
            "Modify --validate behaviour to test whether the bag directory"
            " has the expected payload specified in the checksum manifests"
            " without performing checksum validation to detect corruption."
        ),
    )

    checksum_args = parser.add_argument_group(
        _("Checksum Algorithms"),
        _("Select the manifest algorithms to be used when creating bags (default=%s)")
        % ", ".join(DEFAULT_CHECKSUMS),
    )

    for i in CHECKSUM_ALGOS:
        alg_name = re.sub(r"^([A-Z]+)(\d+)$", r"\1-\2", i.upper())
        checksum_args.add_argument(
            "--%s" % i,
            action="append_const",
            dest="checksums",
            const=i,
            help=_("Generate %s manifest when creating a bag") % alg_name,
        )

    metadata_args = parser.add_argument_group(_("Optional Bag Metadata"))
    for header in STANDARD_BAG_INFO_HEADERS:
        metadata_args.add_argument(
            "--%s" % header.lower(),
            type=str,
            action=BagHeaderAction,
            default=argparse.SUPPRESS,
        )

    parser.add_argument(
        "directory",
        nargs="+",
        help=_(
            "Directory which will be converted into a bag in place"
            " by moving any existing files into the BagIt structure"
            " and creating the manifests and other metadata."
        ),
    )

    return parser


def _configure_logging(opts):
    """Set up logging according to --quiet and --log."""
    log_format = "%(asctime)s - %(levelname)s - %(message)s"
    if opts.quiet:
        level = logging.ERROR
    else:
        level = logging.INFO
    if opts.log:
        logging.basicConfig(filename=opts.log, level=level, format=log_format)
    else:
        logging.basicConfig(level=level, format=log_format)


def main():
    """Command-line entry point: create or validate the given bags."""
    if "--version" in sys.argv:
        print(_("bagit-python version %s") % VERSION)
        sys.exit(0)

    parser = _make_parser()
    args = parser.parse_args()

    if args.processes <= 0:
        parser.error(_("The number of processes must be greater than 0"))

    if args.fast and not args.validate:
        parser.error(_("--fast is only allowed as an option for --validate!"))

    if args.completeness_only and not args.validate:
        parser.error(
            _("--completeness-only is only allowed as an option for --validate!")
        )

    _configure_logging(args)

    rc = 0
    for bag_dir in args.directory:
        # validate the bag
        if args.validate:
            try:
                bag = Bag(bag_dir)
                # validate throws a BagError or BagValidationError
                bag.validate(
                    processes=args.processes,
                    fast=args.fast,
                    completeness_only=args.completeness_only,
                )
                if args.fast:
                    LOGGER.info(_("%s valid according to Payload-Oxum"), bag_dir)
                elif args.completeness_only:
                    LOGGER.info(
                        _("%s is complete and valid according to Payload-Oxum"), bag_dir
                    )
                else:
                    LOGGER.info(_("%s is valid"), bag_dir)
            except BagError as e:
                LOGGER.error(
                    _("%(bag)s is invalid: %(error)s"), {"bag": bag_dir, "error": e}
                )
                rc = 1

        # make the bag
        else:
            try:
                make_bag(
                    bag_dir,
                    bag_info=args.bag_info,
                    processes=args.processes,
                    checksums=args.checksums,
                )
            except Exception as exc:  # noqa: BLE001 - log it and go on with the next bag
                LOGGER.error(
                    _("Failed to create bag in %(bag_directory)s: %(error)s"),
                    {"bag_directory": bag_dir, "error": exc},
                    exc_info=True,
                )
                rc = 1

    sys.exit(rc)


if __name__ == "__main__":
    main()
