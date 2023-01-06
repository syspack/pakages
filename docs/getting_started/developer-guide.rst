.. _getting_started-developer-guide:

===============
Developer Guide
===============

This developer guide includes more detail about how to build and distribute your own
pakages repository, or how to create a module package repository.
If you haven't read :ref:`getting_started-installation` you should do that first, along
with learning how to customize settings via :ref:`getting_started-settings`.
You will need to set a username and email to sign packages.

Developer Goals
===============

Pakages is a packaging framework that is optimized for community packages, meaning that
anyone can generate a simple repository with a package specification and then:

1. The repository automatically detects new versions of a package upstream and builds
2. Building is recommended to perform testing
3. A successful update, build, and test leads to a new release
4. The repository then serves metadata about the package via RESTful API
5. (Optionally) the repository can provide single containers

While we use Spack as the underlying manager for building, we have extended a Spack
spec and other concepts to be flexible to installing from a source like GitHub.


Pakages Development
===================

The following sections will provide detail about how to provide packages.


GitHub Token
------------

If you intend to push packages to a registry, you will need to provide a ``GITHUB_TOKEN``
in the environment. The CI recipes will give you an error if you forget to add this in
your workflow, and locally running Pak from the command line will too.


GitHub Packages
---------------

If you are using Pakages as a developer, you likely want to build and deploy binaries
of your own packages. This means you will need to push packages to your organization,
and ideally via an automated workflow that deploys to a specific repository namespace.
To allow packages to be pushed you will need to go to Settings -> Packages
and ensure that the public box is checked. Otherwise, all packages will be private (and not seen by
the tool) unless you are using them privately in CI only. Note that by default we use
packages from `the pakages organization <https://github.com/pakages>`_ , which you likely
won't have permission to push to, but you can pull/install from.


Repository Creation
-------------------

These instructions will be written soon! We are still working on core of Pakages and
developing the CI workflows for a package repository.
