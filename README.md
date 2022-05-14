# Pakages

> Pakages is a framework for building community packages and containers 📦️

![docs/assets/img/paks.png](docs/assets/img/paks.png)

⭐️ [Documentation](https://syspack.github.io/pakages) ⭐️

You can see trusted packages under the [pakages](https://github.com/pakages) organization. Trusted means
that they are built, tested, and deployed from modular repositories, and can be
installed into consistent container bases that Pakages provides.

## Goals

We want a framework that is optimized to help people build packages from source,
and distribute the binaries via GitHub packages and also provide robust metadata
and an organization scheme that works well for containers. We want a focus on that
and then testing and automatically updating the individual packages provided.
Pakages provides this functionality by wrapping spack to perform builds, and then
providing tooling to release to a GitHub packages build cache, and to run base
containers that will reliably hit the cache.

🚧️ **under development** 🚧️

