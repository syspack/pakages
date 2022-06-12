__author__ = "Vanessa Sochat, Alec Scott"
__copyright__ = "Copyright 2021-2022, Vanessa Sochat and Alec Scott"
__license__ = "Apache-2.0"

from pakages.logger import logger
import pakages.spack.utils as utils
import pakages.utils
from spack.main import SpackCommand
import pakages.defaults
import pakages.settings
import pakages.spack.oras

import shutil
import os


def gpg_init(dirname):
    """
    Init the gpg directory, setting permissions etc.
    """
    pakages.utils.mkdirp(dirname)
    os.chmod(dirname, 0o700)


def get_gpg_key():
    """
    Find the first key created for spack

    This would really be nicer if we didn't have to use gpg :)
    """
    gpg = SpackCommand("gpg")

    key = None
    lines = gpg("list").split("\n")
    for i, line in enumerate(lines):
        if "Spack" in line:
            key = lines[i - 1].strip()
            break
    return key


class BuildCache:
    """
    A controller that makes it easy to create a build cache and install to it.
    """

    def __init__(self, cache_dir=None, username=None, email=None, settings=None):
        if not cache_dir:
            cache_dir = pakages.utils.get_tmpdir()
        self.cache_dir = cache_dir

        # Inherit settings from the client, or set to empty settings
        if not settings:
            settings = pakages.settings.EmptySettings()
        self.settings = settings

    def remove(self):
        """
        Delete the entire build cache
        """
        if self.cache_dir and os.path.exists(self.cache_dir):
            logger.warning("Removing %s" % self.cache_dir)
            shutil.rmtree(self.cache_dir)

    def create(self, specs, key=None):
        """
        Create the build cache with some number of specs

        Ideally we could do spack buildcache add but that isn't supported.
        """
        command = ["spack", "buildcache", "create", "-r", "-a", "-u"]
        if key:
            command += ["-k", key]
        command += ["-d", self.cache_dir, specs]
        for line in pakages.utils.stream_command(command):
            logger.info(line.strip('\n'))

    def push(self, uri=None, tag=None):
        """
        Push the build cache to an OCI registry (compatible with ORAS)
        """
        tag = tag or self.settings.default_tag
        content_type = self.settings.content_type or pakages.defaults.content_type
        uri = uri or self.settings.trusted_packages_registry

        # Create an oras client
        oras = pakages.spack.oras.Oras()

        # Find all .spack archives in the cache
        for archive in pakages.utils.recursive_find(self.cache_dir, ".spack"):

            # Only push generic name - the full hash never hits
            package_name = os.path.basename(archive)
            generic_name = utils.generalize_spack_archive(package_name)
            full_name = "%s/%s:%s" % (uri, generic_name, tag)
            oras.push(full_name, archive, content_type=content_type)

    def __repr__(self):
        return str(self)

    def __str__(self):
        return "[pakages-build-cache]"
