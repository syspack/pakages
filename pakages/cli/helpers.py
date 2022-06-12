__author__ = "Vanessa Sochat, Alec Scott"
__copyright__ = "Copyright 2021-2022, Vanessa Sochat and Alec Scott"
__license__ = "Apache-2.0"


def parse_extra(extras):
    """
    Given a listing of extra arguments, parse into lookup dict.
    """
    values = {}
    if not extras:
        return values

    while extras:
        key = extras.pop(0)

        # A boolean or a key/value pair
        if key.startswith("--") and extras:
            key = key.replace("--", "").replace("-", "_")
            value = extras.pop(0)

            # key value pair
            if not value.startswith("--"):
                values[key] = value

            # Two booleans
            else:
                values[key] = True
                key = value.replace("--", "").replace("-", "_")
                values[key] = True

        # Just a boolean flag
        elif key.startswith("--") and not extras:
            key = key.replace("--", "").replace("-", "_")
            extras[key] = True
    return values
