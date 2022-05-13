__author__ = "Vanessa Sochat, Alec Scott"
__copyright__ = "Copyright 2021-2022, Vanessa Sochat and Alec Scott"
__license__ = "Apache-2.0"

import pakages.utils as utils
from pakages.logger import logger
import requests
import os


base = "https://api.github.com"
accept = [
    "application/vnd.github.v3+json",
    "application/vnd.github.antiope-preview+json",
    "application/vnd.github.shadow-cat-preview+json",
]
accept_headers = ";".join(accept)


class GitHub:
    def __init__(self, token=None):
        self.token = token or os.environ.get("GITHUB_TOKEN")
        self.init_headers()

    def init_headers(self):
        self.headers = {"Accept": accept_headers}
        if self.token:
            self.headers["Authorization"] = "token %s" % self.token

    def clone(self, url, dest=None):
        """
        Given a URL, clone to dest. If dest not provided, create tmpdir
        """
        if not dest:
            dest = utils.get_tmpdir()

        res = utils.run_command(["git", "clone", url, dest])
        if res["return_code"] != 0:
            logger.exit(res["message"])
        return dest

    def get_org_packages(self, org):
        """
        Get organization packages.

        It doesn't seem to matter to set custom content type - these are pushed
        as containers. This is not ideal - we should be able to make an endpoint that
        is free to read with this metadata.
        """
        if not self.token:
            logger.error(
                "A token with packages:read scope is required for the Packages API."
            )
            return
        return self.get("/orgs/%s/packages" % org, {"package_type": "container"})

    def get(self, url, data=None):
        response = requests.get(base + url, headers=self.headers, params=data)
        if response.status_code != 200:
            logger.exit("Failed request to %s: %s" % (url, response.json()))
