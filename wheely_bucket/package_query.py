import platform
import re

import httpx
from packaging.requirements import Requirement
from packaging.specifiers import SpecifierSet
from packaging.version import Version

from wheely_bucket import __url__, __version__
from wheely_bucket.parse_lockfile import PackageSpec

PYPI_SIMPLE_API = "https://pypi.org/simple/"
ACCEPT_JSON = "application/vnd.pypi.simple.v1+json"
USER_AGENT = (
    f"wheely-bucket/{__version__} ({__url__}) "
    f"httpx/{httpx.__version__} "
    f"{platform.python_implementation()}/{platform.python_version()}"
)
HEADER = {
    "User-Agent": USER_AGENT,
    "Accept": ACCEPT_JSON,
}


def _normalize(package_name: str) -> str:
    """
    Normalize the package name per PyPA's package normalization specification.

    See: https://packaging.python.org/en/latest/specifications/name-normalization/#name-normalization
    See: https://packaging.python.org/en/latest/specifications/simple-repository-api/#normalized-names
    """
    return re.sub(r"[-_.]+", "-", package_name).lower()


def query_pypi_simple(package_name: str) -> tuple[list[PackageSpec], list[Version]]:
    """
    Query the PyPI Simple Repository API for wheels & releases available for the specified package.

    Specs should be reterned in reverse chronological order.

    NOTE: Yanked wheels are not included in the final output, though may still be included in the
    version list.
    """
    r = httpx.get(
        f"{PYPI_SIMPLE_API}{_normalize(package_name)}/",
        headers=HEADER,
        follow_redirects=True,
    )
    r.raise_for_status()

    package_info = r.json()
    packages = []
    for f in reversed(package_info["files"]):
        if f.get("yanked", False):
            continue

        url: str = f["url"]
        if not url.endswith(".whl"):
            continue

        packages.append(PackageSpec.from_url(f["url"]))

    releases = [Version(v) for v in reversed(package_info["versions"])]

    return packages, releases


def filtered_pypi_query(req: Requirement) -> set[PackageSpec]:
    """
    Query the PyPI Simple Repository API for wheels that satisfy the provided requirement.

    NOTE: Yanked wheels are not included in the final output.
    """
    available_packages, available_versions = query_pypi_simple(req.name)
    filtered_packages: set[PackageSpec] = set()

    # For an unspecified requirement, set the specifier to the latest version
    # Not sure if this might run into issues with yanked releases, I think those might still show up
    # in the version list
    if not req.specifier:
        filter_spec = SpecifierSet(f"=={available_versions[0]}")
    else:
        filter_spec = req.specifier

    # Resolve the latest compatible version & add all matching wheels
    filtered_versions = list(filter_spec.filter(available_versions))
    if not filtered_versions:
        return filtered_packages

    latest_ver = filtered_versions[0]
    for p in available_packages:
        if p.version == latest_ver:
            filtered_packages.add(p)

    return filtered_packages
