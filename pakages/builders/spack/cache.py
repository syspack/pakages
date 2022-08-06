__author__ = "Vanessa Sochat, Alec Scott"
__copyright__ = "Copyright 2021-2022, Vanessa Sochat and Alec Scott"
__license__ = "Apache-2.0"

import os
import shutil

import spack.config

import pakages.build
import pakages.defaults
import pakages.settings
import pakages.utils
from pakages.logger import logger


class BuildCache:
    """
    A controller that makes it easy to create a build cache and install to it.
    We require that it is specific to one spec for now.
    """

    def __init__(
        self, spec_name, cache_dir=None, username=None, email=None, settings=None
    ):
        if not cache_dir:
            cache_dir = pakages.utils.get_tmpdir()
        self.cache_dir = cache_dir

        # Inherit settings from the client, or set to empty settings
        if not settings:
            settings = pakages.settings.EmptySettings()
        self.settings = settings

        # Set when we do create to remember specs
        self.spec_string = spec_name
        self.spec = None

    def remove(self):
        """
        Delete the entire build cache
        """
        if self.cache_dir and os.path.exists(self.cache_dir):
            logger.warning("Removing %s" % self.cache_dir)
            shutil.rmtree(self.cache_dir)

    def add_as_mirror(self, name):
        """
        Add the cache directory to spack as a filesystem mirror

        This currently downloads and adds to /tmp, and we issue a warning to the
        user. I'm not sure how people will want to install from caches but for
        the time being I'm making it a temporary interaction.
        """
        commands = [
            ["spack", "mirror", "add", name, self.cache_dir],
            ["spack", "buildcache", "update-index", "-d", self.cache_dir],
            ["spack", "buildcache", "list", "--allarch"],
        ]

        # Cut out early if mirror already added
        mirrors = spack.config.get("mirrors")
        if name not in mirrors:
            return

        for command in commands:
            try:
                for line in pakages.utils.stream_command(command):
                    logger.info(line.strip("\n"))

            # Mirror already exists, just pass for now
            except:
                pass

    def create(self, specs, key=None):
        """
        Create the build cache with some number of specs

        Ideally we could do spack buildcache add but that isn't supported.
        """
        # Save the spec name for pushing to remote cache later
        self.spec_name = specs
        command = ["spack", "buildcache", "create", "-r", "-a", "-u"]
        if key:
            command += ["-k", key]
        command += ["-d", self.cache_dir, specs]
        logger.info(command)
        for line in pakages.utils.stream_command(command):
            logger.info(line.strip("\n"))

    def load_spec(self):
        """
        Given a name at creation, find the corresponding spec json to load
        """
        if not self.spec_string:
            return

        # This might have an issue with a compiler as package
        for blob in pakages.utils.recursive_find(self.cache_dir, pattern="spec.json"):
            print(f"Looking for {self.spec_name} in {blob}")
            if self.spec_name in blob:
                print("Found!")
                self.spec = pakages.utils.read_json(blob)
                break

    def get_spec_uri(self):
        """
        Given a spec, return the unique resource identifier for the remote cache.
        """
        if not self.spec:
            self.load_spec()
        spec = self.spec["spec"]["nodes"][0]
        name = spec["name"]
        version = spec["version"]
        compiler = "%s-%s" % (spec["compiler"]["name"], spec["compiler"]["version"])
        target = spec["arch"]["target"]
        platform = spec["arch"]["platform"]
        osys = spec["arch"]["platform_os"]
        # TODO should we remove target?
        return f"{platform}-{osys}-{compiler}-{target}-{name}-{version}"

    def push(self, uri=None, tag=None):
        """
        Push the build cache to an OCI registry (compatible with ORAS)
        """
        tag = tag or self.settings.default_tag
        uri = uri or self.settings.trusted_packages_registry

        # Ensure the cache_dir exists
        if not os.path.exists(self.cache_dir) or not os.listdir(self.cache_dir):
            logger.exit(f"{self.cache_dir} is empty, use build to populate first.")

        # We must have the spec to generate archive name
        self.load_spec()
        if not self.spec:
            logger.exit(f"Cannot find spec for {self.spec_name} in cache.")

        if not uri:
            uri = self.get_spec_uri()
        if ":" not in uri:
            uri = f"{uri}:{tag}"

        # Create a build result with the temporary directory
        result = pakages.build.BuildResult("spack", self.cache_dir)

        # Here we add each filename (relative to the root) as a layer
        for blob in pakages.utils.recursive_find(self.cache_dir):

            # A title for the blob instead of the default basename
            result.add_title(blob, blob.replace(self.cache_dir + os.sep, ""))
            result.add_archive(blob, "application/vnd.oci.image.layer.v1.tar")

        result.push(uri)
        return result

    def __repr__(self):
        return str(self)

    def __str__(self):
        return "[pakages-build-cache]"
