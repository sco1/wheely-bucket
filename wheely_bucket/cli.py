from pathlib import Path

import typer

CWD = Path()

wb_cli = typer.Typer(
    no_args_is_help=True,
    add_completion=False,
    help="Cache wheels for your locked dependencies.",
)


@wb_cli.command()
def package(
    packages: list[str] = typer.Argument(..., help="Package(s) to download"),
    dest: Path = typer.Option(CWD, file_okay=False, help="Destination directory"),
    python_version: str | None = typer.Option(None, help="Python interpreter version(s)"),
    platform: str | None = typer.Option(None, help="Platform specification(s)"),
) -> None:
    """
    Download wheels for the the specified package(s).

    Package specifiers are expected in a form understood by pip, e.g. "black" or "black==25.1.0";
    multiple packages may be specified.

    python_version and platform are expected in a form understood by 'pip download'; multiple
    comma-delimited targets may be specified. If not specified, pip will default to matching the
    currently running interpreter.
    """
    raise NotImplementedError


@wb_cli.command()
def project(
    topdir: Path = typer.Argument(..., file_okay=False, help="Base directory"),
    dest: Path = typer.Option(CWD, help="Destination directory", file_okay=False),
    recurse: bool = typer.Option(
        False, "-r", "--recurse", help="Parse child directories for lockfiles [default: False]"
    ),
    lock_filename: str = typer.Option("uv.lock", help="Name of lockfile to match"),
    python_version: str | None = typer.Option(None, help="Python interpreter version(s)"),
    platform: str | None = typer.Option(None, help="Platform specification(s)"),
) -> None:
    """
    Download wheels specified by the project's uv lockfile.

    If recurse is True, the specified base directory is assumed to contain one or more projects
    managed by uv, and will recursively parse all contained lockfiles for locked dependencies. To
    avoid resolver issues, 'pip download' is called for each child project discovered.

    python_version and platform are expected in a form understood by 'pip download'; multiple
    comma-delimited targets may be specified. If not specified, pip will default to matching the
    currently running interpreter.
    """
    raise NotImplementedError


if __name__ == "__main__":
    wb_cli()
