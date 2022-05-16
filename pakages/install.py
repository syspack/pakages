__author__ = "Vanessa Sochat, Alec Scott"
__copyright__ = "Copyright 2021-2022, Vanessa Sochat and Alec Scott"
__license__ = "Apache-2.0"

import os
import shutil
import tarfile
from collections import defaultdict

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

        def _get_task(self, pkg, request, is_compiler, all_deps):
            """
            Get a build task for the package.
            """
            task = spack.installer.BuildTask(
                pkg,
                request,
                is_compiler,
                0,
                0,
                spack.installer.STATUS_ADDED,
                self.installed,
            )
            pkg_id = spack.installer.package_id(pkg)

            for dep_id in task.dependencies:
                all_deps[dep_id].add(pkg_id)
            return task

        def prepopulate_tasks(self):
            """
            Pre-populate a lookup of tasks for the cache.
            """
            # Prepare the complete list of dependencies to look for
            # This mimicks init_queue
            self._pakages_tasks = {}
            all_deps = defaultdict(set)
            logger.debug("Initializing the build queue from the build requests")
            for request in self.build_requests:
                for dep in request.traverse_dependencies():
                    dep_id = spack.installer.package_id(dep.package)
                    if dep_id not in self.build_tasks:
                        task = self._get_task(dep.package, request, False, all_deps)
                        self._pakages_tasks[task.pkg_id] = task
                    spack.store.db.clear_failure(dep, force=False)

                if request.pkg_id not in self._pakages_tasks:
                    spack.store.db.clear_failure(request.spec, force=True)
                    task = self._get_task(request.pkg, request, False, all_deps)
                    self._pakages_tasks[task.pkg_id] = task

            # Add missing dependents to ensure proper uninstalled dependency
            # tracking when installing multiple specs
            for dep_id, dependents in all_deps.items():
                if dep_id in self._pakages_tasks:
                    task = self._pakages_tasks[dep_id]
                    for dependent_id in dependents.difference(task.dependents):
                        task.add_dependent(dependent_id)

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

            if not self.build_requests:
                return

            # We will update build requests with specs we find
            # This is a loose matching, we just care about name and version for now
            requests = {
                "%s:%s" % (x.pkg.spec.name, x.pkg.spec.version): x
                for x in self.build_requests
            }

            # If we want to use Github packages API, it requires token with package;read scope
            # https://docs.github.com/en/rest/reference/packages#list-packages-for-an-organization
            for pkg_id, request in self._pakages_tasks.items():

                # Don't continue if installed!
                if request.pkg.spec.install_status() == True:
                    continue

                # The name of the expected package, and directory to put it
                tmpdir = pakages.utils.get_tmpdir()

                # Try until we get a cache hit
                artifact = None
                for registry in registries:
                    name = bd.tarball_name(request.pkg.spec, ".spack")
                    generic_name = pakages.utils.generalize_spack_archive(name)
                    uri = "%s/%s:%s" % (registry, generic_name, tag)
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
                    # Note - for now not signing, since we don't have a consistent key strategy
                    # The spack function is a hairball that doesn't respect the provided filename
                    spec = extract_tarball(request.pkg.spec, artifact)
                    if not spec:
                        continue

                    # Remove the build request if we hit it. Note that this
                    # might fail if dependencies are still needed (and not hit)
                    # I haven't tested it yet
                    spec_id = f"{spec.name}:{spec.version}"
                    if spec_id in requests:

                        # update the build request
                        requests[spec_id].pkg.spec = spec
                        requests[spec_id].pkg_id = spack.installer.package_id(
                            spec.package
                        )
                        requests[spec_id].dependencies = {
                            f"{x.name}-{x.version}-{x._hash}"
                            for x in spec.dependencies()
                        }

                        # And flag the task as installed
                        task = requests[spec_id]
                        requests[spec_id].task = spack.installer.STATUS_INSTALLED
                        self._flag_installed(task.pkg, spec.dependents())

                    # And finish this piece of the install
                    spec.package.installed_from_binary_cache = True
                    spack.hooks.post_install(spec)
                    spack.store.db.add(spec, spack.store.layout)

            # Update build requests
            self.build_requests = list(requests.values())

    builder = PakInstaller([(self, kwargs)])

    # Download what we can find from the GitHub cache
    builder.prepopulate_tasks()
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
    from_dir = os.path.dirname(filename)
    name = os.path.basename(filename)
    dag_hash = name.split("-")[-1].replace(".spack", "")

    # Anything installed from system
    if spack.store.layout.root not in spec.prefix:
        return
        extract_dir = spack.store.layout.root

        # ['linux', 'ubuntu20.04', 'x86_64', 'gcc', '9.4.0', 'bzip2', '1.0.8']
        parts = os.path.basename(filename).split("-")[:-1]
        prefix = os.path.join(
            extract_dir,
            f"{parts[0]}-{parts[1]}-{parts[2]}",
            f"{parts[3]}-{parts[4]}",
            f"{spec.name}-{spec.version}-{dag_hash}",
        )
    else:
        extract_dir = os.path.dirname(spec.prefix)
        prefix = os.path.join(extract_dir, f"{spec.name}-{spec.version}-{dag_hash}")

    # The spec prefix is an easy way to get the directory name
    if os.path.exists(prefix):
        shutil.rmtree(prefix)

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
    new_spec._prefix = prefix

    try:
        bd.relocate_package(new_spec, False)
    # This probably shouldn't fail, will let it slide for now
    except Exception as e:
        raise e
    finally:
        shutil.rmtree(tmpdir)
        if os.path.exists(filename):
            os.remove(filename)
    return new_spec
