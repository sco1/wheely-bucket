from collections import abc
from pathlib import Path

import typer
from packaging.requirements import Requirement
from packaging.version import Version

from wheely_bucket.dl_manager import download_packages, filter_packages
from wheely_bucket.package_query import filtered_pypi_query
from wheely_bucket.parse_lockfile import PackageSpec, parse_project

CWD = Path()

wb_cli = typer.Typer(
    no_args_is_help=True,
    add_completion=False,
    help="Cache wheels for your locked dependencies.",
)


def _dl_pipeline(
    packages: abc.Iterable[PackageSpec],
    dest: Path,
    python_version: str | None,
    platform: str | None,
) -> None:
    if python_version is not None:
        pyvers = []
        for split_ver in python_version.split(","):
            ver = Version(split_ver)
            pyvers.append((ver.major, ver.minor))
    else:
        pyvers = None

    if platform is not None:
        plat = platform.split(",")
    else:
        plat = None

    dest.mkdir(parents=True, exist_ok=True)
    filtered = filter_packages(packages=packages, python_versions=pyvers, platforms=plat)
    download_packages(packages=filtered, dest=dest)


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

    python_version and platform are expected in a form understood by pip; multiple comma-delimited
    targets may be specified. If not specified, pip will default to matching the currently running
    interpreter.
    """
    reqs = [Requirement(p) for p in packages]
    wheels = set()
    for r in reqs:
        wheels |= filtered_pypi_query(r)

    _dl_pipeline(packages=wheels, dest=dest, python_version=python_version, platform=platform)


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
    managed by uv, and will recursively parse all contained lockfiles for locked dependencies.

    python_version and platform are expected in a form understood by pip; multiple comma-delimited
    targets may be specified. If not specified, pip will default to matching the currently running
    interpreter.
    """
    if recurse:
        pattern = f"**/{lock_filename}"
    else:
        pattern = lock_filename

    lockfiles = tuple(topdir.glob(pattern, case_sensitive=False))
    print(f"Found {len(lockfiles)} lockfiles to process...")

    packages = set()
    for lf in lockfiles:
        packages |= parse_project(lf.parent, lock_filename=lock_filename)

    _dl_pipeline(packages=packages, dest=dest, python_version=python_version, platform=platform)


if __name__ == "__main__":
    wb_cli()
