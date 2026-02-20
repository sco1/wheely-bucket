from collections import abc
from pathlib import Path

import pytest
from pytest_mock import MockerFixture

from wheely_bucket.dl_manager import download_packages, filter_packages
from wheely_bucket.parse_lockfile import PackageSpec

# fmt: off
BASE_PACKAGES = (
    PackageSpec.from_url("https://a.b.c/black-25.1.0-cp312-cp312-macosx_10_13_x86_64.whl"),
    PackageSpec.from_url("https://a.b.c/black-25.1.0-cp312-cp312-macosx_11_0_arm64.whl"),
    PackageSpec.from_url("https://a.b.c/black-25.1.0-cp312-cp312-manylinux_2_17_x86_64.manylinux2014_x86_64.manylinux_2_28_x86_64.whl"),
    PackageSpec.from_url("https://a.b.c/black-25.1.0-cp312-cp312-win_amd64.whl"),
    PackageSpec.from_url("https://a.b.c/black-25.1.0-cp313-cp313-macosx_10_13_x86_64.whl"),
    PackageSpec.from_url("https://a.b.c/black-25.1.0-cp313-cp313-macosx_11_0_arm64.whl"),
    PackageSpec.from_url("https://a.b.c/black-25.1.0-cp313-cp313-manylinux_2_17_x86_64.manylinux2014_x86_64.manylinux_2_28_x86_64.whl"),
    PackageSpec.from_url("https://a.b.c/black-25.1.0-cp313-cp313-win_amd64.whl"),
    PackageSpec.from_url("https://a.b.c/black-25.1.0-py3-none-any.whl"),
)
# fmt: on

PACKAGE_FILTER_TEST_CASES = (
    (
        ((3, 13),),
        ("win_amd64",),
        {
            PackageSpec.from_url("https://a.b.c/black-25.1.0-cp313-cp313-win_amd64.whl"),
            PackageSpec.from_url("https://a.b.c/black-25.1.0-py3-none-any.whl"),
        },
    ),
    (
        ((3, 12), (3, 13)),
        ("win_amd64",),
        {
            PackageSpec.from_url("https://a.b.c/black-25.1.0-cp312-cp312-win_amd64.whl"),
            PackageSpec.from_url("https://a.b.c/black-25.1.0-cp313-cp313-win_amd64.whl"),
            PackageSpec.from_url("https://a.b.c/black-25.1.0-py3-none-any.whl"),
        },
    ),
)


@pytest.mark.parametrize(("python_versions", "platforms", "truth_out"), PACKAGE_FILTER_TEST_CASES)
def test_filter_packages(
    python_versions: abc.Iterable[tuple[int, int]] | None,
    platforms: abc.Iterable[str] | None,
    truth_out: set[PackageSpec],
) -> None:
    filtered = filter_packages(
        packages=BASE_PACKAGES, python_versions=python_versions, platforms=platforms
    )
    print(filtered)
    assert filtered == truth_out


@pytest.mark.asyncio
async def test_download_packages_already_exist(
    tmp_path: Path,
    capsys: pytest.CaptureFixture,
) -> None:
    DUMMY_PACKAGE = PackageSpec.from_url("https://a.b.c/black-25.1.0-py3-none-any.whl")
    download_wheel = tmp_path / DUMMY_PACKAGE.wheel_name
    download_wheel.touch()

    await download_packages(packages=(DUMMY_PACKAGE,), dest=tmp_path)

    captured = capsys.readouterr()
    assert captured.out.startswith("Wheel was already downloaded")


@pytest.mark.asyncio
async def test_download_packages_in_pip_cache(
    tmp_path: Path,
    capsys: pytest.CaptureFixture,
    mocker: MockerFixture,
) -> None:
    # Setup & mock a fake pip cache location so we aren't actually messing with pip
    dummy_pip_cache = tmp_path / "pip_cache"
    mocker.patch("wheely_bucket.parse_lockfile.PIP_HTTP_CACHE", dummy_pip_cache)

    DUMMY_PACKAGE = PackageSpec.from_url("https://a.b.c/black-25.1.0-py3-none-any.whl")
    DUMMY_PACKAGE.cached_wheel_path.parent.mkdir(parents=True)
    DUMMY_PACKAGE.cached_wheel_path.touch()

    download_wheel = tmp_path / DUMMY_PACKAGE.wheel_name
    await download_packages(packages=(DUMMY_PACKAGE,), dest=tmp_path)

    captured = capsys.readouterr()
    assert captured.out.startswith("Using cached")
    assert download_wheel.exists()
