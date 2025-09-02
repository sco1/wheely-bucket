import pytest

from wheely_bucket.parse_lockfile import PackageSpec


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
