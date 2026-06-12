import click

from . import __version__


@click.group()
@click.version_option(version=__version__)
def cli():
    """Measurement Integrity Intelligence Engine (MIIE)."""
    pass


if __name__ == "__main__":
    cli()
