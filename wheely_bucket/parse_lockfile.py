from __future__ import annotations

import tomllib
import typing as t
from pathlib import Path


class PackageSpec(t.NamedTuple):  # noqa: D101
    package_name: str
    locked_ver: str

    def __str__(self) -> str:
        return self.spec

    @property
    def spec(self) -> str:
        """Return a `pip`-compatible package+version specification."""
        return f"{self.package_name}=={self.locked_ver}"

    @classmethod
    def from_string(cls, spec_str: str) -> PackageSpec:
        raise NotImplementedError

    @classmethod
    def from_lock(cls, locked_info: dict[str, t.Any]) -> PackageSpec:
        """Build a `PackageSpec` instance from a package's `uv.lock` metadata."""
        return cls(
            package_name=locked_info["name"],
            locked_ver=locked_info["version"],
        )

    @classmethod
    def from_lockfile(cls, lockfile: Path, exclude_editable: bool = True) -> set[PackageSpec]:
        """
        Parse all resolved package metadata from `uv.lock` into a set of `PackageSpec` instances.

        If `exclude_editable` is `True`, editable package installations (e.g. the project being
        worked on) are ignored when building the final output.
        """
        with lockfile.open("rb") as f:
            lf = tomllib.load(f)

        packages = set()
        for p in lf["package"]:
            if exclude_editable and ("editable" in p["source"]):
                continue

            packages.add(cls.from_lock(p))

        return packages
