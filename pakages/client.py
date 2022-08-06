__author__ = "Vanessa Sochat, Alec Scott"
__copyright__ = "Copyright 2021-2022, Vanessa Sochat and Alec Scott"
__license__ = "Apache-2.0"

import os

import pakages.builders

from .settings import Settings


def get_client(builder=None, settings_file=None):
    """
    Get a pakages client
    """
    # We don't require other builders to have spack installed
    if builder == "spack":
        from pakages.builders.spack import SpackClient

        return SpackClient(settings_file=settings_file)
    return PakagesClient(settings_file=settings_file)


class PakagesClient:
    """
    Pakages has a main controller for interacting with pakages.
    """

    def __init__(self, *args, **kwargs):
        settings_file = kwargs.get("settings_file")
        validate = kwargs.get("validate", True)
        if not hasattr(self, "settings"):
            self.settings = Settings(settings_file, validate=validate)

    def __repr__(self):
        return str(self)

    def __str__(self):
        return "[pakages-client]"

    def push(self, uri, cache_dir=None, tag=None):
        """
        Given an existing cache directory, push known specs to a specific uri
        """
        raise NotImplementedError

    def build(self, *args, **kwargs):
        """
        Build one or more packages.
        """
        args = list(args)
        if not args[0] or args[0] == ".":
            args[0] = os.getcwd()
        pkg = pakages.builders.get_package(args[0])

        # This returns a build result
        result = pkg.build()
        result.summary()
        return result

    def install(self, packages, registry=None, tag=None, **kwargs):
        """
        Install one or more packages.
        """
        raise NotImplementedError

    def uninstall(self, packages):
        """
        Uninstall a pakage
        """
        raise NotImplementedError
