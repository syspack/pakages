.. _getting_started-installation:

============
Installation
============

Paks can be installed from pypi, or from source. We recommend a container interaction
for the quickest way to get up and running via our `container bases <https://github.com/orgs/syspack/packages?repo_name=pakages>`_

Note that `spack <https://github.com/spack/spack>`_ is required to be on your path.
If you use the container, this will already be provided.

.. code:: console

    $ git clone --depth 1 https://github.com/spack/spack
    $ source spack/share/spack/setup-env.sh


Container
=========

It's recommended to interact with pakages via `one of the container bases <https://github.com/orgs/syspack/packages?repo_name=pakages>`_
mentioned previously. That might look like the following:

.. code:: console

    $ docker run -it ghcr.io/syspack/pakages-ubuntu-18.04
    # which pakages
    /usr/local/bin/pakages
    # which spack
    /opt/spack/bin/spack
    # which oras
    /usr/local/bin/oras

You'll notice that the container, along with pakages, also provides spack and `oras <https://oras.land>`_
which is used to interact with the GitHub packages registry.

Pypi
====

If you want to use Paks locally on your machine or via some custom install,
the module is available in pypi as `the pakages project <https://pypi.org/project/pakages/>`_.

.. code:: console

    $ pip install pakages

This will provide the latest release. If you want a branch or development version, you can install from GitHub, shown next.


Virtual Environment
===================

Here is how to clone the repository and do a local install.

.. code:: console

    $ git clone https://github.com/syspack/pakages
    $ cd pakages

Create a virtual environment (recommended)

.. code:: console

    $ python -m venv env
    $ source env/bin/activate


And then install (this is development mode, remove the -e to not use it)

.. code:: console

    $ pip install -e .

Installation of pakages adds an executable, ``pakages`` to your path.

.. code:: console

    $ which pakages
    /opt/conda/bin/pakages


Once it's installed, you should be able to inspect the client!


.. code-block:: console

    $ pakages --help


You'll next want to install or build packages, discussed in :ref:`getting-started`.
