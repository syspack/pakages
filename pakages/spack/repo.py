__author__ = "Vanessa Sochat, Alec Scott"
__copyright__ = "Copyright 2021-2022, Vanessa Sochat and Alec Scott"
__license__ = "Apache-2.0"

import pakages.spack.install
import pakages.handlers.github
import pakages.utils as utils
from pakages.logger import logger

import spack.repo
import spack.config
import llnl.util.lang
import spack.util.naming as nm

import six
import shutil
import sys
import os
import re


class PakRepo:
    @property
    def is_remote(self):
        if re.search("(http|https)://github.com", self.raw):
            return True
        return False

    def __init__(self, path, add=True):
        """
        Create a new spack repo and add for spack to see.

        A Pak Repo can be a GitHub URL or a local path. It has a repos.yaml
        and packages/ directory.
        """
        self.raw = path
        if os.path.exists(path):
            self.path = os.path.abspath(path)
        elif self.is_remote:
            self.path = pakages.handlers.github.GitHub().clone(path)
        self.validate()

    def validate(self):
        """
        Validate that we have a repo, meaning we expect a repo.yml|yaml and packages
        """
        repo_yaml = list(utils.recursive_find(self.path, "repo[.](yml|yaml)"))
        if not repo_yaml:
            logger.exit("Cannot find repo.yaml or repo.yml anywhere in %s" % self.path)
        repo_yaml = repo_yaml[0]

        # Add directory with repo.yaml to spack just to list
        self.repo_dir = os.path.dirname(repo_yaml)

    def list_packages(self):
        """
        Given a filesystem repository, list packages there.

        We don't add the repository to be known by spack here, as we would want
        to do this when we install.
        """
        self.add()
        repo = Repo(self.repo_dir)
        return repo.all_package_names()

    def cleanup(self):
        """
        Cleanup a cloned repository - be careful don't run this for a local path!
        """
        if os.path.exists(self.repo_dir) and self.is_remote:
            shutil.rmtree(self.repo_dir)
            repos = spack.config.get("repos")
            updated = [r for r in repos if r != self.repo_dir]
            spack.config.set("repos", updated)

    def add(self):
        """
        Add the repository to be known to spack
        """
        repos = spack.config.get("repos")
        repos.insert(0, self.repo_dir)
        spack.config.set("repos", repos)


class RepoPath(spack.repo.RepoPath):
    def __init__(self, *repos):
        """
        Since we want control over customizing the package class, we return
        a pakages.repo.Repo instead.
        """
        self.repos = []
        self.by_namespace = nm.NamespaceTrie()

        self._provider_index = None
        self._patch_index = None
        self._tag_index = None

        # Add each repo to this path.
        for repo in repos:
            try:
                if isinstance(repo, six.string_types):
                    repo = Repo(repo)
                self.put_last(repo)
            except spack.repo.RepoError as e:
                logger.exit("Failed to initialize repository: '%s': %s" % (repo, e))

    def find_module(self, fullname, python_path=None):
        # Compatibility method to support Python 2.7
        return None
        # Note, might need to update this to be akin to parent


class Repo(spack.repo.Repo):
    @spack.repo.autospec
    def get(self, spec):
        """Returns the package associated with the supplied spec

        However we add custom functions provided by Pakages.
        """
        if spec.name is None:
            raise spack.repo.UnknownPackageError(None, self)

        if spec.namespace and spec.namespace != self.namespace:
            raise spack.repo.UnknownPackageError(spec.name, self.namespace)

        package_class = self.get_pkg_class(spec.name)

        # Monkey patch the class with the new install!
        package_class.do_install = pakages.spack.install.do_install

        try:
            return package_class(spec)
        except spack.error.SpackError:
            # pass these through as their error messages will be fine.
            raise
        except Exception as e:
            logger.debug(e)

            # Make sure other errors in constructors hit the error
            # handler by wrapping them
            if spack.config.get("config:debug"):
                sys.excepthook(*sys.exc_info())
            raise spack.repo.FailedConstructorError(spec.fullname, *sys.exc_info())


def _singleton_path(repo_dirs=None):
    """
    Get a singleton repository path, along with pakages custom
    """
    repo_dirs = repo_dirs or spack.config.get("repos")
    if not repo_dirs:
        raise spack.repo.NoRepoConfiguredError(
            "Spack configuration contains no package repositories."
        )

    path = RepoPath(*repo_dirs)
    sys.meta_path.append(path)
    return path


#: Singleton repo path instance
path = llnl.util.lang.Singleton(_singleton_path)


def get(spec):
    """Convenience wrapper around ``spack.repo.get()``."""
    # TODO add support here for a spec name that is from GitHub
    # And then add to singleton path (do dynamically as function)
    return path.get(spec)
