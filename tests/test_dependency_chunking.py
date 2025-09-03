from wheely_bucket.parse_lockfile import PackageSpec
from wheely_bucket.wrap_dl import split_conflicting


def test_split_conflicting() -> None:
    PACKAGES = [
        PackageSpec.from_string("abc==0.1.0"),
        PackageSpec.from_string("abc==0.2.0"),
        PackageSpec.from_string("abc==0.3.0"),
        PackageSpec.from_string("def==0.1.0"),
    ]

    TRUTH_CHUNKED = [
        [PackageSpec.from_string("abc==0.3.0")],
        [PackageSpec.from_string("abc==0.2.0")],
        [PackageSpec.from_string("abc==0.1.0"), PackageSpec.from_string("def==0.1.0")],
    ]

    chunked = list(split_conflicting(PACKAGES))
    assert chunked == TRUTH_CHUNKED


def test_split_conflicting_no_conflict() -> None:
    PACKAGES = [
        PackageSpec.from_string("abc==0.1.0"),
        PackageSpec.from_string("def==0.1.0"),
    ]

    TRUTH_CHUNKED = [
        [
            PackageSpec.from_string("abc==0.1.0"),
            PackageSpec.from_string("def==0.1.0"),
        ]
    ]

    chunked = list(split_conflicting(PACKAGES))
    assert chunked == TRUTH_CHUNKED
