# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### New

### Changed

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


