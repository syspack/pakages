__author__ = "Vanessa Sochat, Alec Scott"
__copyright__ = "Copyright 2021-2022, Vanessa Sochat and Alec Scott"
__license__ = "Apache-2.0"

from pakages.client import get_client


def main(args, parser, extra, subparser):

    lookup = {"ipython": ipython, "python": python}
    shells = ["ipython", "python"]

    # The default shell determined by the command line client
    shell = args.interpreter
    if shell is not None:
        shell = shell.lower()
        if shell in lookup:
            try:
                return lookup[shell](args)
            except ImportError:
                pass

    # Otherwise present order of liklihood to have on system
    for shell in shells:
        try:
            return lookup[shell](args)
        except ImportError:
            pass


def create_client(args):
    return get_client(builder=args.builder, settings_file=args.settings_file)


def ipython(args):
    """
    Generate an IPython shell with the client.
    """
    client = create_client(args)  # noqa
    from IPython import embed

    embed()


def python(args):
    """
    Generate an python shell with the client.
    """
    import code

    client = create_client(args)
    code.interact(local={"client": client})
