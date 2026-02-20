import asyncio
from collections import abc
from pathlib import Path

import aioshutil
import anyio
import httpx

from wheely_bucket import USER_AGENT
from wheely_bucket.parse_lockfile import PackageSpec, is_compatible_with

MAX_CONCURRENT_DOWNLOADS = 5


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


async def _download_package(
    client: httpx.AsyncClient, url: str, dest: Path, wheel_name: str, semaphore: asyncio.Semaphore
) -> None:
    out_filepath = dest / wheel_name
    async with semaphore:
        print(f"Downloading {out_filepath}")

        async with client.stream("GET", url) as r:
            if r.status_code == httpx.codes.OK:
                async with await anyio.open_file(out_filepath, "wb") as f:
                    async for chunk in r.aiter_bytes():
                        await f.write(chunk)
            else:
                print(f"Could not download package {wheel_name}: {r.status_code}")


async def download_packages(packages: abc.Iterable[PackageSpec], dest: Path) -> None:
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
            await aioshutil.copy(src=p.cached_wheel_path, dst=dest_filepath)
            continue

        to_download.append(p)

    semaphore = asyncio.Semaphore(MAX_CONCURRENT_DOWNLOADS)
    async with httpx.AsyncClient(headers={"User-Agent": USER_AGENT}) as client:
        dl_tasks = [
            _download_package(
                client=client,
                url=p.wheel_url,
                dest=dest,
                wheel_name=p.wheel_name,
                semaphore=semaphore,
            )
            for p in to_download
        ]
        await asyncio.gather(*dl_tasks)
