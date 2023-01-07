__author__ = "Vanessa Sochat, Alec Scott"
__copyright__ = "Copyright 2021-2023, Vanessa Sochat and Alec Scott"
__license__ = "Apache-2.0"

from pakages.client import get_client
from pakages.logger import logger


def main(args, parser, extra, subparser):
    cli = get_client(builder=args.builder, settings_file=args.settings_file)

    # Finally, add the repository and install packages
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
        cache.push(args.push)

        # By default, we clean up the build cache, unless a custom cache is used
        if not args.no_cleanup and not args.cache_dir:
            cache.remove()

        # Otherwse, require --no-cleanup and --force
        elif not args.no_cleanup and args.cache_dir and args.force:
            cache.remove()
