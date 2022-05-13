__author__ = "Vanessa Sochat, Alec Scott"
__copyright__ = "Copyright 2021-2022, Vanessa Sochat and Alec Scott"
__license__ = "Apache-2.0"

from pakages.client import PakClient
from pakages.logger import logger


def main(args, parser, extra, subparser):
    cli = PakClient(args.settings_file)
    installed = cli.list_installed()
    if not installed:
        logger.warning("There are no packages installed.")
