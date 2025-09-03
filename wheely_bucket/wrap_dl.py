import subprocess
import sys
from collections import abc, defaultdict
from pathlib import Path

from wheely_bucket.parse_lockfile import PackageSpec


def split_conflicting(packages: abc.Iterable[PackageSpec]) -> abc.Iterator[list[PackageSpec]]:
    """
    Split the provided `PackageSpec`s into the largest possible non-conflicting chunks.

    Because `pip download` attempts to resolve the dependencies passed, multiple locked versions of
    the same package will result in a `ResolutionImpossible` error.
    """
    mapped_packages = defaultdict(list)
    for p in packages:
        mapped_packages[p.package_name].append(p.locked_ver)

    while True:
        chunk = []
        for pname, versions in mapped_packages.items():
            if len(versions) > 1:
                chunk.append(PackageSpec(package_name=pname, locked_ver=versions.pop()))

        if chunk:
            yield chunk
        else:
            break

    yield [
        PackageSpec(package_name=pname, locked_ver=versions.pop())
        for pname, versions in mapped_packages.items()
    ]


def pip_dl(
    packages: abc.Iterable[PackageSpec],
    dest: Path,
    python_version: str | None = None,
    platform: str | None = None,
) -> None:
    """
    Thin wrapper around the `pip download` CLI invocation.

    Semantics are largely shared with `pip download`. `python_version` and `platform` may be any
    string specification understood by `pip`; if not specified `pip` will default to matching the
    currently running interpreter.

    See: https://pip.pypa.io/en/stable/cli/pip_download/ for additional information.

    NOTE: `--only-binary=:all:` will always be passed to the invoked CLI command; sdists are
    currently not considered by this tool.

    NOTE: `packages` is assumed to not contain conflicting dependency specifications, e.g.
    `abc==0.1.0` and `abc==0.2.0`, which will cause `pip` to throw a `ResolutionImpossible` error.
    Download of conflicting packages can still be done into the same destination folder, but must be
    done in separate calls.
    """
    pip_cmd = [
        sys.executable,
        "-m",
        "pip",
        "download",
        "-d",
        f"{dest}",
        "--only-binary=:all:",
    ]

    if python_version is not None:
        pip_cmd.extend(
            [
                "--python-version",
                python_version,
            ]
        )

    if platform is not None:
        pip_cmd.extend(
            [
                "--platform",
                platform,
            ]
        )

    pip_cmd.extend(p.spec for p in packages)

    subprocess.check_call(pip_cmd)
