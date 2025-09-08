# Changelog

Versions follow [Semantic Versioning](https://semver.org/spec/v2.0.0.html) (`<major>`.`<minor>`.`<patch>`)

## `[v0.3.0]`

### Changed
* (Internal) #4 Refactor away from `pip download` in favor of internal downloading; an attempt is still made to utilize `pip`'s HTTP cache prior to queuing a download

## `[v0.2.1]`

### Changed
* #2, #3 When using `wheely_bucket project --recurse`, `pip download` is called per-project rather than attempting to mitigate resolver issues

## `[v0.2.0]`

### Changed
* #1 `python-version` and `platform` are now specified as comma-delimited rather than space-delimited

### Fixed
* #2 When using `wheely_bucket project --recurse`, conflicting dependencies are split into separate `pip download` calls to avoid issues with `pip`'s dependency resolution

## `[v0.1.0]`

Initial release 🎉
