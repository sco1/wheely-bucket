# Changelog

Versions follow [Semantic Versioning](https://semver.org/spec/v2.0.0.html) (`<major>`.`<minor>`.`<patch>`)

## `[v0.2.0]`

### Changed
* #1 `python-version` and `platform` are now specified as comma-delimited rather than space-delimited

### Fixed
* #2 When using `wheely_bucket project --recurse`, conflicting dependencies are split into separate `pip download` calls to avoid issues with `pip`'s dependency resolution

## `[v0.1.0]`

Initial release 🎉
