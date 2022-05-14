__author__ = "Vanessa Sochat, Alec Scott"
__copyright__ = "Copyright 2021-2022, Vanessa Sochat and Alec Scott"
__license__ = "Apache-2.0"

import os
import shutil
import tarfile

import pakages.oras
import pakages.sbom
import pakages.utils
import pakages.defaults
from pakages.logger import logger

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

        def iter_artifact_names(self, registry, spec, tag):
            """
            Given a registry
            """
            name = bd.tarball_name(spec, ".spack")

            uri = "%s/%s:%s" % (registry, name, tag)
            yield name, uri

            # Now try a generic name WITHOUT hash
            generic_name = pakages.utils.generalize_spack_archive(name)
            uri = "%s/%s:%s" % (registry, generic_name, tag)
            yield generic_name, uri

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
                tmpdir = pakages.utils.get_tmpdir()

                # Try until we get a cache hit
                artifact = None
                for registry in registries:

                    # break for outer loop
                    if artifact:
                        break

                    for name, uri in self.iter_artifact_names(
                        registry, request.pkg.spec, tag
                    ):
                        artifact = oras.fetch(uri, os.path.join(tmpdir, name))
                        if artifact:
                            break

                # Don't continue if not found
                if not artifact:
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
                    logger.info(f"Extracting archive {artifact}...")

                    # Note - for now not signing, since we don't have a consistent key strategy
                    # The spack function is a hairball that doesn't respect the provided filename
                    spec = extract_tarball(request.pkg.spec, artifact)
                    spack.hooks.post_install(spec)
                    spack.store.db.add(spec, spack.store.layout)

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


def extract_tarball(spec, filename):
    """
    extract binary tarball for given package into install area
    """
    # The spec prefix is an easy way to get the directory name
    extract_dir = os.path.dirname(spec.prefix)
    from_dir = os.path.dirname(filename)
    name = os.path.basename(filename)
    dag_hash = name.split("-")[-1].replace(".spack", "")

    # Assemble the new spec prefix
    prefix = os.path.join(extract_dir, f"{spec.name}-{spec.version}-{dag_hash}")
    if os.path.exists(spec.prefix):
        shutil.rmtree(spec.prefix)

    tmpdir = pakages.utils.get_tmpdir()
    with tarfile.open(filename, "r") as tar:
        tar.extractall(tmpdir)

    # Find the json file and .tar.gz
    spec_file = None
    targz = None
    for path in os.listdir(tmpdir):
        if path.endswith(".json"):
            spec_file = os.path.join(tmpdir, path)
        elif path.endswith("gz"):
            targz = os.path.join(tmpdir, path)

    if not spec_file:
        shutil.rmtree(tmpdir)
        shutil.rmtree(from_dir)
        logger.exit(f"{spec} did not come with a spec json.")

    new_prefix = str(os.path.relpath(prefix, spack.store.layout.root))
    content = pakages.utils.read_json(spec_file)

    # if the original relative prefix is in the spec file use it
    buildinfo = content.get("buildinfo", {})
    relative_prefix = buildinfo.get("relative_prefix", new_prefix)

    extract_tmp = os.path.join(spack.store.layout.root, ".tmp")
    pakages.utils.mkdirp(extract_tmp)
    extracted_dir = os.path.join(extract_tmp, relative_prefix.split(os.path.sep)[-1])

    with tarfile.open(targz, "r") as tar:
        tar.extractall(path=extract_tmp)
    try:
        shutil.move(extracted_dir, prefix)
    except Exception as e:
        shutil.rmtree(extracted_dir)
        raise e

    # Clean up
    os.remove(targz)
    os.remove(spec_file)

    # Create a dummy spec to do the relocation
    new_spec = spack.spec.Spec.from_dict({"spec": content["spec"]})

    try:
        bd.relocate_package(new_spec, False)
    except Exception as e:
        shutil.rmtree(spec.prefix)
        raise e
    finally:
        shutil.rmtree(tmpdir)
        if os.path.exists(filename):
            os.remove(filename)
    return new_spec
