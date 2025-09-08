import json
import typing as t
from pathlib import Path

import pytest
from packaging.requirements import Requirement
from packaging.version import Version
from pytest_mock import MockerFixture

from wheely_bucket.package_query import _normalize, filtered_pypi_query, query_pypi_simple
from wheely_bucket.parse_lockfile import PackageSpec

TEST_DATA_DIR = Path(__file__).parent / "test_data"

NORMALIZE_TEST_CASES = (
    ("friendly-bard", "friendly-bard"),
    ("Friendly-Bard", "friendly-bard"),
    ("FRIENDLY-BARD", "friendly-bard"),
    ("friendly.bard", "friendly-bard"),
    ("friendly_bard", "friendly-bard"),
    ("friendly--bard", "friendly-bard"),
    ("FrIeNdLy-._.-bArD", "friendly-bard"),
)


@pytest.mark.parametrize(("package_name", "truth_normalized"), NORMALIZE_TEST_CASES)
def test_normalize(package_name: str, truth_normalized: str) -> None:
    assert _normalize(package_name) == truth_normalized


class DummyResponse:
    def __init__(self, json_resp: dict[str, t.Any]) -> None:
        self._json = json_resp

    def raise_for_status(self) -> None: ...

    def json(self) -> dict[str, t.Any]:
        return self._json


# fmt: off
ANN_311 = PackageSpec.from_url("https://files.pythonhosted.org/packages/bf/ce/55b1908ccfd729b896a57111c40772d81c506d3710dcc15ed827c9dec661/flake8_annotations-3.1.1-py3-none-any.whl")
ANN_291 = PackageSpec.from_url("https://files.pythonhosted.org/packages/f6/dc/ee0cfd300f22f169d42fd951c4a44840041f777987de8c56f861be5faefd/flake8_annotations-2.9.1-py3-none-any.whl")
ANN_100 = PackageSpec.from_url("https://files.pythonhosted.org/packages/cd/a4/af2d10e21c41bd84cb195d383cd2242a0ac73754fa2bc3e3ca20c0593723/flake8_annotations-1.0.0-py3-none-any.whl")
# fmt: on


SAMPLE_RESPONSE = TEST_DATA_DIR / "simple_return.json"
with SAMPLE_RESPONSE.open("r") as f:
    SAMPLE_RESPONSE_JSON = json.load(f)


def test_query_pypi_simple(mocker: MockerFixture) -> None:
    mocker.patch(
        "wheely_bucket.package_query.httpx.get", return_value=DummyResponse(SAMPLE_RESPONSE_JSON)
    )

    TRUTH_PACKAGES = [ANN_311, ANN_291, ANN_100]
    TRUTH_VERSIONS = [
        Version("3.1.1"),
        Version("2.9.1"),
        Version("1.0.0"),
    ]

    packages, versions = query_pypi_simple("flake8-annotations")
    assert packages == TRUTH_PACKAGES
    assert versions == TRUTH_VERSIONS


def test_query_pypi_simple_ignore_yanked(mocker: MockerFixture) -> None:
    DUMMY_JSON = {
        "files": [
            {
                "url": "https://a.b.c/flake8_annotations-1.0.0-py3-none-any.whl",
                "yanked": "this was yanked",
            }
        ],
        "versions": [],
    }
    mocker.patch("wheely_bucket.package_query.httpx.get", return_value=DummyResponse(DUMMY_JSON))

    packages, _ = query_pypi_simple("flake8-annotations")
    assert not packages


FILTER_QUERY_CASES = (  # type: ignore[var-annotated]
    (Requirement("flake8-annotations"), {ANN_311}),
    (Requirement("flake8-annotations<3"), {ANN_291}),
    (Requirement("flake8-annotations>=42"), set()),
)


@pytest.mark.parametrize(("requirement", "truth_out"), FILTER_QUERY_CASES)
def test_filtered_pypi_query(
    requirement: Requirement, truth_out: set[PackageSpec], mocker: MockerFixture
) -> None:
    mocker.patch(
        "wheely_bucket.package_query.httpx.get", return_value=DummyResponse(SAMPLE_RESPONSE_JSON)
    )

    assert filtered_pypi_query(requirement) == truth_out
