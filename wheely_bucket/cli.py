import itertools
from collections import abc
from pathlib import Path

import typer

from wheely_bucket.parse_lockfile import PackageSpec, parse_project
from wheely_bucket.wrap_dl import pip_dl

CUR_DIR = Path()

wb_cli = typer.Typer(
    no_args_is_help=True,
    add_completion=False,
    help="Cache wheels for your locked dependencies.",
)


def _dl_pipeline(
    specs: abc.Iterable[PackageSpec],
    dest: Path,
    python_version: abc.Iterable[str] | None,
    platform: abc.Iterable[str] | None,
) -> None:
    """Helper download pipeline to iterate over python version & platform permutations."""
    if (python_version is not None) and (platform is not None):
        for ver, plat in itertools.product(python_version, platform):
            pip_dl(packages=specs, dest=dest, python_version=ver, platform=plat)
    elif python_version is not None:
        for ver in python_version:
            # I think the narrowing is correct here, but mypy doesn't seem to infer accurately
            # Being more explicit with the elif fixes one problem but makes another for the else
            # statement, so everything gets uglier and I like it this way better
            pip_dl(packages=specs, dest=dest, python_version=ver, platform=platform)  # type: ignore[arg-type]
    elif platform is not None:
        for plat in platform:
            pip_dl(packages=specs, dest=dest, python_version=python_version, platform=plat)
    else:
        pip_dl(packages=specs, dest=dest, python_version=python_version, platform=platform)


@wb_cli.command()
def package(
    packages: list[str],
    dest: Path = CUR_DIR,
    python_version: list[str] | None = None,
    platform: list[str] | None = None,
) -> None:
    """
    Download wheels for the the specified package(s).

    Package specifiers are expected in a form understood by pip, e.g. "black" or "black==25.1.0".

    python_version and platform are expected in a form understood by 'pip download'; multiple
    targets may be specified. If not specified, pip will default to matching the currently running
    interpreter.
    """
    specs = (PackageSpec.from_string(p) for p in packages)
    _dl_pipeline(specs=specs, dest=dest, python_version=python_version, platform=platform)


@wb_cli.command()
def project(
    topdir: Path,
    dest: Path = CUR_DIR,
    recurse: bool = False,
    python_version: list[str] | None = None,
    platform: list[str] | None = None,
    lock_filename: str = "uv.lock",
) -> None:
    """
    Download wheels specified by the project's uv lockfile.

    python_version and platform are expected in a form understood by 'pip download'; multiple
    targets may be specified. If not specified, pip will default to matching the currently running
    interpreter.

    If recurse is True, the specified topdir is assumed to contain one or more projects managed by
    uv, and will recursively parse all contained lockfiles for locked dependencies.
    """
    specs = parse_project(base_dir=topdir, lock_filename=lock_filename, recurse=recurse)
    _dl_pipeline(specs=specs, dest=dest, python_version=python_version, platform=platform)


if __name__ == "__main__":
    wb_cli()
