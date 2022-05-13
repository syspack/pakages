__author__ = "Vanessa Sochat, Alec Scott"
__copyright__ = "Copyright 2021-2022, Vanessa Sochat and Alec Scott"
__license__ = "Apache-2.0"

from pakages.client import PakClient
from pakages.logger import logger
from .helpers import parse_package_request


def main(args, parser, extra, subparser):
    cli = PakClient(args.settings_file)

    # Get list of packages and (optionally) repository
    packages, repo = parse_package_request(args)

    # Finally, add the repository and install packages
    if repo:
        cli.add_repository(repo.repo_dir)
    cache = cli.build(
        args.packages,
        cache_dir=args.cache_dir,
        key=args.key,
        registry=args.registry,
        tag=args.tag,
    )

    # We cannot have both
    if args.push and args.push_trusted:
        logger.exit("Please use only --push or --pushd")

    # Do we want to push to a build cache?
    if args.push or args.push_trusted:
        cache.push(
            args.push,
        )

        # By default, we clean up the build cache, unless a custom cache is used
        if not args.no_cleanup and not args.cache_dir:
            cache.remove()

        # Otherwse, require --no-cleanup and --force
        elif not args.no_cleanup and args.cache_dir and args.force:
            cache.remove()
