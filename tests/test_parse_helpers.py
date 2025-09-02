from pathlib import Path

import pytest

from wheely_bucket.parse_lockfile import PackageSpec, parse_project


def test_packagespec_from_lock_spec() -> None:
    LOCK_SPEC = {"name": "black", "version": "25.1.0"}
    TRUTH_SPEC = PackageSpec(package_name="black", locked_ver="==25.1.0")

    assert PackageSpec.from_lock(LOCK_SPEC) == TRUTH_SPEC


FROM_STR_TEST_CASES = (
    ("black==25.1.0", PackageSpec(package_name="black", locked_ver="==25.1.0")),
    ("black", PackageSpec(package_name="black", locked_ver=None)),
)


@pytest.mark.parametrize(("spec_str", "truth_spec"), FROM_STR_TEST_CASES)
def test_packagespec_from_str(spec_str: str, truth_spec: PackageSpec) -> None:
    assert PackageSpec.from_string(spec_str) == truth_spec


ROUNDTRIP_CASES = ("black==25.1.0", "black")


@pytest.mark.parametrize(("spec_str"), ROUNDTRIP_CASES)
def test_spec_roundtrip(spec_str: str) -> None:
    spec = PackageSpec.from_string(spec_str)

    assert PackageSpec.from_string(spec.spec) == spec
    assert PackageSpec.from_string(str(spec)) == spec


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
    { url = "...", hash = "...", size = 30390, upload-time = "2025-06-10T12:42:38.203Z" },
]

[[package]]
name = "pip"
version = "25.2"
source = { registry = "https://pypi.org/simple" }
sdist = { url = "...", hash = "...", size = 1840021, upload-time = "2025-07-30T21:50:15.401Z" }
wheels = [
    { url = "...", hash = "...", size = 1752557, upload-time = "2025-07-30T21:50:13.323Z" },
]

[[package]]
name = "wheely-bucket"
version = "0.1.0"
source = { editable = "." }
"""


def test_parse_project(tmp_path: Path) -> None:
    lf = tmp_path / "uv.lock"
    lf.write_text(DUMMY_LOCK)

    TRUTH_PACKAGES = {
        PackageSpec(package_name="cogapp", locked_ver="==3.5.1"),
        PackageSpec(package_name="pip", locked_ver="==25.2"),
    }

    assert parse_project(base_dir=tmp_path) == TRUTH_PACKAGES


def test_parse_project_include_editable(tmp_path: Path) -> None:
    lf = tmp_path / "uv.lock"
    lf.write_text(DUMMY_LOCK)

    TRUTH_PACKAGES = {
        PackageSpec(package_name="cogapp", locked_ver="==3.5.1"),
        PackageSpec(package_name="pip", locked_ver="==25.2"),
        PackageSpec(package_name="wheely-bucket", locked_ver="==0.1.0"),
    }

    assert parse_project(base_dir=tmp_path, exclude_editable=False) == TRUTH_PACKAGES


def test_parse_project_recurse(tmp_path: Path) -> None:
    child_path = tmp_path / "my_project"
    child_path.mkdir()
    lf = child_path / "uv.lock"
    lf.write_text(DUMMY_LOCK)

    TRUTH_PACKAGES = {
        PackageSpec(package_name="cogapp", locked_ver="==3.5.1"),
        PackageSpec(package_name="pip", locked_ver="==25.2"),
    }

    assert parse_project(base_dir=tmp_path, recurse=True) == TRUTH_PACKAGES


def test_parse_project_invalid_basedir_raises() -> None:
    missing_dir = Path() / "m/i/s/s/i/n/g/"
    with pytest.raises(ValueError, match="base directory"):
        _ = parse_project(base_dir=missing_dir)
