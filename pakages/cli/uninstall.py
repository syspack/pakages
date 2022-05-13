__author__ = "Vanessa Sochat, Alec Scott"
__copyright__ = "Copyright 2021-2022, Vanessa Sochat and Alec Scott"
__license__ = "Apache-2.0"

from pakages.client import PakClient


def main(args, parser, extra, subparser):
    cli = PakClient(args.settings_file)
    cli.uninstall(args.packages)
