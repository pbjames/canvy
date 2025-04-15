from typer import Typer

from cansync.utils import setup_logging

cli = Typer()


@cli.command()
def main(): ...


if __name__ == "__main__":
    setup_logging()
    cli()
