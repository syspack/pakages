__author__ = "Vanessa Sochat, Alec Scott"
__copyright__ = "Copyright 2021-2022, Vanessa Sochat and Alec Scott"
__license__ = "Apache-2.0"

import pakages.utils as utils
import pakages.build
from pakages.logger import logger
from citelang.main.packages import SetupManager

from cyclonedx_py.parser.requirements import RequirementsParser
from cyclonedx.model.bom import Bom
from cyclonedx.output import get_instance, OutputFormat
from cyclonedx.model import Tool

from pakages.version import __version__ as version
import shutil
import os


class PythonPackage:
    def __init__(self, path):
        self.path = path

    @classmethod
    def matches(cls, root):
        """
        Determine if a root has a setup.py or setup.cfg
        """
        files = os.listdir(root)
        return "setup.py" in files or "setup.cfg" in files

    def build(self):
        """
        A build returns a build result.
        """
        # The build result will manage the result files
        tmpdir = utils.get_tmpdir()
        result = pakages.build.BuildResult("python", tmpdir)
        bom = None

        with utils.workdir(self.path):

            # Build distribution
            command = f"python setup.py sdist --dist-dir {tmpdir}"
            cmd = utils.Command(command)
            res = cmd.run()

            # If we have a setup.py, generate an sbom
            if os.path.exists("setup.py"):
                manager = SetupManager()
                reqs = manager.from_file("setup.py")
                requirements = [
                    "%s==%s" % (x["name"], x["number"]) for x in reqs["dependencies"]
                ]
                rp = RequirementsParser("\n".join(requirements))
                bom = Bom.from_parser(parser=rp)

        logger.info(res.output)
        logger.warning(res.error)
        if res.returncode != 0:
            shutil.rmtree(tmpdir)
            logger.exit(f"Error running command: {command}.")
        targz = os.listdir(tmpdir)
        if not targz:
            logger.exit("No files found in build directory.")
        targz_path = os.path.join(tmpdir, targz[0])
        result.add_archive(targz_path, "application/vnd.oci.image.layer.v1.tar+gzip")

        if bom:
            bom.metadata.tools.add(
                Tool(vendor="Syspack", name="pakages", version=version)
            )
            instance = get_instance(bom, output_format=OutputFormat.JSON)
            sbom_path = os.path.join(tmpdir, "sbom.json")
            instance.output_to_file(sbom_path)
            result.add_archive(sbom_path, "application/vnd.cyclonedx")

        return result
