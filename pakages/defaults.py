__author__ = "Vanessa Sochat, Alec Scott"
__copyright__ = "Copyright 2021-2022, Vanessa Sochat and Alec Scott"
__license__ = "Apache-2.0"

import os

import pakages.utils as utils

install_dir = utils.get_installdir()
reps = {"$install_dir": install_dir, "$root_dir": os.path.dirname(install_dir)}

# The default settings file in the install root
default_settings_file = os.path.join(reps["$install_dir"], "settings.yml")

# Pakages home stores user specific keys, etc
pakageshome = os.path.expanduser("~/.pakages")

# The user settings file can be created to over-ride default
user_settings_file = os.path.join(pakageshome, "settings.yml")

# Default directory for keys
keys_dir = os.path.join(pakageshome, "keys")

# Fallback content type
content_type = "application/vnd.spack.package"

# Allowed variables for the environment
allowed_envars = ["username"]

# Default registry prefix to install from
trusted_packages_registry = "ghcr.io/pakages"

# The GitHub repository for pakages
github_url = "https://github.com/syspack/pakages"
