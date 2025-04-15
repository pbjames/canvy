from typer import Typer

cli = Typer()


@cli.command()
def main(): ...


if __name__ == "__main__":
    cli()
