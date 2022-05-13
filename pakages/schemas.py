__author__ = "Vanessa Sochat, Alec Scott"
__copyright__ = "Copyright 2021-2022, Vanessa Sochat and Alec Scott"
__license__ = "Apache-2.0"

## ContainerConfig Schema

schema_url = "https://json-schema.org/draft-07/schema/#"

## Settings.yml (loads as json)

# Currently all of these are required
settingsProperties = {
    "content_type": {"type": "string"},
    "config_editor": {"type": "string"},
    "updated_at": {"type": ["string", "null"]},
    "username": {"type": ["string", "null"]},
    "email": {"type": ["string", "null"]},
    "cache_dir": {"type": ["string", "null"]},
    # We pull from these
    "trusted_pull_registries": {"type": "array", "items": {"type": "string"}},
    # This is where we push to
    "trusted_packages_registry": {"type": "string"},
    "default_tag": {"type": "string"},
}

settings = {
    "$schema": schema_url,
    "title": "Settings Schema",
    "type": "object",
    "required": [
        "default_tag",
        "trusted_packages_registry",
        "trusted_pull_registries",
        "config_editor",
        "content_type",
    ],
    "properties": settingsProperties,
    "additionalProperties": False,
}
