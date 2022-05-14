__author__ = "Vanessa Sochat, Alec Scott"
__copyright__ = "Copyright 2021-2022, Vanessa Sochat and Alec Scott"
__license__ = "Apache-2.0"

import spack.spec
from pakages.logger import logger
import spack.util.string
import pakages.repo
import six


class Spec(spack.spec.Spec):
    @property
    def package(self):
        """
        Return a custom repository that can deliver Pakages packages
        """
        if not self._package:
            self._package = pakages.repo.get(self)
        return self._package


def parse(string):
    """Returns a list of specs from an input string.
    For creating one spec, see Spec() constructor.
    """
    return


def parse_specs(packages):
    """
    Parse specs from a list of strings, and concretize
    """
    if not isinstance(packages, six.string_types):
        packages = " ".join(spack.util.string.quote(packages))

    specs = []
    for legacy in spack.spec.SpecParser().parse(packages):

        logger.info(f"Preparing spec for {legacy}")
        # Create a new Pak spec to copy (duplicate) into
        spec = Spec()
        spec._dup(legacy)

        # Always set the arch to be general
        spec.architecture = spack.spec.ArchSpec()
        spec.architecture.target = spack.target.Target("x86_64")

        spec.concretize()
        specs.append(spec)
    return specs
