import hashlib
import tomllib
import typing as t
from collections import abc
from dataclasses import dataclass
from pathlib import Path

from packaging.tags import Tag, cpython_tags
from packaging.utils import parse_wheel_filename
from packaging.version import Version
from pip._internal.locations import USER_CACHE_DIR

PIP_CACHE_BASE = Path(USER_CACHE_DIR)
PIP_HTTP_CACHE = PIP_CACHE_BASE / "http-v2"
PIP_USER_WHEEL_CACHE = PIP_CACHE_BASE / "wheels"

NONE_ANY_TAG = Tag("py3", "none", "any")


@dataclass(frozen=True, slots=True)
class PackageSpec:  # noqa: D101
    package_name: str
    version: Version
    wheel_name: str
    wheel_url: str
    tags: frozenset[Tag]

    @property
    def url_hash(self) -> str:
        """Calculate the SHA224 hash of the wheel URL."""
        return hashlib.sha224(self.wheel_url.encode()).hexdigest()

    @property
    def cached_wheel_path(self) -> Path:
        """
        Generate the path to where `pip` should be caching the downloaded wheel for this package.

        `pip`'s cache works by hashing the HTTP response from the wheel's download URL. The SHA224
        hash of the URL is calculated and the first `5` characters of the hash are used to build the
        path components within `pip`'s HTTP cache, whose base is located at `.../pip/cache/http-v2`.
        The HTTP response body, which should be the desired wheel file is saved to this location as
        `<hash>.body`.

        For example, if the URL hashes to `abcd1234`, the wheel should be cached to:
        `.../pip/cache/http-v2/a/b/c/d/1/abcd1234.body`

        NOTE: Path existence is not validated by this method.
        """
        hashed = self.url_hash
        path_components = list(hashed[:5])
        cache_path = PIP_HTTP_CACHE / "/".join(path_components)
        return cache_path / f"{hashed}.body"

    @classmethod
    def from_lock(cls, locked_info: dict[str, t.Any]) -> set[t.Self]:
        """
        Build `PackageSpec` instance(s) from a package's `uv.lock` metadata.

        A locked package may define zero or more wheels for the locked package version. If no wheels
        are available, an empty set is returned.
        """
        packages: set[t.Self] = set()
        wheel_spec = locked_info.get("wheels", None)
        if wheel_spec is None:
            return packages

        for spec in wheel_spec:
            wheel_url = spec["url"]
            packages.add(cls.from_url(wheel_url))

        return packages

    @classmethod
    def from_url(cls, url: str) -> t.Self:
        """Build `PackageSpec` instance(s) from the provided wheel URL."""
        *_, wheel_filename = url.split("/")
        name, ver, _, tags = parse_wheel_filename(wheel_filename)

        return cls(
            package_name=name,
            version=ver,
            wheel_name=wheel_filename,
            wheel_url=url,
            tags=tags,
        )


def is_compatible_with(
    tags: abc.Iterable[Tag],
    python_version: abc.Sequence[int] | None = None,
    platforms: abc.Iterable[str] | None = None,
) -> bool:
    """
    Check the package's tag(s) for compatibility with the given Python version and platform(s).

    The expected form of `python_version` and `platforms` matches that of
    `packaging.tags.cpython_tags`.
    """
    if NONE_ANY_TAG in tags:
        # Short-circuit on universal wheel, this tag is not yielded by cpython_tags
        return True

    for tag in cpython_tags(python_version=python_version, platforms=platforms):
        if tag in tags:
            return True

    return False


def parse_project(
    base_dir: Path,
    lock_filename: str = "uv.lock",
) -> set[PackageSpec]:
    """
    Parse project lockfile(s) into a set of `PackageSpec` instances.

    `lock_filename` may be adjusted to match the desired lockfile filename. Note that matching is
    not case sensitive.

    NOTE: Editable packages are not extracted from the lockfile being parsed; in this context this
    is generally only the spec for the individual project.
    """
    if not base_dir.is_dir():
        raise ValueError("Specified base directory either does not exist or is not a directory.")

    lockfile = base_dir / lock_filename
    if not lockfile.exists():
        raise ValueError(f"Lockfile does not exist: '{lockfile}'")

    with lockfile.open("rb") as f:
        locked = tomllib.load(f)

    packages = set()
    for p in locked["package"]:
        if "editable" in p["source"]:
            continue

        packages |= PackageSpec.from_lock(p)

    return packages
