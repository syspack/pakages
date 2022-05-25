__author__ = "Vanessa Sochat, Alec Scott"
__copyright__ = "Copyright 2021-2022, Vanessa Sochat and Alec Scott"
__license__ = "Apache-2.0"

from pakages.logger import logger
from pakages.client import get_client

def main(args, parser, extra, subparser):
    cli = get_client(builder=args.builder, settings_file=args.settings_file)
    installed = cli.list_installed()
    if not installed:
        logger.warning("There are no packages installed.")
