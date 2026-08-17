# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### New
- Metric translations (`graphing/translations.py`) that map all 33 pre-0.3.0 metric names onto their `oposs_zpool_`-prefixed equivalents. This recovers the graph history that the 0.3.0 rename orphaned: RRD files are never renamed on disk, so the translation aliases the old data onto the new metric name at query time and merges the two series chronologically. Sites that already upgraded to 0.3.0 get their pre-upgrade history back; no manual RRD migration is needed. This supersedes the "RRD history is not carried over" note in the 0.3.0 entry below.

### Changed

### Fixed

## 0.3.0 - 2026-08-17
### Changed
- **BREAKING**: All metric names are now prefixed with `oposs_zpool_` (e.g. `read_ops` -> `oposs_zpool_read_ops`, `free` -> `oposs_zpool_free`) to avoid collisions with built-in metrics introduced in Checkmk 3.0 (e.g. `cmk.plugins.collection.graphing.standalone:metric_read_ops`). This caused "plug-in 'read_ops' already defined" errors on Checkmk 3.0. Existing graphs and RRD history for the old metric names are not carried over.
- **BREAKING**: Graph and perfometer names are now prefixed with `oposs_zpool_` as well (e.g. `zpool_capacity` -> `oposs_zpool_capacity`). These live in the same global registry as metric names and are exposed to the same collision risk, so they are renamed in the same breaking change rather than in a later one.
- Documentation (`README.md`, checkman page) updated to the prefixed metric names, the `_s` seconds suffix on wait times, and the `oposs_zpool_rebuild*` metrics that were previously undocumented.

### Fixed
- Checkman page listed two metrics that the check never emits (`trimq_read_pend`, `trimq_read_activ`); the actual metrics are `oposs_zpool_trimq_write_pend` and `oposs_zpool_trimq_write_activ`.
- `cmk-validate-plugins` validation error: `check_default_parameters` used plain `None` for level parameters, which the `SimpleLevels` form spec in the referenced ruleset cannot transform. Defaults now use the proper SimpleLevels consumer model (`('fixed', (warn, crit))` / `('no_levels', None)`), and the check function treats `('no_levels', None)` as "no thresholds configured" instead of evaluating it as truthy fixed levels.
- Fixed compatibility with Checkmk 3.0: "plug-in '...' already defined" errors during `cmk-update-config` / upgrade caused by unprefixed metric names colliding with new built-in metrics

## 0.2.1 - 2025-09-02
### Fixed
- Fixed #3: Crash with TypeError when using default storage_levels parameter - incorrect dict format replaced with proper SimpleLevels tuple format

## 0.2.0 - 2025-08-15
### New
- Dynamic header parsing in agent plugin - automatically adapts to changes in `zpool iostat` output format
- Support for ZFS rebuild operations (rebuild_wait, rebuildq_write_pend, rebuildq_write_activ metrics)
- Much improved graph organization with 5 logical groups:
  - **Capacity**: Pool storage allocation and usage
  - **Operations**: Read/write operations per second
  - **Bandwidth**: Bidirectional read/write throughput visualization
  - **Wait Times**: Comprehensive view of all wait metrics in a single graph
  - **Task Queues**: All queue depths (sync, async, scrub, trim, rebuild) in one view

### Changed
- **BREAKING**: All wait time metrics now have `_s` suffix to indicate seconds unit (e.g., `read_wait_s`)
- Wait time metrics converted from nanoseconds to seconds internally (SI base unit)
- Agent now parses headers dynamically instead of using a hardcoded field list
- Fixed field naming: trimq_read_* corrected to trimq_write_* (matching actual zpool iostat output)
- Improved header position calculation by preserving leading whitespace
- User thresholds configured in milliseconds for convenience, internally converted to seconds

### Fixed
- Incorrect parsing of `free` field due to header alignment issues
- Missing support for rebuild-related fields in newer ZFS versions
- Proper handling of missing metrics (NaN values) in graphs

## 0.1.5 - 2025-08-11
### Fixed
- Code cleanup

## 0.1.4 - 2025-08-08
### Fixed
- Use proper v2 check_levels instead of doing it manually

## 0.1.3 - 2025-08-07
### Fixed
- Interval must be an integer

## 0.1.2 - 2025-08-07
### Fixed
- Respin with updated mkp-builder to properly include backery plugin path

## 0.1.1 - 2025-08-07
### Fixed
- Added Download URL

## 0.1.0 - 2025-08-07
### New
- Initial release


