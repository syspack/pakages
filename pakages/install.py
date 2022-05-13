__author__ = "Vanessa Sochat, Alec Scott"
__copyright__ = "Copyright 2021-2022, Vanessa Sochat and Alec Scott"
__license__ = "Apache-2.0"

import os
import shutil

import pakages.oras
import pakages.sbom
import pakages.utils
import pakages.defaults
import pakages.logger as logger

import spack.binary_distribution as bd
import spack.hooks
import spack.store
import spack.util.crypto


def do_install(self, **kwargs):
    """
    Refactored install process to add proper cache handling.
    """
    from spack.installer import PackageInstaller

    dev_path_var = self.spec.variants.get("dev_path", None)
    registries = kwargs.get("registries")
    tag = kwargs.get("tag")

    if dev_path_var:
        kwargs["keep_stage"] = True

    class PakInstaller(PackageInstaller):
        """
        The PakInstaller wraps the PackageInstaller.

        We take this inline approach because we are not able to import it.
        """

        def prepare_cache(self, registries=None, tag=None):
            """
            Given that we have a build cache for a package, install it.

            Since the GitHub packages API requires a token, we take an approach
            that attempts a pull for an artifact, and just continue if we don't
            have one.
            """
            # If no registries in user settings or command line, use default
            if not registries:
                registries = [pakages.defaults.trusted_packages_registry]
            tag = tag or pakages.defaults.default_tag

            # prepare oras client
            oras = pakages.oras.Oras()

            # If we want to use Github packages API, it requires token with package;read scope
            # https://docs.github.com/en/rest/reference/packages#list-packages-for-an-organization
            for request in self.build_requests:

                # Don't continue if installed!
                if request.spec.install_status() == True:
                    continue

                # The name of the expected package, and directory to put it
                name = bd.tarball_name(request.pkg.spec, ".spack")
                tmpdir = pakages.utils.get_tmpdir()

                # Try until we get a cache hit
                cache_hit = False
                for registry in registries:
                    uri = "%s/%s:%s" % (registry, name, tag)

                    # Retrieve the artifact (will be None if doesn't exist)
                    artifact = oras.fetch(uri, os.path.join(tmpdir, name))
                    if artifact:
                        cache_hit = True
                        break

                # Don't continue if not found
                if not cache_hit:
                    shutil.rmtree(tmpdir)
                    continue

                # Checksum check (removes sha256 prefix)
                sha256 = oras.get_manifest_digest(uri)
                if sha256:
                    checker = spack.util.crypto.Checker(sha256)
                    if not checker.check(artifact):
                        logger.exit("Checksum of %s is not correct." % artifact)

                # If we have an artifact, extract where needed and tell spack it's installed!
                if artifact:

                    # Note - for now not signing, since we don't have a consistent key strategy
                    bd.extract_tarball(request.pkg.spec, artifact, unsigned=True)
                    spack.hooks.post_install(request.pkg.spec)
                    spack.store.db.add(request.pkg.spec, spack.store.layout)

    builder = PakInstaller([(self, kwargs)])

    # Download what we can find from the GitHub cache
    builder.prepare_cache(registries, tag)
    builder.install()

    # If successful, generate an sbom
    meta_dir = os.path.join(self.prefix, ".spack")
    if os.path.exists(meta_dir):
        sbom = pakages.sbom.generate_sbom(self.spec)
        sbom_file = os.path.join(meta_dir, "sbom.json")
        pakages.utils.write_json(sbom, sbom_file)
