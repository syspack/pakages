.. _getting_started-user-guide:

==========
User Guide
==========

Pakages provides basic functionality to install, build, and deploy spack packages.
If you haven't installed Pakages yet or shelled into a pre-built container,
you should read :ref:`getting_started-installation` first. If you want to tweak
settings, read :ref:`getting_started-settings`. If you are looking to develop, meaning build, test,
and deploy your own packages, you should see :ref:`getting_started-developer-guide`.

Quick Start
===========

After installation, you'll first need spack to be on your path. If 
you want control over Pakages settings (discussed next) you should create your own copy of the config file.

.. code-block:: console

    # Init your user config
    $ pakages config init

This will create a ``$HOME/.pakages/settings.yml`` that you can customize to override
the defaults. To quickly edit:

.. code-block:: console

    $ pakages config edit

The settings will let you add trusted package registries to try pulling from (which
also can be set on the fly on the command line) along with a default registry to push to,
a tag to use, and default cache directory, and others. Browse :ref:`getting_started-settings` 
and ensure the settings are to your liking before continuing. And importantly - if you are just
using pakages to install the default provided trusted registry at pakages, you likely don't need to customize 
anything. Finally, make sure that you have spack added to your path, to be discovered by pakages.
If you are using a pre-built container, this will already be the case.

Commands
========

Pakages allows for easy install of different formats of packages, which currently
includes spack and Python (pip). 

-----
Spack
-----

The goal of the pakages spack builder to to make it easy to:

1. Host your own package.py recipes in a repository (also allowing for automated update of those recipes)
2. On any change, trigger an automated build for the package with spack develop
3. Install to spack using this build cache from GitHub packages.

For development, we provide (currently under development) `a set of packages, "pakages" <https://github.com/pakages>`_ , 
that you can easily install. The following commands work with the spack builder:


Build
-----

Pakages can install from spack just using pakages install (which is installable via pip so it can be on your path
more easily or in a Python environment). For Spack, the intended workflow is to build (and optionally push) when you
want to create a GitHub packages build cache, and then to install pointing at the cache. If you don't need to push to
GitHub packagese, build would be equivalent to manually creating a spack build cach. First, here is how to do that:

.. code-block:: console
    
    $ pakages --builder spack build zlib
    # equivalent to pakages -b spack build zlib
    Preparing to install zlib
    linux-ubuntu20.04-skylake
    [+] /home/vanessa/Desktop/Code/syspack/pakages/pakages/spack/opt/spack/linux-ubuntu20.04-skylake/gcc-9.3.0/zlib-1.2.11-3kmnsdv36qxm3slmcyrb326gkghsp6px

To push to GitHub packages, provide the push prefix (which will be appended
with your system architecture):

.. code-block:: console
    
    $ pakages --builder spack build zlib --push ghcr.io/pakages/zlib

The above will be extended to include ``ghcr.io/pakages/zlib-linux-ubuntu20.04-x86_64:latest``.
Note that if/when we want to support builds with customized names (not including host info) this can be
added - please open an issue. The current functionality is assuming that you are uploading a cache
using the same host you built on. 

Note that you can build from a local package repository structured liked this:

.. code-block:: console

    ./
      repos.yaml
      packages/
         mypackage/
            package.py
         zlib/
            package.py



Install
-------

Finally, when you are ready to install (using the GitHub packages build
cache) you can do:

.. code-block:: console
    
    $ pakages install --builder spack zlib --use-cache ghcr.io/pakages/zlib-linux-ubuntu20.04-x86_64:latest

The above will prepare the build cache, add it, and then perform the install, allowing spack to decide
if a binary and libraries are compatible.


------
Python
------

The goal of the Python builder is to make it easy to "release" your Python packages
to GitHub packages, and then install in a consistent way (not developed yet).

If you have a repository with a setup.py, it is determined to be a Python package
and we will attempt to build with traditional approaches (e.g., setuptools).
Here is an example:

.. code-block:: console

    $ git clone https://github.com/vsoch/citelang /tmp/citelang
    $ cd /tmp/citelang
    $ pakages build

