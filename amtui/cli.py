# -*- coding: utf-8 -*-

"""Console script for amtui."""
import sys
import click
from amtui.main import main

@click.command()
def gui(args=None):
    """Console script for amtui."""
    return main()


if __name__ == "__main__":
    sys.exit(main())  # pragma: no cover
