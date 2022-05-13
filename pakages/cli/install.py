__author__ = "Vanessa Sochat, Alec Scott"
__copyright__ = "Copyright 2021-2022, Vanessa Sochat and Alec Scott"
__license__ = "Apache-2.0"

from pakages.client import PakClient
from .helpers import parse_package_request


def main(args, parser, extra, subparser):
    cli = PakClient(args.settings_file)

    # Get list of packages and (optionally) repository
    packages, repo = parse_package_request(args)

    # Finally, add the repository and install packages
    if repo:
        cli.add_repository(repo.repo_dir)
    cli.install(args.packages, registry=args.registry, tag=args.tag)
