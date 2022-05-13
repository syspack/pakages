__author__ = "Vanessa Sochat, Alec Scott"
__copyright__ = "Copyright 2021-2022, Vanessa Sochat and Alec Scott"
__license__ = "Apache-2.0"

import spack.bootstrap
import spack.spec
import pakages.utils as utils
import pakages.defaults
import spack.util.executable
import spack.util.crypto

from pakages.logger import logger

import os
import requests


class Oras:
    def __init__(self):
        self._oras = None

    @property
    def oras(self):
        """
        Get the oras executable (easier to install on your computer over bootstrap)
        """
        if not self._oras:
            with spack.bootstrap.ensure_bootstrap_configuration():
                spec = spack.spec.Spec("oras")
                spack.bootstrap.ensure_executables_in_path_or_raise(
                    ["oras"], abstract_spec=spec
                )
                self._oras = spack.util.executable.which("oras")
        return self._oras

    def get_manifest(self, uri):
        """
        Use crane to get the image manifest
        """
        response = requests.get("https://crane.ggcr.dev/manifest/" + uri)
        if response.status_code == 200:
            return response.json()

    def get_manifest_digest(self, uri):
        """
        Get the first layer digest (the spack package archive)
        """
        response = self.get_manifest(uri)
        if not response:
            return

        layers = response.get("layers")
        if layers:
            digest = layers[0].get("digest")
            if digest:
                return digest.replace("sha256:", "")

    def push(self, uri, push_file, content_type=None):
        """
        Push an oras artifact to an OCI registry
        """
        content_type = content_type or pakages.defaults.content_type
        logger.info("Pushing oras {0}".format(uri))
        with utils.workdir(os.path.dirname(push_file)):
            self.oras(
                "push",
                uri,
                "--manifest-config",
                "/dev/null:application/vnd.unknown.config.v1+json",
                # GitHub does not honor this content type - it will return an empty artifact
                os.path.basename(push_file) + ":" + content_type,
            )

    def fetch(self, url, save_file):
        """
        Fetch an oras artifact from an OCI registry
        """
        # We don't have programmatic access to list, so we just try to pull
        logger.info("Fetching oras {0}".format(url))

        try:
            self.oras("pull", url, "-a", "--output", os.path.dirname(save_file))
        except:
            logger.info("{0} is not available for pull.".format(url))
            return

        # Return the file if exists
        if os.path.exists(save_file):
            return save_file
