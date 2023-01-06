.. _getting_started-settings:

========
Settings
========

Most defaults should work without changing, however you will likely want to customize
settings in the case that you are deploying packages (as a developer)
or if you want to install from a different trusted registry (as a user).

Updating Settings
=================

To change defaults you can either edit the settings.yml file in the installation directory
at ``pakages/settings.yml`` or create a user-specific configuration by doing:


.. code-block:: console

    $ pakages config init
    Created user settings file /home/vanessa/.pakages/settings.yml


You can then change a setting, such as the username and email for your gpg key (used to sign
the build cache artifacts):


.. code-block:: console

    $ pakages config set username:dinosaur
    Updated username to be dinosaur
    $ pakages config set email:dinosaur@users.noreply.github.io
    Updated email to be dinosaur@users.noreply.github.io


These user settings will over-ride the default installation ones.

Settings Table
==============

The following variables can be configured in your user settings:

.. list-table:: Title
   :widths: 25 65 10
   :header-rows: 1

   * - Name
     - Description
     - Default
   * - username
     - A username to use to sign packages (only required when using build)
     - Defaults to your ``$USER``
   * - email
     - An email to use to sign packages (only required when using build)
     - Defaults to ``$USER@users.noreply.spack.io``
   * - trusted_packages_org
     - The trusted packages GitHub organization to install from
     - pakages
   * - trusted_packages_registry
     - The default trusted packages GitHub organization to push to. If no push registries are provided, we fallback to push here.
     - ghcr.io/pakages
   * - trusted_pull_registries
     - One or more registries to pull from.
     - [ghcr.io/pakages]
   * - cache_dir
     - A default cache directory to use - will only be cleaned up for build using ``--force``
     - unset
   * - default_tag
     - The default tag to use to push artifacts.
     - latest
   * - content_type
     - The default content type for the spack package (not recommended to change)
     - application/vnd.spack.package


Note that we will be extending settings to include allowing more than one trusted registry to be added,
and they will be queried in the order they are provided. We will also separate the trusted packages registry
to use for install from a default to push, as they could easily be different. These variables will also be added for customization on
the command line (not added yet).
