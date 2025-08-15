#!/usr/bin/env python3
"""
CheckMK Graphing configuration for OPOSS zpool iostat monitoring
Defines metrics, graphs, and perfometers using CheckMK 2.3 v1 graphing API
"""

from cmk.graphing.v1 import Title
from cmk.graphing.v1.metrics import (
    Color,
    DecimalNotation,
    IECNotation,
    Metric,
    TimeNotation,
    Unit,
)
from cmk.graphing.v1.graphs import (
    Graph,
    MinimalRange,
    Bidirectional,
)
from cmk.graphing.v1.perfometers import (
    Perfometer,
    FocusRange,
    Closed,
    Stacked,
)

# Define units
unit_ops_per_sec = Unit(DecimalNotation("/s"))
unit_bytes_per_sec = Unit(IECNotation("B/s"))
unit_bytes = Unit(IECNotation("B"))
unit_seconds = Unit(TimeNotation())  # Use TimeNotation for proper SI scaling (s, ms, μs, etc.)
unit_count = Unit(DecimalNotation(""))
unit_percent = Unit(DecimalNotation("%"))

# Storage capacity metrics
metric_allocated = Metric(
    name="allocated",
    title=Title("Allocated space"),
    unit=unit_bytes,
    color=Color.BLUE,
)

metric_free = Metric(
    name="free",
    title=Title("Free space"),
    unit=unit_bytes,
    color=Color.GREEN,
)

metric_storage_used_percent = Metric(
    name="storage_used_percent",
    title=Title("Storage utilization"),
    unit=unit_percent,
    color=Color.ORANGE,
)

# I/O Operations metrics
metric_read_ops = Metric(
    name="read_ops",
    title=Title("Read operations"),
    unit=unit_ops_per_sec,
    color=Color.CYAN,
)

metric_write_ops = Metric(
    name="write_ops",
    title=Title("Write operations"),
    unit=unit_ops_per_sec,
    color=Color.PURPLE,
)

# Throughput metrics
metric_read_throughput = Metric(
    name="read_throughput",
    title=Title("Read throughput"),
    unit=unit_bytes_per_sec,
    color=Color.LIGHT_BLUE,
)

metric_write_throughput = Metric(
    name="write_throughput",
    title=Title("Write throughput"),
    unit=unit_bytes_per_sec,
    color=Color.LIGHT_PURPLE,
)

# Wait time metrics - now in seconds with _s suffix
metric_read_wait_s = Metric(
    name="read_wait_s",
    title=Title("Read wait time"),
    unit=unit_seconds,
    color=Color.BLUE,
)

metric_write_wait_s = Metric(
    name="write_wait_s",
    title=Title("Write wait time"),
    unit=unit_seconds,
    color=Color.RED,
)

metric_disk_read_wait_s = Metric(
    name="disk_read_wait_s",
    title=Title("Disk read wait time"),
    unit=unit_seconds,
    color=Color.CYAN,
)

metric_disk_write_wait_s = Metric(
    name="disk_write_wait_s",
    title=Title("Disk write wait time"),
    unit=unit_seconds,
    color=Color.ORANGE,
)

metric_disk_wait_max_s = Metric(
    name="disk_wait_max_s",
    title=Title("Max disk wait time"),
    unit=unit_seconds,
    color=Color.DARK_RED,
)

# Queue wait time metrics - now in seconds with _s suffix
metric_syncq_read_wait_s = Metric(
    name="syncq_read_wait_s",
    title=Title("Sync queue read wait time"),
    unit=unit_seconds,
    color=Color.GREEN,
)

metric_syncq_write_wait_s = Metric(
    name="syncq_write_wait_s",
    title=Title("Sync queue write wait time"),
    unit=unit_seconds,
    color=Color.YELLOW,
)

metric_asyncq_read_wait_s = Metric(
    name="asyncq_read_wait_s",
    title=Title("Async queue read wait time"),
    unit=unit_seconds,
    color=Color.PURPLE,
)

metric_asyncq_write_wait_s = Metric(
    name="asyncq_write_wait_s",
    title=Title("Async queue write wait time"),
    unit=unit_seconds,
    color=Color.PINK,
)

# Special operation wait times - now in seconds with _s suffix
metric_scrub_wait_s = Metric(
    name="scrub_wait_s",
    title=Title("Scrub wait time"),
    unit=unit_seconds,
    color=Color.BROWN,
)

