__author__ = "Vanessa Sochat, Alec Scott"
__copyright__ = "Copyright 2021-2023, Vanessa Sochat and Alec Scott"
__license__ = "Apache-2.0"

import os
import sys

from pakages.utils.terminal import get_installdir, run_command, which


def generalize_spack_archive(name):
    """
    Helper function to consistently return the archive name with arch, os, no build hash
    """
    return "-".join(name.split("-")[:-1]) + ".spack"


def install_spack(repo=None, branch=None):
    """
    Install spack to pakages/spack (note this is not used).
    """
    repo = repo or "https://github.com/spack/spack"
    branch = branch or "develop"
    spack_prefix = os.path.join(get_installdir(), "spack")
    return run_command(["git", "clone", "-b", branch, repo, spack_prefix])


def ensure_spack_on_path():
    """
    Ensure spack is on the path.
    """
    # First check for spack in environment
    spack_prefix = which("spack")
    if spack_prefix:

        # spack -> bin -> root
        spack_prefix = os.path.dirname(os.path.dirname(spack_prefix))

    else:
        # Then check for spack installed to package
        spack_prefix = os.path.join(get_installdir(), "spack")

    # Otherwise, fail
    if not os.path.exists(spack_prefix):
        sys.exit("spack must be installed! Add to path for pakages to find.")
