__author__ = "Vanessa Sochat, Alec Scott"
__copyright__ = "Copyright 2021-2023, Vanessa Sochat and Alec Scott"
__license__ = "Apache-2.0"

from pakages.client import get_client

from .helpers import parse_extra


def main(args, parser, extra, subparser):
    kwargs = parse_extra(extra)
    cli = get_client(builder=args.builder, settings_file=args.settings_file)
    cli.install(args.packages, registry=args.registry, tag=args.tag, **kwargs)
