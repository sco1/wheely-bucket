import subprocess
import sys
from pathlib import Path

from wheely_bucket.parse_lockfile import PackageSpec


def pip_dl(
    package: PackageSpec, dest: Path, python_version: str | None = None, platform: str | None = None
) -> None:
    """
    Thin wrapper around the `pip download` CLI invocation.

    Semantics are largely shared with `pip download`. `python_version` and `platform` may be any
    string specification understood by `pip`; if not specified `pip` will default to matching the
    currently running interpreter.

    See: https://pip.pypa.io/en/stable/cli/pip_download/ for additional information.

    NOTE: `--only-binary=:all:` will always be passed to the invoked CLI command; sdists are
    currently not considered by this tool.
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

    pip_cmd.append(package.spec)

    subprocess.check_call(pip_cmd)