metric_trim_wait_s = Metric(
    name="trim_wait_s",
    title=Title("Trim wait time"),
    unit=unit_seconds,
    color=Color.GRAY,
)

metric_rebuild_wait_s = Metric(
    name="rebuild_wait_s",
    title=Title("Rebuild wait time"),
    unit=unit_seconds,
    color=Color.PINK,
)

# Queue depth metrics (pending operations)
metric_syncq_read_pend = Metric(
    name="syncq_read_pend",
    title=Title("Sync queue read pending"),
    unit=unit_count,
    color=Color.LIGHT_GRAY,
)

metric_syncq_read_activ = Metric(
    name="syncq_read_activ",
    title=Title("Sync queue read active"),
    unit=unit_count,
    color=Color.GRAY,
)

metric_syncq_write_pend = Metric(
    name="syncq_write_pend",
    title=Title("Sync queue write pending"),
    unit=unit_count,
    color=Color.LIGHT_BROWN,
)

metric_syncq_write_activ = Metric(
    name="syncq_write_activ",
    title=Title("Sync queue write active"),
    unit=unit_count,
    color=Color.BROWN,
)

metric_asyncq_read_pend = Metric(
    name="asyncq_read_pend",
    title=Title("Async queue read pending"),
    unit=unit_count,
    color=Color.LIGHT_CYAN,
)

metric_asyncq_read_activ = Metric(
    name="asyncq_read_activ",
    title=Title("Async queue read active"),
    unit=unit_count,
    color=Color.DARK_CYAN,
)

metric_asyncq_write_pend = Metric(
    name="asyncq_write_pend",
    title=Title("Async queue write pending"),
    unit=unit_count,
    color=Color.LIGHT_PINK,
)

metric_asyncq_write_activ = Metric(
    name="asyncq_write_activ",
    title=Title("Async queue write active"),
    unit=unit_count,
    color=Color.PINK,
)

# Special operation queue metrics
metric_scrubq_read_pend = Metric(
    name="scrubq_read_pend",
    title=Title("Scrub queue read pending"),
    unit=unit_count,
    color=Color.LIGHT_PURPLE,
)

metric_scrubq_read_activ = Metric(
    name="scrubq_read_activ",
    title=Title("Scrub queue read active"),
    unit=unit_count,
    color=Color.PURPLE,
)

metric_trimq_write_pend = Metric(
    name="trimq_write_pend",
    title=Title("Trim queue write pending"),
    unit=unit_count,
    color=Color.LIGHT_BLUE,
)

metric_trimq_write_activ = Metric(
    name="trimq_write_activ",
    title=Title("Trim queue write active"),
    unit=unit_count,
    color=Color.DARK_BLUE,
)

metric_rebuildq_write_pend = Metric(
    name="rebuildq_write_pend",
    title=Title("Rebuild queue write pending"),
    unit=unit_count,
    color=Color.LIGHT_PURPLE,
)

metric_rebuildq_write_activ = Metric(
    name="rebuildq_write_activ",
    title=Title("Rebuild queue write active"),
    unit=unit_count,
    color=Color.PURPLE,
)

# Define graphs - organized into 5 logical groups

# 1. Capacity - Storage allocation and usage
graph_zpool_capacity = Graph(
    name="zpool_capacity",
    title=Title("ZFS Pool Capacity"),
    simple_lines=[
        "allocated",
        "free",
    ],
    minimal_range=MinimalRange(
        lower=0,
        upper=1000000000000,  # 1TB default upper limit
    ),
)

# 2. Operations - Read/write operations per second
graph_zpool_operations = Graph(
    name="zpool_operations",
    title=Title("ZFS Pool Operations"),
    simple_lines=[
        "read_ops",
        "write_ops",
    ],
    minimal_range=MinimalRange(
        lower=0,
        upper=1000,
    ),
)

# 3. Bandwidth - Read/write throughput
graph_zpool_bandwidth = Bidirectional(
    name="zpool_bandwidth",
    title=Title("ZFS Pool Bandwidth"),
    lower=Graph(
        name="zpool_bandwidth_read",
        title=Title("Read Bandwidth"),
        simple_lines=["read_throughput"],
    ),
    upper=Graph(
        name="zpool_bandwidth_write", 
        title=Title("Write Bandwidth"),
        simple_lines=["write_throughput"],
    ),
)

