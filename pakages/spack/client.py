__author__ = "Vanessa Sochat, Alec Scott"
__copyright__ = "Copyright 2021-2022, Vanessa Sochat and Alec Scott"
__license__ = "Apache-2.0"

from pakages.logger import logger
import pakages.spack.cache
import pakages.client

import spack.cmd
import spack.target
import spack.main
import spack.config

import re
import os
import json

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

        # Case 1: we have an install directed at the present working directory
        if packages and packages[0] == ".":
            repo = os.getcwd()
            packages.pop(0)

        # If we have a path (akin to the first)
        if packages and os.path.exists(packages[0]):
            repo = packages.pop(0)

        # OR if we have a github URI
        if packages and re.search("(http|https)://github.com", packages[0]):
            repo = packages.pop(0)

        # Add the repository, if defined
        if repo:
            repo = pakages.spack.repo.PakRepo(repo)

        # If we don't have packages and we have a repo, derive from PWD
        if repo and not packages:
            packages = repo.list_packages()

        # Finally, add the repository
        if repo:
            self.add_repository(repo.repo_dir)

        return packages

    def list_installed(self):
        """
        List installed packages
        """
        find = spack.main.SpackCommand("find")
        print(find())
        return json.loads(find("--json"))

    def build(self, packages, cache_dir=None, key=None, registry=None, tag=None):
        """
        Build a package into a cache
        """
        # Prepare a cache directory
        cache = pakages.spack.cache.BuildCache(
            cache_dir=cache_dir or self.settings.cache_dir,
            username=self.settings.username,
            email=self.settings.email,
            settings=self.settings,
        )

        # Install all packages, and also generate sboms.
        self.install(packages, registry=registry, tag=tag)
        cache.create(packages, key=key)
        return cache

    def push(self, uri, cache_dir=None, tag=None):
        """
        Given an existing cache directory, push known specs to a specific uri
        """
        # Prepare a cache directory
        cache = pakages.spack.cache.BuildCache(
            cache_dir=cache_dir or self.settings.cache_dir,
            username=self.settings.username,
            email=self.settings.email,
            settings=self.settings,
        )
        cache.push(uri, tag=tag)
        return cache

    def add_repository(self, path):
        """
        Add a repository.

        Given a path that exists, add the repository to the
        underlying spack. If you need to add a GitHub uri, create a
        pakages.repo.PakRepo first.
        """
        repos = spack.config.get("repos")
        repos.insert(0, path)
        spack.config.set("repos", repos)

    def install(self, packages, registry=None, tag=None, use_cache=False):
        """
        Install one or more packages.

        This eventually needs to take into account using the GitHub packages bulid cache
        """
        # Default to registries defined in settings
        registries = self.settings.trusted_pull_registries

        # Do we have an additional trusted registry provided on the command line?
        if registry:
            registries = [registry] + registries

        # Install packages using system spack - we aren't responsible for this working
        for line in pakages.utils.stream_command(['spack', 'install', packages]):
            logger.info(line.strip('\n'))

    def uninstall(self, packages):
        """
        Uninstall a spack package
        """
        for line in pakages.utils.stream_command(['spack', 'uninstall', packages]):
            logger.info(line.strip('\n'))
