__author__ = "Vanessa Sochat, Alec Scott"
__copyright__ = "Copyright 2021-2022, Vanessa Sochat and Alec Scott"
__license__ = "Apache-2.0"

from pakages.client import PakClient


def main(args, parser, extra, subparser):
    cli = PakClient(args.settings_file)

    uri = None
    cache_dir = None

    # If we have one argument, if can be either the uri or cache
    if len(args.paths) >= 1:
        if args.paths[0].startswith("ghcr.io"):
            uri = args.paths.pop(0)
        else:
            cache_dir = args.paths.pop(0)

    # Do we still have the other one?
    if args.paths and not uri:
        uri = args.paths.pop(0)
    elif args.paths and not cache_dir:
        cache_dir = args.paths.pop(0)

    # Do we want to push to a build cache?
    cache = cli.push(cache_dir=cache_dir, uri=uri, tag=args.tag)

    # For an explicit push, the cache dir needed to already exist, require --cleanup
    if args.cleanup:
        cache.remove()
