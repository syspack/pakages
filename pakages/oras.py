__author__ = "Vanessa Sochat, Alec Scott"
__copyright__ = "Copyright 2021-2022, Vanessa Sochat and Alec Scott"
__license__ = "Apache-2.0"

import os
import oras.oci
import oras.defaults
import oras.provider
from oras.decorator import ensure_container
from pakages.logger import logger


def get_oras_client():
    """
    Consistent method to get an oras client
    """
    user = os.environ.get("ORAS_USER")
    password = os.environ.get("ORAS_PASS")
    reg = Registry()
    if user and password:
        print("Found username and password for basic auth")
        reg.set_basic_auth(user, password)
    else:
        logger.warning("ORAS_USER or ORAS_PASS is missing, push may have issues.")
    return reg


def pull_to_dir(pull_dir, target):
    """
    Given a URI, pull to an output directory.
    """
    reg = get_oras_client()
    return reg.pull(target=target, outdir=pull_dir)


class Registry(oras.provider.Registry):
    @ensure_container
    def push(self, container, archives: dict, annotations=None, titles: dict = None):
        """
        Given a dict of layers (paths and corresponding mediaType) push.
        """
        # Lookup of titles to override default
        titles = titles or {}

        # Prepare a new manifest
        manifest = oras.oci.NewManifest()

        # A lookup of annotations we can add
        annotset = oras.oci.Annotations(annotations or {})

        # Upload files as blobs
        for blob, mediaType in archives.items():

            # Must exist
            if not os.path.exists(blob):
                logger.exit(f"{blob} does not exist.")

            # Save directory or blob name before compressing
            blob_name = os.path.basename(blob)
            if blob in titles:
                blob_name = titles[blob]

            # If it's a directory, we need to compress
            cleanup_blob = False
            if os.path.isdir(blob):
                blob = oras.utils.make_targz(blob)
                cleanup_blob = True

            # Create a new layer from the blob
            layer = oras.oci.NewLayer(blob, mediaType, is_dir=cleanup_blob)
            annotations = annotset.get_annotations(blob)
            layer["annotations"] = {oras.defaults.annotation_title: blob_name}
            if annotations:
                layer["annotations"].update(annotations)

            # update the manifest with the new layer
            manifest["layers"].append(layer)

            # Upload the blob layer
            logger.info(f"Uploading {blob}")
            response = self._upload_blob(blob, container, layer)
            self._check_200_response(response)

            # Do we need to cleanup a temporary targz?
            if cleanup_blob and os.path.exists(blob):
                os.remove(blob)

        # Add annotations to the manifest, if provided
        manifest_annots = annotset.get_annotations("$manifest")
        if manifest_annots:
            manifest["annotations"] = manifest_annots

        # Prepare the manifest config (temporary or one provided)
        config_annots = annotset.get_annotations("$config")
        conf, config_file = oras.oci.ManifestConfig()

        # Config annotations?
        if config_annots:
            conf["annotations"] = config_annots

        # Config is just another layer blob!
        response = self._upload_blob(config_file, container, conf)
        self._check_200_response(response)

        # Final upload of the manifest
        manifest["config"] = conf
        self._check_200_response(self._upload_manifest(manifest, container))
        print(f"Successfully pushed {container}")
        return response
