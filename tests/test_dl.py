from pathlib import Path

from pytest_mock import MockerFixture

from wheely_bucket.cli import _dl_pipeline
from wheely_bucket.parse_lockfile import PackageSpec
from wheely_bucket.wrap_dl import pip_dl


def test_dl_pipeline_infer_python_platform(mocker: MockerFixture) -> None:
    patched = mocker.patch("wheely_bucket.cli.pip_dl")

    specs = [PackageSpec.from_string("black")]
    dest = Path()

    _dl_pipeline(
        specs=specs,
        dest=dest,
        python_version=None,
        platform=None,
    )

    patched.assert_called_once_with(
        packages=specs,
        dest=dest,
        python_version=None,
        platform=None,
    )


def test_dl_pipeline_multi_python(mocker: MockerFixture) -> None:
    patched = mocker.patch("wheely_bucket.cli.pip_dl")

    specs = [PackageSpec.from_string("black")]
    dest = Path()
    python_version = "3.13,3.14"

    _dl_pipeline(
        specs=specs,
        dest=dest,
        python_version=python_version,
        platform=None,
    )

    assert patched.call_count == 2


def test_dl_pipeline_multi_platform(mocker: MockerFixture) -> None:
    patched = mocker.patch("wheely_bucket.cli.pip_dl")

    specs = [PackageSpec.from_string("black")]
    dest = Path()
    platform = "arm64,win_amd64"

    _dl_pipeline(
        specs=specs,
        dest=dest,
        python_version=None,
        platform=platform,
    )

    assert patched.call_count == 2


def test_dl_pipeline_multi_python_multi_platform(mocker: MockerFixture) -> None:
    patched = mocker.patch("wheely_bucket.cli.pip_dl")

    specs = [PackageSpec.from_string("black")]
    dest = Path()
    python_version = "3.13,3.14"
    platform = "arm64,win_amd64"

    _dl_pipeline(
        specs=specs,
        dest=dest,
        python_version=python_version,
        platform=platform,
    )

    assert patched.call_count == 4


def test_pip_dl_infer_python_platform(mocker: MockerFixture) -> None:
    patched = mocker.patch("wheely_bucket.wrap_dl.subprocess.check_call")

    pip_dl(
        packages=[PackageSpec.from_string("black")],
        dest=Path(),
        python_version=None,
        platform=None,
    )

    args = patched.call_args.args[0]
    assert "--python-version" not in args
    assert "--platform" not in args


def test_pip_dl_specify_python_ver(mocker: MockerFixture) -> None:
    patched = mocker.patch("wheely_bucket.wrap_dl.subprocess.check_call")

    pip_dl(
        packages=[PackageSpec.from_string("black")],
        dest=Path(),
        python_version="3.14",
        platform=None,
    )

    args = patched.call_args.args[0]
    assert "--python-version" in args
    assert "--platform" not in args


def test_pip_dl_specify_platform(mocker: MockerFixture) -> None:
    patched = mocker.patch("wheely_bucket.wrap_dl.subprocess.check_call")

    pip_dl(
        packages=[PackageSpec.from_string("black")],
        dest=Path(),
        python_version=None,
        platform="win_amd64",
    )

    args = patched.call_args.args[0]
    assert "--python-version" not in args
    assert "--platform" in args