# 4. Wait Times - Combined graph for all working wait time metrics

graph_zpool_wait_times = Graph(
    name="zpool_wait_times",
    title=Title("ZFS Pool Wait Times"),
    simple_lines=[
        # Total wait times
        "read_wait_s",
        "write_wait_s",
        # Disk wait times
        "disk_read_wait_s",
        "disk_write_wait_s",
        # Sync queue wait times
        "syncq_read_wait_s",
        "syncq_write_wait_s",
        # Async queue wait times
        "asyncq_read_wait_s",
        "asyncq_write_wait_s",
        # Special operation wait times
        "scrub_wait_s",
        "trim_wait_s",
        "rebuild_wait_s",
    ],
    optional=[
        # All metrics are optional - graph displays even if some are missing
        "read_wait_s",
        "write_wait_s",
        "disk_read_wait_s",
        "disk_write_wait_s",
        "syncq_read_wait_s",
        "syncq_write_wait_s",
        "asyncq_read_wait_s",
        "asyncq_write_wait_s",
        "scrub_wait_s",
        "trim_wait_s",
        "rebuild_wait_s",
    ],
    minimal_range=MinimalRange(
        lower=0,
        upper=0.001,  # 1ms upper limit - typical for fast storage
    ),
)

# 5. Task Queues - Combined graph for sync and async queues

graph_zpool_queue_depths = Graph(
    name="zpool_queue_depths",
    title=Title("ZFS Pool Queue Depths"),
    simple_lines=[
        # Sync queue depths
        "syncq_read_pend",
        "syncq_read_activ",
        "syncq_write_pend",
        "syncq_write_activ",
        # Async queue depths
        "asyncq_read_pend",
        "asyncq_read_activ",
        "asyncq_write_pend",
        "asyncq_write_activ",
        # Scrub queue depths  
        "scrubq_read_pend",
        "scrubq_read_activ",
        # Trim queue depths (will be NaN until agent is updated)
        "trimq_write_pend",
        "trimq_write_activ",
        # Rebuild queue depths (will be NaN until agent is updated)
        "rebuildq_write_pend",
        "rebuildq_write_activ",
    ],
    optional=[
        # All metrics are optional - graph displays even if some are missing
        "syncq_read_pend",
        "syncq_read_activ",
        "syncq_write_pend",
        "syncq_write_activ",
        "asyncq_read_pend",
        "asyncq_read_activ",
        "asyncq_write_pend",
        "asyncq_write_activ",
        "scrubq_read_pend",
        "scrubq_read_activ",
        "trimq_write_pend",
        "trimq_write_activ",
        "rebuildq_write_pend",
        "rebuildq_write_activ",
    ],
    minimal_range=MinimalRange(
        lower=0,
        upper=100,  # 100 operations upper limit
    ),
)

# Define perfometers
perfometer_zpool_operations = Perfometer(
    name="zpool_operations",
    focus_range=FocusRange(
        lower=Closed(0),
        upper=Closed(1000),
    ),
    segments=[
        "read_ops",
        "write_ops",
    ],
)

perfometer_zpool_storage = Perfometer(
    name="zpool_storage",
    focus_range=FocusRange(
        lower=Closed(0),
        upper=Closed(1000000000000),  # 1TB
    ),
    segments=[
        "allocated",
        "free",
    ],
)

perfometer_zpool_wait_times = Perfometer(
    name="zpool_wait_times",
    focus_range=FocusRange(
        lower=Closed(0),
        upper=Closed(0.1),  # 100ms in seconds
    ),
    segments=[
        "read_wait_s",
        "write_wait_s",
    ],
)

# Stacked perfometer for comprehensive view
perfometer_zpool_comprehensive = Stacked(
    name="zpool_comprehensive",
    lower=Perfometer(
        name="zpool_ops_lower",
        focus_range=FocusRange(
            lower=Closed(0),
            upper=Closed(1000),
        ),
        segments=["read_ops", "write_ops"],
    ),
    upper=Perfometer(
        name="zpool_storage_upper",
        focus_range=FocusRange(
            lower=Closed(0),
            upper=Closed(1000000000000),  # 1TB
        ),
        segments=["allocated", "free"],
    ),
)