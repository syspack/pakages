# Paks

## TODO

 - expand container bases to include more, possibly provide set of solid base images.
 - from @alecbcs - add "trusted" packages repo (tested, signed, etc.)
 - There is eventually going to be a design flaw in installing this if the user doesn't have write to the install location because of spack. Ug.
 - Can we have a nightly run to compare sboms for package releases to clair?
 - create pakages metadata spec for container labels? Also add spack labels to container
 - where can we put the trusted registry metadata, aside from the registry configs/labels? E.g., an interface?
 - get on conda for faster install
 
## Old Brainstorming

The project was originally going to be called "stack" but the pypi name wasn't available!

### Paks Organization

On a high level, Stack should be optimized to:

1. Install packages from the Github package caches. This ensures that installation is fast. And since we are optimizing for container installs, we will typically choose a core set of containers to provide binaries for. Since the installs are just downloading binaries, it should also be quick. This means we will need a similar logic / organization to a package install tree as is done with [spack](https://github.com/spack/spack), where packages are installed based on a hash of some kind under a common tree, and can be loaded as such.
2. Build containers.
3. Provide a community framework to empower individuals to build, test, and deploy. This should cut down on maintenance responsibility by some central team.

### stack Client

#### Building Packages

The stack client will be optimized to build packages from source, and this will be done
on GitHub (and likely with a GitHub action). When we are in a repository, that might look like:

```bash
$ stack build .
```

If we are on the command line and want to build a remote repository, that might look like:

```bash
$ stack build github.com/vanessa/salad
```

And then we would require the GitHub repository to provide some basic files for the install.
If we want to keep things in Go, likely it would be a module called package served at the repository:

```bash
package/
  package.go
```

and then a module named accordingly. E.g.,:

```bash
# go.mod
module github.com/username/packagename

go 1.16
```

I think this would be possible if each package was interacted with as a [plugin](https://github.com/vladimirvivien/go-plugin-example)
because then we could download the package to some known root, e.g.,:

```bash
/tmp/stack-install-xndfush
   packagename/
      go.mod
      go.sum
      package/
         package.go
```

And then via the plugin framework define the module as the path there, build an so, and then
load the package to then be built from source. Arguably this could also be done locally,
but it's more optimal to do in advance. There is a good example of using plugins [here](https://github.com/vladimirvivien/go-plugin-example/blob/b5d9c4134805a908c1b1320951cc3dd6d64d851c/greeter.go#L32).


##### Containers

The builds could be done in containers, and thus we would be controlling the architecture
and organization within the container. We could deploy a container, but we would be pushing GitHub
packages and adding them to a container.

1. Can we have a minimal filesystem / container base to install the tool?
2. Then can we grab packages (binaries) that the user wants to add (pre-built)
3. The container base would be akin to any other contianer base (e.g., ubuntu 16.04) and we may want to start with something that already exists
4. A user could easily build their own arch packages (maybe it's represented in the package metadata / arch name)

More abstractly, we want to have a package manager built around GitHub packages.
We can look at ones that already exist to get a better sense of how others do that.

#### Installing Packages

Installation would be straight forward - you would install via a GitHub repository URI:

```bash
$ stack install github.com/usernamename/packagename
```
And I'm thinking we could have an entire org that serves packages, and then they would be provided
in a registry known to stack. Then instead of packagename, if that repository is registered under packagename,
we would just do:

```bash
$ stack install packagename
```

And stack would:

1. Lookup the package in the registry
2. Run the same stack install with the full GitHub URI

During install, we would basically need to match the architecture of the package
to what is requested, and we would provide a reasonable set. This package manager is not 
intended for HPC, it would be intended for installing inside containers.
