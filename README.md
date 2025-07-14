# CheckMK OPOSS zpool iostat Plugin

A comprehensive CheckMK plugin for monitoring ZFS storage pool I/O performance using `zpool iostat`.

## Overview

This plugin provides detailed monitoring of ZFS storage pool I/O statistics including:

- **I/O Operations**: Read/write operations per second
- **Throughput**: Read/write data throughput in bytes/second
- **Latency**: I/O wait times at various levels (pool, disk, queue)
- **Storage Utilization**: Pool capacity usage monitoring
- **Queue Statistics**: Detailed queue depths and wait times for sync/async operations
- **Maintenance Operations**: Scrub and trim operation monitoring

## Features

- **Comprehensive Metrics**: Collects all available metrics from `zpool iostat -Hylpq`
- **Granular Thresholds**: Individual configurable thresholds for each metric type
- **Agent Bakery Support**: Automated deployment and configuration
- **Error Handling**: Robust error handling with detailed error reporting
- **Performance Optimized**: Efficient data collection with configurable sampling intervals

## Installation

1. Copy the plugin files to your CheckMK installation:
   ```bash
   cp -r local/* ~SITE/local   
   ```

2. Reload CheckMK configuration:
   ```bash
   omd reload apache
   ```

3. Deploy the agent plugin to target hosts via Agent Bakery or manually.

## Configuration

### Agent Configuration

Create `/etc/check_mk/oposs_zpool_iostat.json` on monitored hosts:

```json
{
  "enabled": true,
  "timeout": 30,
  "sampling_duration": 10
}
```

**Parameters:**
- `enabled`: Enable/disable monitoring (default: true)
- `timeout`: Command timeout in seconds (default: 30)
- `sampling_duration`: How long iostat collects data before reporting (default: 10)

### Check Parameters

Configure monitoring thresholds in CheckMK under "Host & Service Parameters" > "Applications, Processes & Services" > "OPOSS zpool iostat monitoring":

#### Basic Monitoring
- **Storage Levels**: Pool capacity utilization thresholds
- **I/O Operations**: Read/write operations per second thresholds
- **Basic Latency**: Read/write wait time thresholds
- **Throughput**: Read/write data throughput thresholds

#### Advanced Monitoring
- **Disk Wait Times**: Disk-level I/O latency thresholds
- **Queue Wait Times**: Individual queue wait time thresholds for:
  - Synchronous read/write queues
  - Asynchronous read/write queues
  - Scrub and trim operations
- **Queue Depths**: Individual queue depth thresholds for:
  - Pending and active operations
  - Sync/async queues
  - Scrub and trim queues

## Metrics

### Basic Metrics
- `read_ops`, `write_ops` - Operations per second
- `read_throughput`, `write_throughput` - Bytes per second
- `read_wait`, `write_wait` - I/O wait times in milliseconds
- `storage_used_percent` - Pool utilization percentage
- `allocated`, `free` - Pool space allocation

### Advanced Metrics
- `disk_read_wait`, `disk_write_wait` - Disk-level wait times
- `syncq_*_wait`, `asyncq_*_wait` - Queue-specific wait times
- `scrub_wait`, `trim_wait` - Maintenance operation wait times
- `*_pend`, `*_activ` - Queue depths (pending/active operations)

## Requirements

- ZFS filesystem with `zpool` command available
- At least one ZFS pool configured and accessible
- Python 3.6 or later
- CheckMK 2.3 or later

## Compatibility

- **Linux**: All modern distributions with ZFS support
- **FreeBSD**: Native ZFS support
- **Solaris/OpenSolaris**: Native ZFS support

## Troubleshooting

### Common Issues

1. **No services discovered**:
   - Ensure ZFS is installed and pools are accessible
   - Check that the agent plugin is executable
   - Verify `/sbin/zpool` exists and is accessible

2. **Timeout errors**:
   - Increase timeout value in configuration
   - Check pool health (`zpool status`)
   - Verify adequate system resources

3. **Permission errors**:
   - Ensure agent runs with sufficient privileges
   - Check that `/dev/zfs` is accessible

### Debug Information

Enable debug logging by running the agent plugin manually:
```bash
/usr/lib/check_mk_agent/plugins/oposs_zpool_iostat
```

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Support

For issues and feature requests, please create an issue in the project repository.