.. _getting_started-user-guide:

==========
User Guide
==========

Pakages provides basic functionality to install, build, and deploy spack packages.
If you haven't installed Pakages yet or shelled into a pre-built container,
you should read :ref:`getting_started-installation` first. If you want to tweak
settings, read :ref:`getting_started-settings`.

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

Pakages provides the following commands via the ``pakages`` command line client.

Install
-------

Pakages allows for easy install of different formats of packages. Where do they come from?
We provide (currently under development) `a set of packages, "pakages" <https://github.com/pakages>`_ , 
that you can easily install as a Pak user. If you are looking to develop, meaning build, test,
and deploy your own packages, you should see :ref:`getting_started-developer-guide`.

Spack 
^^^^^

Since pakages is a wrapper to spack, you can install any list of packages that you would
install with spack, just using pakages install (which is installable via pip so it can be on your path
more easily or in a Python environment).


.. code-block:: console
    
    $ pakages install zlib
    Preparing to install zlib
    linux-ubuntu20.04-skylake
    [+] /home/vanessa/Desktop/Code/syspack/pakages/pakages/spack/opt/spack/linux-ubuntu20.04-skylake/gcc-9.3.0/zlib-1.2.11-3kmnsdv36qxm3slmcyrb326gkghsp6px


This is a traditional install, but it's also a little more! We generate a software
bill of materials (SBOM) to go alongside the install, and if the package is available as a binary
on GitHub packages in your trusted registry it will be retrieved there first. If you don't need either
this binary install or the SBOM, you could just install with spack. To change the registry to pull from on the fly
(given that you don't want to change permanently in your settings) add ``--registry``:

.. code-block:: console

    $ pakages install zlib --registry ghcr.io/myorg

Note that we use the manifest 
of the artifact to validate the checksum before installing it.

Local
^^^^^

If you have a package repository locally, e.g., a directory with this structure:

.. code-block:: console

    ./
      repos.yaml
      packages/
         mypackage/
            package.py
         zlib/
            package.py

Then you can install all packages via:


.. code-block:: console

    $ pakages install .

Pakages will detect that you want to install from the present working directory,
and then install appropriately. The above ``.`` will install all packages in the present working directory.
You'd likely want to use this in a CI recipe to build and deploy a single package repository, however it could
have a local use case too, in the case that you want to clone someone's package repository and install all of them.
If you don't want to install all packages in the local repository, you can also select a specific package by name:

.. code-block:: console

    $ pakages install . zlib


This install command is different from a traditional ``spack install zlib`` because we are providing an absolute
or relative path first to a packages repository before the package name.
The above command will add the package directory, and then install zlib from it. Finally, to install from
a repository with the same package structure but from a remote on GitHub:

.. code-block:: console

    $ pakages install https://github.com/pakages/zlib

The above will create a temporary repository to use, and then clean up.


Shell
-----

If you want a quick shell to interact with the Pak client and spack, you can do:

.. code-block:: console

    $ pakages shell
    Python 3.8.8 (default, Apr 13 2021, 19:58:26) 
    Type 'copyright', 'credits' or 'license' for more information
    IPython 7.30.1 -- An enhanced Interactive Python. Type '?' for help.

    In [1]: client
    Out[1]: [pakages-client]

You can also import anything from spack in the shell, so this is a useful developer command.


Build
-----

The main functionality of pakages is (drumroll) to build packages that are then easy to install
in a container, or again into the spack install that comes with Pakages. A basic build is going
to generate a build cache with one or more specs of interest. Any time you build and 
push to a trusted Pakages registry (the one in your settings) then this registry will be used as a cache for future installs. 
Here is how to build zlib:

.. code-block:: console

    $ pakages build zlib

By default, a build cache will be created in a temporary directory and the Pakages
saved there. This is recommended, as each pak is intended to be modular. If you want
to specify a custom cache (or one that is always used) you can add ``--cache-dir``.
You also might want to set a specific gpg key hash to sign with ``--key`` (otherwise
we will default to the first one we find that is commented to be intended for Spack).
When you do a build, it will show you the location of the build cache.


.. code-block:: console

    $ pakages build zlib
    Preparing to install zlib
    linux-ubuntu20.04-skylake
    [+] /home/vanessa/Desktop/Code/syspack/pakages/pakages/spack/opt/spack/linux-ubuntu20.04-skylake/gcc-9.3.0/zlib-1.2.11-3kmnsdv36qxm3slmcyrb326gkghsp6px
    ==> Pushing binary packages to file:///tmp/pakages-tmp.1by0dclj/build_cache
    gpg: using "DECA3181DA00313E633F963157BE6A82D830EA34" as default secret key for signing

Build also supports local and remote repositories, as outlined in install. For example:


.. code-block:: console

    $ pakages build .

Or build a package by name:

.. code-block:: console

    $ pakages build . zlib

Or build from a remote:

.. code-block:: console

    $ pakages build https://github.com/pakages/zlib

Akin to install, you can also specify a registry to add to look for build cache entries
to speed up the install:

.. code-block:: console

    $ pakages build zlib --registry ghcr.io/myorg


Build and Push
--------------

If you add ``--push`` with a GitHub repository (or other OCI registry that supports oras) identifier, we will
use a command line tool called oras to upload there:

.. code-block:: console

    $ pakages build zlib --push ghcr.io/syspack/pakages

It's recommeded to `install oras <https://oras.land/cli/>`_ so it's faster, but if you don't it will be bootstrapped (and you
can go off and have a sandwich or sword fight!). By default, the above with ``--push`` 
will build, push, and cleanup. You can disable cleanup:

