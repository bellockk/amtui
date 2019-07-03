# -*- coding: utf-8 -*-

"""Console script for amtui."""
import sys
import click
from amtui.gui

@click.command()
def gui(args=None):
    """Console script for amtui."""
    click.echo("Replace this message by putting your code into "
               "amtui.cli.main")
    click.echo("See click documentation at http://click.pocoo.org/")
    return 0


if __name__ == "__main__":
    sys.exit(main())  # pragma: no cover
