__author__ = "Vanessa Sochat, Alec Scott"
__copyright__ = "Copyright 2021-2023, Vanessa Sochat and Alec Scott"
__license__ = "Apache-2.0"

import json
import os
import re
import shlex
import subprocess

import pakages.builders.spack.cache as spack_cache
import pakages.client
import pakages.oras
import pakages.utils
from pakages.logger import logger


class SpackClient(pakages.client.PakagesClient):
    """
    Pakages has a main controller for interacting with pakages.
    """

    def parse_package_request(self, packages):
        """
        Parse the packages and repo (if any) from it.
        This is shared between install and build
        """
        # By defualt, assume not adding a repository
        repo = None

        if not isinstance(packages, list):
            packages = shlex.split(packages)

        # Case 1: we have an install directed at the present working directory
        if packages and packages[0] == ".":
            repo = os.getcwd()
            packages.pop(0)

        # If we have a path (akin to the first)
        if packages and os.path.exists(packages[0]):
            repo = packages.pop(0)

        # OR if we have a github URI TODO, can clone here
        if packages and re.search("(http|https)://github.com", packages[0]):
            repo = packages.pop(0)

        # If we don't have packages and we have a repo, derive from PWD
        if repo and not packages:
            for path in pakages.utils.recursive_find(repo, "package.py"):
                packages.append(os.path.basename(os.path.dirname(path)))

        # Finally, add the repository
        if repo:
            self.add_repository(repo)

        return packages

    def list_installed(self):
        """
        List installed packages
        """
        command = ["spack", "find"]
        for line in pakages.utils.stream_command(command):
            print(line.strip("\n"))

        command = ["spack", "find", "--json"]
        result = pakages.utils.run_command(command)
        return json.loads(result["message"])

    def build(self, packages, cache_dir=None, key=None, **kwargs):
        """
        Build a package into a cache
        """
        packages = self.parse_packages(packages)

        # Prepare a cache directory
        cache = spack_cache.BuildCache(
            spec_name=packages,
            cache_dir=cache_dir or self.settings.cache_dir,
            username=self.settings.username,
            email=self.settings.email,
            settings=self.settings,
        )

        # Install all packages
        self._install(packages)
        cache.create(packages, key=key)

        # Push function is on cache, if desired
        return cache

    def parse_packages(self, packages):
        """
        Helper function to ensure we return consistent names.
        """
        packages = self.parse_package_request(packages)
        if isinstance(packages, list):
            packages = packages[0]
        if " " in packages:
            logger.exit("We currently only support one package for build.")
        logger.info(f"Preparing package {packages}")
        return packages

    def add_repository(self, path):
        """
        Add a repository.

        Given a path that exists, add the repository to the
        underlying spack. If you need to add a GitHub uri, create a
        pakages.repo.PakRepo first.
        """
        try:
            command = ["spack", "repo", "add", path]
            for line in pakages.utils.stream_command(command):
                logger.info(line.strip("\n"))
        except subprocess.CalledProcessError as e:
            if "Repository is already registered" in e.output:
                pass
            else:
                raise e

    def download_cache(self, target, download_dir=None):
        """
        Download a target to a cache download directory
        """
        download_dir = download_dir or pakages.utils.get_tmpdir()
        reg = pakages.oras.get_oras_client()

        # This will error if not successful, result is a list of files
        reg.pull(target=target, outdir=download_dir)
        return download_dir

    def install(self, packages, **kwargs):
        """
        Install one or more packages.
        """
        packages = self.parse_packages(packages)
        use_cache = kwargs.get("use_cache", False)
        if use_cache:
            cache_dir = self.download_cache(use_cache)
            cache = spack_cache.BuildCache(
                packages, cache_dir=cache_dir, settings=self.settings
            )

            # Cache is named after target, this is a filesystem mirror
            cache.add_as_mirror(re.sub("(-|:|/)", "-", use_cache))

        # Prepare install command with or without cache
        command = ["spack", "install"]
        if use_cache:
            command.append("--use-cache")
        if isinstance(packages, list):
            command.append(" ".join(packages))
        else:
            command.append(packages)

        # Install packages using system spack - we aren't responsible for this working
        for line in pakages.utils.stream_command(command):
            logger.info(line.strip("\n"))

    def _install(self, packages):
        """
        Install one or more packages.

        This eventually needs to take into account using the GitHub packages bulid cache
        """
        # Install packages using system spack - we aren't responsible for this working
        for line in pakages.utils.stream_command(["spack", "install", packages]):
            logger.info(line.strip("\n"))

    def uninstall(self, packages):
        """
        Uninstall a spack package
        """
        for line in pakages.utils.stream_command(["spack", "uninstall", packages]):
            logger.info(line.strip("\n"))
