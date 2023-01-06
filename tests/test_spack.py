#!/usr/bin/python

# Copyright (C) 2022 Vanessa Sochat.

# This Source Code Form is subject to the terms of the
# Mozilla Public License, v. 2.0. If a copy of the MPL was not distributed
# with this file, You can obtain one at http://mozilla.org/MPL/2.0/.

import os

from pakages.builders.spack import SpackClient

here = os.path.abspath(os.path.dirname(__file__))


def test_list_dir(tmp_path):
    """
    Test upgrade from a filesystem registry.
    """
    cli = SpackClient()
    test_dir = os.path.join(here, "spack")
    os.chdir(test_dir)

    request = cli.parse_package_request(["."])
    assert len(request) == 1
    assert "zlib" in request
