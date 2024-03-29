# CHANGELOG

This is a manually generated log to track changes to the repository for each release.
Each section should include general headers such as **Implemented enhancements**
and **Merged pull requests**. Critical items to know are:

 - renamed commands
 - deprecated / removed commands
 - changed defaults
 - backward incompatible changes (recipe file format? image file format?)
 - migration guidance (how to convert images?)
 - changed behaviour (recipe sections work differently)

The versions coincide with releases on pip. Only major versions will be released as tags on Github.

## [0.0.x](https://github.scom/syspack/pakages/tree/main) (0.0.x)
 - only call spack from the command line, not reliable as API (0.0.21)
 - add new vendoring line imports (0.0.2)
 - bug with parsing hidden (and non package directories) in spack (0.0.19)
 - bugfixes to install and adding GitHub action (0.0.18)
   - checking for existing mirrors before adding blindly
 - updates to spack build (0.0.17)
 - adding multiprocessing workers (0.0.16)
 - tweaking install process (0.0.15)
 - refactoring artifact extraction to allow reuse (0.0.14)
   - adding exponential backoff and 5 retries for oras push
 - Ensuring pakages pushes a generic name too (0.0.13)
 - More control over custom push/pull registries and settings (0.0.12)
 - Added support for building local path or GitHub remote (0.0.11)
 - First release with ability to install, build, and push with oras (0.0.1)
 - Initial skeleton of project (0.0.0)
