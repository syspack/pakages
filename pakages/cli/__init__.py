#!/usr/bin/env python

__author__ = "Vanessa Sochat, Alec Scott"
__copyright__ = "Copyright 2021-2022, Vanessa Sochat and Alec Scott"
__license__ = "Apache-2.0"

import argparse
import os
import sys

import pakages
from pakages.logger import setup_logger


def get_parser():
    parser = argparse.ArgumentParser(
        description="pakages community package manager",
        formatter_class=argparse.RawTextHelpFormatter,
    )

    # Global Variables
    parser.add_argument(
        "--debug",
        dest="debug",
        help="use verbose logging to debug.",
        default=False,
        action="store_true",
    )

    parser.add_argument(
        "--quiet",
        dest="quiet",
        help="suppress additional output.",
        default=False,
        action="store_true",
    )

    parser.add_argument(
        "--version",
        dest="version",
        help="show software version.",
        default=False,
        action="store_true",
    )

    parser.add_argument(
        "--settings-file",
        dest="settings_file",
        help="custom path to settings file.",
    )

    subparsers = parser.add_subparsers(
        help="actions",
        title="actions",
        description="actions",
        dest="command",
    )

    # print version and exit
    subparsers.add_parser("version", description="show software version")

    # Install, Uninstall and Build
    install = subparsers.add_parser(
        "install",
        description="install to the current environment",
        formatter_class=argparse.RawTextHelpFormatter,
    )

    build = subparsers.add_parser(
        "build",
        description="build into a cache",
        formatter_class=argparse.RawTextHelpFormatter,
    )

    build.add_argument(
        "--cache-dir",
        dest="cache_dir",
        help="path to cache directory",
    )

    build.add_argument(
        "--key",
        "-k",
        dest="key",
        help="specify the gpg key hash to use",
    )
    build.add_argument(
        "--push",
        "-p",
        dest="push",
        help="push to a named oras endpoint",
    )
    build.add_argument(
        "--pushd",
        dest="push_trusted",
        action="store_true",
        default=False,
        help="push to default trusted endpoint",
    )
    build.add_argument(
        "--force",
        "-f",
        dest="force",
        action="store_true",
        default=False,
        help="force cleanup of a custom cache directory",
    )
    build.add_argument(
        "--no-cleanup",
        dest="no_cleanup",
        default=False,
        action="store_true",
        help="Given that --push is added, don't clean up the build cache.",
    )

    config = subparsers.add_parser(
        "config",
        description="update configuration settings. Use set or get to see or set information.",
        formatter_class=argparse.RawTextHelpFormatter,
    )
    config.add_argument(
        "--central",
        "-c",
        dest="central",
        help="make edits to the central config file, if a user config is default.",
        default=False,
        action="store_true",
    )

    config.add_argument(
        "params",
        nargs="*",
        help="""Set or get a config value, edit the config, add or remove a list variable, or create a user-specific config.
pakages config set key:value
pakages config get key
pakages edit
pakages config init""",
        type=str,
    )

    # Local shell with client loaded
    shell = subparsers.add_parser(
        "shell",
        description="shell into a Python session with a client.",
        formatter_class=argparse.RawTextHelpFormatter,
    )
    shell.add_argument(
        "--interpreter",
        "-i",
        dest="interpreter",
        help="python interpreter",
        choices=["ipython", "python"],
        default="ipython",
    )

    for command in [install, build]:
        command.add_argument(
            "--registry",
            "-r",
            dest="registry",
            help="registry to use for install or build.",
        )

    for command in [install, build]:
        command.add_argument(
            "--builder",
            "-b",
            dest="builder",
            help="Package builder (default is auto-detect)",
        )
        command.add_argument(
            "--tag",
            "-t",
            dest="tag",
            help="tag to use for build cache retrieval or push",
        )
        command.add_argument(
            "packages", help="build or install these packages", nargs="+"
        )

    return parser


def run_main():
    parser = get_parser()

    def help(return_code=0):
        """print help, including the software version and active client
        and exit with return code.
        """

        version = pakages.__version__

        print("\nSingularity Registry (HPC) Client v%s" % version)
        parser.print_help()
        sys.exit(return_code)

    # If the user didn't provide any arguments, show the full help
    if len(sys.argv) == 1:
        help()

    # If an error occurs while parsing the arguments, the interpreter will exit with value 2
    args, extra = parser.parse_known_args()

    if args.debug is True:
        os.environ["MESSAGELEVEL"] = "DEBUG"

    # Show the version and exit
    if args.command == "version" or args.version:
        print(pakages.__version__)
        sys.exit(0)

    setup_logger(
        quiet=args.quiet,
        debug=args.debug,
    )

    # retrieve subparser (with help) from parser
    helper = None
    subparsers_actions = [
        action
        for action in parser._actions
        if isinstance(action, argparse._SubParsersAction)
    ]
    for subparsers_action in subparsers_actions:
        for choice, subparser in subparsers_action.choices.items():
            if choice == args.command:
                helper = subparser
                break

    if args.command == "build":
        from .build import main
    elif args.command == "config":
        from .config import main
    elif args.command == "install":
        from .install import main
    elif args.command == "shell":
        from .shell import main

    # Pass on to the correct parser
    return_code = 0
    try:
        main(args=args, parser=parser, extra=extra, subparser=helper)
        sys.exit(return_code)
    except UnboundLocalError:
        return_code = 1

    help(return_code)


if __name__ == "__main__":
    run_main()
