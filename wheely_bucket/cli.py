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


@wb_cli.command()
def package(
    packages: list[str],
    dest: Path = CUR_DIR,
    python_version: str | None = None,
    platform: str | None = None,
) -> None:
    """
    Download wheels for the the specified package(s).

    Package specifiers are expected in a form understood by pip, e.g. "black" or "black==25.1.0".

    python_version and platform are expected in a form understood by 'pip download'; if not
    specified pip will default to matching the currently running interpreter.
    """
    specs = (PackageSpec.from_string(p) for p in packages)
    pip_dl(packages=specs, dest=dest, python_version=python_version, platform=platform)


@wb_cli.command()
def project(
    topdir: Path,
    dest: Path = CUR_DIR,
    recurse: bool = False,
    python_version: str | None = None,
    platform: str | None = None,
    lock_filename: str = "uv.lock",
) -> None:
    """
    Download wheels specified by the project's uv lockfile.

    python_version and platform are expected in a form understood by 'pip download'; if not
    specified pip will default to matching the currently running interpreter.

    If recurse is True, the specified topdir is assumed to contain one or more projects managed by
    uv, and will recursively parse all contained lockfiles for locked dependencies.
    """
    specs = parse_project(base_dir=topdir, lock_filename=lock_filename, recurse=recurse)
    pip_dl(packages=specs, dest=dest, python_version=python_version, platform=platform)


if __name__ == "__main__":
    wb_cli()
