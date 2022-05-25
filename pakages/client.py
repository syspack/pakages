__author__ = "Vanessa Sochat, Alec Scott"
__copyright__ = "Copyright 2021-2022, Vanessa Sochat and Alec Scott"
__license__ = "Apache-2.0"

from pakages.logger import logger
import pakages.cache
from .settings import Settings

import json


def get_client(builder=None, settings_file=None):
    """
    Get a pakages client
    """
    if builder == "spack":
        from pakages.spack.client import SpackClient

        return SpackClient(settings_file=settings_file)
    else:
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

    def install(self, packages, registry=None, tag=None):
        """
        Install one or more packages.
        """
        raise NotImplementedError

    def uninstall(self, packages):
        """
        Uninstall a pakage
        """
        raise NotImplementedError
