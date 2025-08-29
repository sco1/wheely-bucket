from __future__ import annotations

import tomllib
import typing as t
from pathlib import Path

from packaging import tags


class WheelSpec(t.NamedTuple):  # noqa: D101
    package_name: str
    wheel_name: str
    url: str
    platforms: frozenset[str]

    @classmethod
    def from_url(cls, url: str) -> WheelSpec:
        """
        Build a `WheelSpec` instance from the provided wheel download URL.

        URLs are assumed to be of the form `"https://<CDN component>/<wheel name>"`, e.g.
        `"https://<CDN component>/flake8_annotations-3.1.1-py3-none-any.whl"`

        Platform tags are parsed using the `packaging` library & stored to assist with downstream
        filtering.
        """
        *_, wname = url.split("/")
        pname, _, raw_tag = wname.split("-", maxsplit=2)
        parsed_tag = tags.parse_tag(raw_tag.removesuffix(".whl"))

        return cls(
            package_name=pname,
            wheel_name=wname,
            url=url,
            platforms=frozenset(p.platform for p in parsed_tag),
        )


def parse_lockfile(lockfile: Path, platform_filter: set[str] | None = None) -> set[WheelSpec]:
    """
    Parse `uv`'s TOML lockfile and attempt to extract wheel information for all resolved packages.

    By default, only cross-platform wheels are extracted from the lockfile. `platform_filter` may be
    specified, as a set of platform tag strings, to include wheels for additional platforms if
    available.

    NOTE: Packages that only provide source distributions are not currently considered.
    """
    with lockfile.open("rb") as f:
        lf = tomllib.load(f)

    keep_wheels = set()
    for p in lf["package"]:
        # TODO: Probably need to provide sdist-only as well
        for w in p.get("wheels", []):
            spec = WheelSpec.from_url(w["url"])
            if "any" in spec.platforms:
                keep_wheels.add(spec)

            if platform_filter is not None:
                if spec.platforms & platform_filter:
                    keep_wheels.add(spec)

    return keep_wheels
