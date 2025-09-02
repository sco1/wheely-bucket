from __future__ import annotations

import tomllib
import typing as t
from pathlib import Path

from packaging.requirements import Requirement


class PackageSpec(t.NamedTuple):  # noqa: D101
    package_name: str
    locked_ver: str | None

    def __str__(self) -> str:
        return self.spec

    @property
    def spec(self) -> str:
        """Return a `pip`-compatible package+version specification."""
        if self.locked_ver is not None:
            return f"{self.package_name}=={self.locked_ver}"
        else:
            return self.package_name

    @classmethod
    def from_string(cls, spec_str: str) -> PackageSpec:
        """Build a `PackageSpec` instance from the profided specifier."""
        r = Requirement(spec_str)
        if r.specifier:
            return cls(package_name=r.name, locked_ver=str(r.specifier))
        else:
            return cls(package_name=r.name, locked_ver=None)

    @classmethod
    def from_lock(cls, locked_info: dict[str, t.Any]) -> PackageSpec:
        """Build a `PackageSpec` instance from a package's `uv.lock` metadata."""
        return cls(
            package_name=locked_info["name"],
            locked_ver=locked_info["version"],
        )


def parse_project(
    base_dir: Path,
    lock_filename: str = "uv.lock",
    exclude_editable: bool = True,
    recurse: bool = False,
) -> set[PackageSpec]:
    """
    Parse project lockfile(s) into a set of `PackageSpec` instances.

    If `recurse` is `False`, it is assumed that `base_dir` points to the top level of the project
    whose lockfile is to be parsed. Otherwise, lockfiles are discovered recursively and parsed into
    a single set of specs.

    `lock_filename` may be adjusted to match the desired lockfile filename. Note that matching is
    not case sensitive.

    If `exclude_editable` is `True`, editable packages are not extracted from the lockfile being
    parsed; in this context this is generally only the spec for the individual project.
    """
    if recurse:
        pattern = f"**/{lock_filename}"
    else:
        pattern = lock_filename

    lockfiles = tuple(base_dir.glob(pattern, case_sensitive=False))
    print(f"Found {len(lockfiles)} lockfile(s) to process...")

    packages = set()
    for lf in lockfiles:
        with lf.open("rb") as f:
            locked = tomllib.load(f)

        for p in locked["package"]:
            if exclude_editable and ("editable" in p["source"]):
                continue

            packages.add(PackageSpec.from_lock(p))

    return packages
