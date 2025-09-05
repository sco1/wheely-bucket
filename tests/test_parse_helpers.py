from pathlib import Path

import pytest
from packaging.tags import parse_tag
from packaging.version import Version

from wheely_bucket.parse_lockfile import PIP_HTTP_CACHE, PackageSpec, parse_project


def test_package_spec_from_url() -> None:
    WHEEL_URL = "https://a.b.c/packages/def/pip-25.2-py3-none-any.whl"
    TRUTH_P = PackageSpec(
        package_name="pip",
        version=Version("25.2"),
        wheel_name="pip-25.2-py3-none-any.whl",
        wheel_url=WHEEL_URL,
        tags=parse_tag("py3-none-any"),
    )

    assert PackageSpec.from_url(WHEEL_URL) == TRUTH_P


def test_package_from_lock_spec() -> None:
    LOCK_SPEC = {
        "name": "pip",
        "version": "25.2",
        "source": {"registry": "https://pypi.org/simple"},
        "sdist": {
            "url": "...",
            "hash": "...",
            "size": 59428,
            "upload-time": "2025-06-10T12:42:39.607Z",
        },
        "wheels": [
            {
                "url": "https://a.b.c/packages/def/pip-25.2-py3-none-any.whl",
                "hash": "...",
                "size": 1752557,
                "upload-time": "2025-07-30T21:50:13.323Z",
            }
        ],
    }

    TRUTH_P = PackageSpec(
        package_name="pip",
        version=Version("25.2"),
        wheel_name="pip-25.2-py3-none-any.whl",
        wheel_url="https://a.b.c/packages/def/pip-25.2-py3-none-any.whl",
        tags=parse_tag("py3-none-any"),
    )

    assert PackageSpec.from_lock(LOCK_SPEC) == {TRUTH_P}


def test_package_from_lock_spec_no_wheels() -> None:
    LOCK_SPEC = {
        "name": "pip",
        "version": "25.2",
        "source": {"registry": "https://pypi.org/simple"},
        "sdist": {
            "url": "...",
            "hash": "...",
            "size": 59428,
            "upload-time": "2025-06-10T12:42:39.607Z",
        },
    }

    assert PackageSpec.from_lock(LOCK_SPEC) == set()


def test_url_hash() -> None:
    WHEEL_URL = "https://a.b.c/packages/def/pip-25.2-py3-none-any.whl"
    p = PackageSpec.from_url(WHEEL_URL)

    assert p.url_hash == "f3843723907efec12c032a6c44eeebbba2618c74a78c3a579d6f504c"


def test_cache_path() -> None:
    WHEEL_URL = "https://a.b.c/packages/def/pip-25.2-py3-none-any.whl"
    p = PackageSpec.from_url(WHEEL_URL)

    TRUTH_PATH = (
        PIP_HTTP_CACHE / "f/3/8/4/3/f3843723907efec12c032a6c44eeebbba2618c74a78c3a579d6f504c.body"
    )

    assert p.cached_wheel_path == TRUTH_PATH


DUMMY_LOCK = """\
version = 1
revision = 3
requires-python = ">=3.12"

[[package]]
name = "cogapp"
version = "3.5.1"
source = { registry = "https://pypi.org/simple" }
sdist = { url = "...", hash = "...", size = 59428, upload-time = "2025-06-10T12:42:39.607Z" }
wheels = [
    { url = "https://a.b.c/packages/abc/cogapp-3.5.1-py3-none-any.whl", hash = "...", size = 30390, upload-time = "2025-06-10T12:42:38.203Z" },
]

[[package]]
name = "pip"
version = "25.2"
source = { registry = "https://pypi.org/simple" }
sdist = { url = "...", hash = "...", size = 1840021, upload-time = "2025-07-30T21:50:15.401Z" }
wheels = [
    { url = "https://a.b.c/packages/def/pip-25.2-py3-none-any.whl", hash = "...", size = 1752557, upload-time = "2025-07-30T21:50:13.323Z" },
]

[[package]]
name = "wheely-bucket"
version = "0.1.0"
source = { editable = "." }
"""


def test_parse_project_invalid_basedir_raises() -> None:
    missing_dir = Path() / "m/i/s/s/i/n/g/"
    with pytest.raises(ValueError, match="base directory"):
        _ = parse_project(base_dir=missing_dir)


def test_parse_project_no_lockfile_raises(tmp_path: Path) -> None:
    with pytest.raises(ValueError, match="Lockfile"):
        _ = parse_project(base_dir=tmp_path)


def test_parse_project(tmp_path: Path) -> None:
    lf = tmp_path / "uv.lock"
    lf.write_text(DUMMY_LOCK)

    TRUTH_PACKAGES = {
        PackageSpec(
            package_name="cogapp",
            version=Version("3.5.1"),
            wheel_name="cogapp-3.5.1-py3-none-any.whl",
            wheel_url="https://a.b.c/packages/abc/cogapp-3.5.1-py3-none-any.whl",
            tags=parse_tag("py3-none-any"),
        ),
        PackageSpec(
            package_name="pip",
            version=Version("25.2"),
            wheel_name="pip-25.2-py3-none-any.whl",
            wheel_url="https://a.b.c/packages/def/pip-25.2-py3-none-any.whl",
            tags=parse_tag("py3-none-any"),
        ),
    }

    assert parse_project(base_dir=tmp_path) == TRUTH_PACKAGES
