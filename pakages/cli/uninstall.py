__author__ = "Vanessa Sochat, Alec Scott"
__copyright__ = "Copyright 2021-2022, Vanessa Sochat and Alec Scott"
__license__ = "Apache-2.0"

from pakages.client import get_client


def main(args, parser, extra, subparser):
    cli = get_client(builder=args.builder, settings_file=args.settings_file)
    cli.uninstall(args.packages)
