__author__ = "Vanessa Sochat, Alec Scott"
__copyright__ = "Copyright 2021-2022, Vanessa Sochat and Alec Scott"
__license__ = "Apache-2.0"

from pakages.repo import PakRepo

import re
import os


def parse_package_request(args):
    """
    Given args, parse the packages and repo (if any) from it.
    This is shared between install and build
    """
    # By defualt, assume not adding a repository
    repo = None

    # Case 1: we have an install directed at the present working directory
    if args.packages and args.packages[0] == ".":
        repo = os.getcwd()
        args.packages.pop(0)

    # If we have a path (akin to the first)
    if args.packages and os.path.exists(args.packages[0]):
        repo = args.packages.pop(0)

    # OR if we have a github URI
    if args.packages and re.search("(http|https)://github.com", args.packages[0]):
        repo = args.packages.pop(0)

    # Add the repository, if defined
    if repo:
        repo = PakRepo(repo)

    # If we don't have packages and we have a repo, derive from PWD
    if repo and not args.packages:
        args.packages = repo.list_packages()
    return args.packages, repo
