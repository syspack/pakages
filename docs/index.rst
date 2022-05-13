.. _manual-main:

====
Paks
====

.. image:: https://img.shields.io/github/stars/syspack/pakages?style=social
    :alt: GitHub stars
    :target: https://github.com/syspack/pakages/stargazers

Paks is a framework for building community packages and containers 📦️

Paks is a wrapper around the spack package manager that aims to provide a set of consistent 
and trusted packages and environments, either for use separately or in combination with `syspack/pack <https://github.com/syspack/pakages>`_. 
It is optimized for install, build, and deploy of spack build caches to GitHub packages. 
The tool wraps spack to ensure that any installation first checks a repository of trusted pakages packages, 
and a Paks user can run one of a set of base containers with a chosen set of operating systems and matched compilers, 
and then quickly install binaries from the GitHub packages cache. Since the packages are built from the same base containers, we can have more assurance of a cache hit than if just running on a local machine. 

The packages are intended to be "trusted" because each package repository will be built and deployed with testing, 
and will use an automated tool (`binoc <https://github.com/alecbcs/binoc>`_) to always look for updates to package versions, 
along with updates from the spack upstream. The packages also will be provided with Software Bill’s of Materials (SBOMs) 
that will be added to the container and easy to interact with, eventually allowing the container to be scanned and 
compared to a vulnerability database.

You can see trusted packages under the `pakages <https://github.com/pakages>`_ organization. Trusted means
that they are built, tested, and deployed from modular repositories, and can be
installed into consistent container bases that Paks provides.

.. _main-goals:

-----
Goals
-----

If you are a developer, pakages is a framework that is optimized to help you build packages from source,
and distribute the binaries via GitHub packages and also provide robust metadata
and an organization scheme that works well for containers. Paks has focus on this build and deploy,
and then testing and automatically updating the individual packages provided.

If you are a Paks user, Paks aims to provide you consistnet and tested container environments for your
software.


To see the code, head over to the `repository <https://github.com/syspack/pakages/>`_.

.. _main-getting-started:

-------------------------
Getting started with Paks
-------------------------

Paks can be installed from pypi or directly from the repository. See :ref:`getting_started-installation` for
installation, and then the :ref:`getting-started` section for using pakages on the command line or 
from a provided base container.

.. _main-support:

-------
Support
-------

* For **bugs and feature requests**, please use the `issue tracker <https://github.com/syspack/pakages/issues>`_.
* For **contributions**, visit Spliced on `Github <https://github.com/syspack/pakages>`_.

---------
Resources
---------

`GitHub Repository <https://github.com/syspack/pakages>`_
    The code on GitHub.


.. toctree::
   :caption: Getting started
   :name: getting_started
   :hidden:
   :maxdepth: 2

   getting_started/index
   getting_started/user-guide
   getting_started/developer-guide

.. toctree::
    :caption: API Reference
    :name: api-reference
    :hidden:
    :maxdepth: 1

    api_reference/pakages
    api_reference/internal/modules
