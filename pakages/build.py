__author__ = "Vanessa Sochat, Alec Scott"
__copyright__ = "Copyright 2021-2022, Vanessa Sochat and Alec Scott"
__license__ = "Apache-2.0"

from pakages.logger import logger
import pakages.oras
import shutil
import os


class BuildResult:
    """
    A BuildResult holds a set of content types and objects to upload.

    We also store the builder name (e.g., Python) so we know how to extract.
    """

    def __init__(self, builder, tmpdir, annotations=None):
        self.builder = builder
        self.archives = {}
        self.tmpdir = tmpdir
        self.annotations = annotations or {}

    def __repr__(self):
        return str(self)

    def __str__(self):
        return "[pakages-build-task]"

    def cleanup(self):
        """
        Delete temporary directory
        """
        if self.tmpdir and os.path.exists(self.tmpdir):
            shutil.rmtree(self.tmpdir)

    def push(self, target):
        """
        Push archives to a target
        """
        user = os.environ.get("ORAS_USER")
        password = os.environ.get("ORAS_PASS")
        reg = pakages.oras.Registry()
        if user and password:
            reg.set_basic_auth(user, password)
        reg.push(target, self.archives, self.annotations)

    def summary(self):
        """
        Print a summary of files
        """
        logger.info(
            "Generated %s build artifacts for %s builder."
            % (len(self.archives), self.builder)
        )
        for path, mediaType in self.archives.items():
            logger.info("%s %s" % (mediaType.ljust(50), path))

    def add_archive(self, path, mediaType):
        """
        Add an archive to the build result
        """
        self.archives[path] = mediaType
