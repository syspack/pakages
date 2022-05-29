__author__ = "Vanessa Sochat, Alec Scott"
__copyright__ = "Copyright 2021-2022, Vanessa Sochat and Alec Scott"
__license__ = "Apache-2.0"

import os
import copy
import requests
import oras.oci
import oras.defaults
import oras.provider
from oras.decorator import ensure_container
from pakages.logger import logger
from typing import *

class Registry(oras.provider.Registry):
    @ensure_container
    def push(self, container, archives: dict, annotations=None):
        """
        Given a dict of layers (paths and corresponding mediaType) push.
        """
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
        
    def do_request(
        self,
        url: str,
        method: str = "GET",
        data: Union[dict, bytes] = None,
        headers: dict = None,
        json: dict = None,
        stream: bool = False,
    ):
        """
        Do a request. This is a wrapper around requests to handle retry auth.

        :param url: the URL to issue the request to
        :type url: str
        :param method: the method to use (GET, DELETE, POST, PUT, PATCH)
        :type method: str
        :param data: data for requests
        :type data: dict or bytes
        :param headers: headers for the request
        :type headers: dict
        :param json: json data for requests
        :type json: dict
        :param stream: stream the responses
        :type stream: bool
        """
        headers = headers or {}

        # Make the request and return to calling function, unless requires auth
        response = self.session.request(
            method, url, data=data, json=json, headers=headers, stream=stream
        )

        # A 401 response is a request for authentication
        print('STATUS CODE %s' % response.status_code)
        if response.status_code != 401:
            return response

        # Otherwise, authenticate the request and retry
        if self.authenticate_request(response):
            headers.update(self.headers)
            return self.session.request(
                method, url, data=data, json=json, headers=headers, stream=stream
            )
        return response

    def authenticate_request(self, originalResponse: requests.Response) -> bool:
        """
        Authenticate Request
        Given a response, look for a Www-Authenticate header to parse.

        We return True/False to indicate if the request should be retried.

        :param originalResponse: original response to get the Www-Authenticate header
        :type originalResponse: requests.Response
        """
        authHeaderRaw = originalResponse.headers.get("Www-Authenticate")
        print("authHeader: %s" % authHeaderRaw)
        if not authHeaderRaw:
            return False

        # If we have a token, set auth header (base64 encoded user/pass)
        if self.token:
            print("SETTING TOKEN for auth")
            self.set_header("Authorization", "Basic %s" % self.token)

        headers = copy.deepcopy(self.headers)
        if "Authorization" not in headers:
            logger.error(
                "This endpoint requires a token. Please set "
                "oras.provider.Registry.set_basic_auth(username, password) "
                "first or use oras-py login to do the same."
            )
            return False

        # Prepare request to retry
        h = oras.auth.parse_auth_header(authHeaderRaw)
        if h.service:
            headers.update(
                {
                    "Service": h.service,
                    "Accept": "application/json",
                    "User-Agent": "oras-py",
                }
            )

        # Currently we don't set a scope (it defaults to build)
        if not h.realm.startswith("http"):  # type: ignore
            h.realm = f"{self.prefix}://{h.realm}"
        print('realm %s' % h.realm)
        authResponse = self.session.get(h.realm, headers=headers)  # type: ignore
        print(authResponse.status_code)
        print(authResponse.reason)
        if authResponse.status_code != 200:
            return False

        # Request the token
        info = authResponse.json()
        print(info.keys())
        token = info.get("token")
        if not token:
            token = info.get("access_token")

        # Set the token to the original request and retry
        self.headers.update({"Authorization": "Bearer %s" % token})
        return True