The above will generate the package archive, and also an sbom as a layer.
We have not yet developed a way to install to a common place (coming soon).


.. code-block:: console

    $ tree /tmp/pakages-tmp.67efwbmf/
    /tmp/pakages-tmp.67efwbmf/
    ├── citelang-0.0.31.tar.gz
    └── sbom.json

---------------
Shared Commands
---------------

The following commands are general and can work with any underlying builder.

Shell
-----

If you want a quick shell to interact with a client (example below with spack)

.. code-block:: console

    $ pakages -b spack shell
    Python 3.8.8 (default, Apr 13 2021, 19:58:26) 
    Type 'copyright', 'credits' or 'license' for more information
    IPython 7.30.1 -- An enhanced Interactive Python. Type '?' for help.

    In [1]: client
    Out[1]: [pakages-client]


Uninstall
---------

You can also uninstall a package, although this can likely be done with
the package manager being wrapped.

.. code-block:: console

    $ pakages -b spack uninstall zlib

    
Containers
----------

Pakages provide a set of `pre-built containers with Pakages <https://github.com/orgs/syspack/packages?repo_name=pakages>`_  that serve
as bases for being able to quickly spin up an environment and install. We intend to deprecate updating containers as the operating
systems that are provided are deprecated. E.g., at the time of writing this in 2022, the earliest Ubuntu version we are providing is 18.04.
As an example, let's run the ubuntu 18.04 container and install zlib.

.. code-block:: console

    $ docker run -it ghcr.io/syspack/pakages-ubuntu-22.04

oras is in the container to easily pull and push packages:

.. code-block:: console

    # which oras
    /usr/local/bin/oras


And then you can interact with ``pakages`` as needed. We will be updated these docs with more soon!


GitHub Action
-------------

You can use one of our GitHub actions to build (and optionally deploy the build cache)
to GitHub packages.

Build
^^^^^

Here is an example for a python package:

.. code-block:: yaml

    name: Test Action

    on:
      pull_request: []

    jobs:
      test-action:
        name: Test Build Action
        runs-on: ubuntu-latest
        steps:
          - name: Checkout Repository
            uses: actions/checkout@v3
        
          - name: Test Pakages Python Build
            uses: syspack/packages/action/build@main
            with:
              user: ${{ github.actor }}
              token: ${{ secrets.GITHUB_TOKEN }}
              builder: python
              package: .
              target: ghcr.io/syspack/pakages/pakages-bundle:latest


And for a spack package:

.. code-block:: yaml

    name: Test Action

    on:
      pull_request: []

    jobs:
      test-action-spack:
        name: Test Spack Build Action
        runs-on: ubuntu-latest
        steps:
          - name: Checkout Repository
            uses: actions/checkout@v3

          - name: Install Spack
            run: |
              git clone --depth 1 https://github.com/spack/spack /opt/spack
              echo "/opt/spack/bin" >> $GITHUB_PATH
              export PATH="/opt/spack/bin:$PATH"
              spack external find

          - name: Test Pakages Spack Build
            uses: ./action/build
            with:
              user: ${{ github.actor }}
              token: ${{ secrets.GITHUB_TOKEN }}
              builder: spack
              package: ./tests/spack flux-core
              target: ghcr.io/syspack/pakages-test/zlib:latest              

Note that the main difference is that for the second we are installing spack
and asking for the spack builder. The package includes the path to our repository
to add, and the name of the package (flux-core).

The following variables are available:

.. list-table:: GitHub Action Variables
   :widths: 25 65 10
   :header-rows: 1

   * - Name
     - Description
     - Default
   * - builder
     - The builder to use (e.g, spack)
     - unset
   * - package
     - package name to build (required)
     - unset
   * - repo
     - filesystem path to repo to add (with your package recipe)
     - . (PWD)
   * - target
     - target to upload to (defaults to GitHub repository)
     - unset
   * - user
     - username to authenticate GitHub packages
     - unset (required)
   * - token
     - token to authenticate GitHub packages
     - unset (required)
     
     
For an example, see `flux-framework/flux-spack <https://github.com/flux-framework/flux-spack>`_.
