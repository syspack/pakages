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
import random
import requests
import time


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

    def push(self, uri, push_file, content_type=None, retry=3, sleep=1):
        """
        Push an oras artifact to an OCI registry
        """
        tries = 0
        content_type = content_type or pakages.defaults.content_type
        logger.info("Pushing oras {0}".format(uri))
        with utils.workdir(os.path.dirname(push_file)):
            while tries < retry:
                try:
                    return self._push(uri, push_file, content_type)
                except:
                    time.sleep(sleep)
                    sleep = sleep * 2**tries + random.uniform(0, 1)
                    tries += 1

    def _push(self, uri, push_file, content_type):
        """
        Helper to push that provides consistent metadata
        """
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
        save_dir = os.path.dirname(save_file)
        try:
            logger.debug("Trying fetch for {0}".format(url))
            self.oras("pull", url, "-a", "--output", save_dir, output=str, error=str)
        except:
            logger.debug("{0} is not available for pull.".format(url))
            return

        # Just print those that are successful
        logger.info("Fetched {0}".format(url))
        # Files are technically saved with the hash, we just hope spack will use
        files = os.listdir(save_dir)
        if len(files) > 0:
            save_file = os.path.join(save_dir, files[0])

        # Return the file if exists
        if os.path.exists(save_file):
            return save_file
