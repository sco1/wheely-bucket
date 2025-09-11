import shutil
from collections import abc
from pathlib import Path

import httpx

from wheely_bucket import USER_AGENT
from wheely_bucket.parse_lockfile import PackageSpec, is_compatible_with


def filter_packages(
    packages: abc.Iterable[PackageSpec],
    python_versions: abc.Iterable[tuple[int, int]] | None = None,
    platforms: abc.Iterable[str] | None = None,
) -> set[PackageSpec]:
    """
    Filter out packages that aren't compatible with the given Python version & platform constraints.

    Python version(s) contained in `python_versions` are assumed to be a two-item tuple representing
    the targeted Python version, e.g. `(3, 14)`. If `None`, the currently running interpreter is
    used.

    Platform(s) contained in `platforms` are assumed to be strings identifying the desired target
    platform, e.g. `'win_amd64'` or `'macosx_11_0_arm64'`. If `None`, the currently running platform
    is used.
    """
    keep_packages: set[PackageSpec] = set()
    for p in packages:
        if python_versions is None:
            if is_compatible_with(tags=p.tags, python_version=python_versions, platforms=platforms):
                keep_packages.add(p)
        else:
            for pyver in python_versions:
                if is_compatible_with(tags=p.tags, python_version=pyver, platforms=platforms):
                    keep_packages.add(p)
                    break

    return keep_packages


def download_packages(packages: abc.Iterable[PackageSpec], dest: Path) -> None:
    """
    Attempt to download the specified package(s) to the destination directory.

    Prior to attempting to download, both `pip`'s cache and the destination directory are checked to
    see if the package's wheel has already been downloaded.
    """
    # Check caches first, then queue any files that need downloading so a single session can be used
    to_download: list[PackageSpec] = []
    for p in packages:
        dest_filepath = dest / p.wheel_name

        # Check if wheel is already in destination
        if dest_filepath.exists():
            print(f"Wheel was already downloaded: {dest_filepath}")
            continue

        # Check if wheel is already in pip's cache
        if p.cached_wheel_path.exists():
            print(f"Using cached {p.wheel_name}")

            # pip's cache names this as the hashed URL
            shutil.copy(src=p.cached_wheel_path, dst=dest_filepath)
            continue

        to_download.append(p)

    with httpx.Client(headers={"User-Agent": USER_AGENT}) as client:
        for p in to_download:
            dest_filepath = dest / p.wheel_name
            with client.stream("GET", p.wheel_url) as r:
                if r.status_code == httpx.codes.OK:
                    with dest_filepath.open("wb") as f:
                        for chunk in r.iter_bytes():
                            f.write(chunk)

                    print(f"Saved {dest_filepath}")
                else:
                    print(f"Could not download package {p.wheel_name}: {r.status_code}")