.. code-block:: console

    $ pakages build zlib --no-cleanup --push ghcr.io/pakages

If you customize the ``--cache-dir`` folder cleanup will be disabled, as it is assumed that you don't want to delete a non-temporary directory.
To force a cleanup of a custom cache directory, add ``--force``

.. code-block:: console

    $ pakages build zlib --no-cleanup --force --push ghcr.io/pakages

The above examples show a push using a custom GitHub unique resource identifier. To use the default trusted registry from your settings, just do:

.. code-block:: console

    $ pakages build zlib --pushd


Push
----

If you have an existing build cache you want to push:

.. code-block:: console

    $ pakages push /tmp/pakages-tmp.nudv7k0u/ ghcr.io/syspack/pakages

Or push and cleanup:

.. code-block:: console

    $ pakages push --cleanup /tmp/pakages-tmp.nudv7k0u/ ghcr.io/syspack/pakages

You can optionally define a default ``cache_dir`` in your settings, in which case you can leave it out:

.. code-block:: console

    $ pakages push ghcr.io/syspack/pakages

The registry will be detected since it starts with ``ghcr.io`` and the default cache directory used. Alternatively,
leave the registry out to use the default, and provide the cache directory:

.. code-block:: console

    $ pakages push /tmp/pakages-tmp.nudv7k0u/

And finally, if you really want to streamline and use the default registry and cache directory, just push!

.. code-block:: console

    $ pakages push


Uninstall
---------

You can also uninstall a package.

.. code-block:: console

    $ pakages uninstall zlib


List
----

List installed packages as follows:

.. code-block:: console

    $ pakages list
    -- linux-ubuntu20.04-x86_64 / gcc@9.3.0 -------------------------
    zlib@1.2.11
    
    
Containers
----------

Pakages provide a set of `pre-built containers with Pakages <https://github.com/orgs/syspack/packages?repo_name=pakages>`_  that serve
as bases for being able to quickly spin up an environment and install. We intend to deprecate updating containers as the operating
systems that are provided are deprecated. E.g., at the time of writing this in 2022, the earliest Ubuntu version we are providing is 18.04.
As an example, let's run the ubuntu 18.04 container and install zlib.

.. code-block:: console

    $ docker run -it ghcr.io/syspack/pakages-ubuntu-18.04

oras is in the container to easily pull and push packages:

.. code-block:: console

    # which oras
    /usr/local/bin/oras


And then you can easily install.

.. code-block:: console

    # pakages install zlib
    Preparing to install zlib
   [+] /opt/spack/opt/spack/linux-ubuntu18.04-x86_64/gcc-7.5.0/zlib-1.2.11-3rlgy7ycxtoho44una6o3itgfjltkmpd


We will be updated these docs with more soon!
