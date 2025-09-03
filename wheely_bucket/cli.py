import itertools
from collections import abc
from pathlib import Path

import typer

from wheely_bucket.parse_lockfile import PackageSpec, parse_project
from wheely_bucket.wrap_dl import pip_dl, split_conflicting

CWD = Path()

wb_cli = typer.Typer(
    no_args_is_help=True,
    add_completion=False,
    help="Cache wheels for your locked dependencies.",
)


def _dl_pipeline(
    specs: abc.Iterable[PackageSpec],
    dest: Path,
    python_version: str | None,
    platform: str | None,
) -> None:
    """Helper download pipeline to iterate over python version & platform permutations."""
    if (python_version is not None) and (platform is not None):
        for ver, plat in itertools.product(python_version.split(","), platform.split(",")):
            pip_dl(packages=specs, dest=dest, python_version=ver, platform=plat)
    elif python_version is not None:
        for ver in python_version.split(","):
            pip_dl(packages=specs, dest=dest, python_version=ver, platform=platform)
    elif platform is not None:
        for plat in platform.split(","):
            pip_dl(packages=specs, dest=dest, python_version=python_version, platform=plat)
    else:
        pip_dl(packages=specs, dest=dest, python_version=python_version, platform=platform)


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
    specs = {PackageSpec.from_string(p) for p in packages}
    _dl_pipeline(specs=specs, dest=dest, python_version=python_version, platform=platform)


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
    managed by uv, and will recursively parse all contained lockfiles for locked dependencies. This
    may necessitate multiple calls to 'pip download' in order to avoid conflicting dependencies
    across projects.

    python_version and platform are expected in a form understood by 'pip download'; multiple
    comma-delimited targets may be specified. If not specified, pip will default to matching the
    currently running interpreter.
    """
    specs = parse_project(base_dir=topdir, lock_filename=lock_filename, recurse=recurse)

    # If spanning multiple projects, packages may need to be deconflicted otherwise pip's resolver
    # will fail
    if recurse:
        for chunk in split_conflicting(specs):
            _dl_pipeline(specs=chunk, dest=dest, python_version=python_version, platform=platform)
    else:
        _dl_pipeline(specs=specs, dest=dest, python_version=python_version, platform=platform)


if __name__ == "__main__":
    wb_cli()
