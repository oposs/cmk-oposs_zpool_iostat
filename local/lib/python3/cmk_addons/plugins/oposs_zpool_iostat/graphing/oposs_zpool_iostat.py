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
    name="oposs_zpool_allocated",
    title=Title("Allocated space"),
    unit=unit_bytes,
    color=Color.BLUE,
)

metric_free = Metric(
    name="oposs_zpool_free",
    title=Title("Free space"),
    unit=unit_bytes,
    color=Color.GREEN,
)

metric_storage_used_percent = Metric(
    name="oposs_zpool_storage_used_percent",
    title=Title("Storage utilization"),
    unit=unit_percent,
    color=Color.ORANGE,
)

# I/O Operations metrics
metric_read_ops = Metric(
    name="oposs_zpool_read_ops",
    title=Title("Read operations"),
    unit=unit_ops_per_sec,
    color=Color.CYAN,
)

metric_write_ops = Metric(
    name="oposs_zpool_write_ops",
    title=Title("Write operations"),
    unit=unit_ops_per_sec,
    color=Color.PURPLE,
)

# Throughput metrics
metric_read_throughput = Metric(
    name="oposs_zpool_read_throughput",
    title=Title("Read throughput"),
    unit=unit_bytes_per_sec,
    color=Color.LIGHT_BLUE,
)

metric_write_throughput = Metric(
    name="oposs_zpool_write_throughput",
    title=Title("Write throughput"),
    unit=unit_bytes_per_sec,
    color=Color.LIGHT_PURPLE,
)

# Wait time metrics - now in seconds with _s suffix
metric_read_wait_s = Metric(
    name="oposs_zpool_read_wait_s",
    title=Title("Read wait time"),
    unit=unit_seconds,
    color=Color.BLUE,
)

metric_write_wait_s = Metric(
    name="oposs_zpool_write_wait_s",
    title=Title("Write wait time"),
    unit=unit_seconds,
    color=Color.RED,
)

metric_disk_read_wait_s = Metric(
    name="oposs_zpool_disk_read_wait_s",
    title=Title("Disk read wait time"),
    unit=unit_seconds,
    color=Color.CYAN,
)

metric_disk_write_wait_s = Metric(
    name="oposs_zpool_disk_write_wait_s",
    title=Title("Disk write wait time"),
    unit=unit_seconds,
    color=Color.ORANGE,
)

metric_disk_wait_max_s = Metric(
    name="oposs_zpool_disk_wait_max_s",
    title=Title("Max disk wait time"),
    unit=unit_seconds,
    color=Color.DARK_RED,
)

# Queue wait time metrics - now in seconds with _s suffix
metric_syncq_read_wait_s = Metric(
    name="oposs_zpool_syncq_read_wait_s",
    title=Title("Sync queue read wait time"),
    unit=unit_seconds,
    color=Color.GREEN,
)

metric_syncq_write_wait_s = Metric(
    name="oposs_zpool_syncq_write_wait_s",
    title=Title("Sync queue write wait time"),
    unit=unit_seconds,
    color=Color.YELLOW,
)

metric_asyncq_read_wait_s = Metric(
    name="oposs_zpool_asyncq_read_wait_s",
    title=Title("Async queue read wait time"),
    unit=unit_seconds,
    color=Color.PURPLE,
)

metric_asyncq_write_wait_s = Metric(
    name="oposs_zpool_asyncq_write_wait_s",
    title=Title("Async queue write wait time"),
    unit=unit_seconds,
    color=Color.PINK,
)

# Special operation wait times - now in seconds with _s suffix
metric_scrub_wait_s = Metric(
    name="oposs_zpool_scrub_wait_s",
    title=Title("Scrub wait time"),
    unit=unit_seconds,
    color=Color.BROWN,
)

metric_trim_wait_s = Metric(
    name="oposs_zpool_trim_wait_s",
    title=Title("Trim wait time"),
    unit=unit_seconds,
    color=Color.GRAY,
)

metric_rebuild_wait_s = Metric(
    name="oposs_zpool_rebuild_wait_s",
    title=Title("Rebuild wait time"),
    unit=unit_seconds,
    color=Color.PINK,
)

# Queue depth metrics (pending operations)
metric_syncq_read_pend = Metric(
    name="oposs_zpool_syncq_read_pend",
    title=Title("Sync queue read pending"),
    unit=unit_count,
    color=Color.LIGHT_GRAY,
)

metric_syncq_read_activ = Metric(
    name="oposs_zpool_syncq_read_activ",
    title=Title("Sync queue read active"),
    unit=unit_count,
    color=Color.GRAY,
)

metric_syncq_write_pend = Metric(
    name="oposs_zpool_syncq_write_pend",
    title=Title("Sync queue write pending"),
    unit=unit_count,
    color=Color.LIGHT_BROWN,
)

metric_syncq_write_activ = Metric(
    name="oposs_zpool_syncq_write_activ",
    title=Title("Sync queue write active"),
    unit=unit_count,
    color=Color.BROWN,
)

metric_asyncq_read_pend = Metric(
    name="oposs_zpool_asyncq_read_pend",
    title=Title("Async queue read pending"),
    unit=unit_count,
    color=Color.LIGHT_CYAN,
)

metric_asyncq_read_activ = Metric(
    name="oposs_zpool_asyncq_read_activ",
    title=Title("Async queue read active"),
    unit=unit_count,
    color=Color.DARK_CYAN,
)

metric_asyncq_write_pend = Metric(
    name="oposs_zpool_asyncq_write_pend",
    title=Title("Async queue write pending"),
    unit=unit_count,
    color=Color.LIGHT_PINK,
)

metric_asyncq_write_activ = Metric(
    name="oposs_zpool_asyncq_write_activ",
    title=Title("Async queue write active"),
    unit=unit_count,
    color=Color.PINK,
)

# Special operation queue metrics
metric_scrubq_read_pend = Metric(
    name="oposs_zpool_scrubq_read_pend",
    title=Title("Scrub queue read pending"),
    unit=unit_count,
    color=Color.LIGHT_PURPLE,
)

metric_scrubq_read_activ = Metric(
    name="oposs_zpool_scrubq_read_activ",
    title=Title("Scrub queue read active"),
    unit=unit_count,
    color=Color.PURPLE,
)

metric_trimq_write_pend = Metric(
    name="oposs_zpool_trimq_write_pend",
    title=Title("Trim queue write pending"),
    unit=unit_count,
    color=Color.LIGHT_BLUE,
)

metric_trimq_write_activ = Metric(
    name="oposs_zpool_trimq_write_activ",
    title=Title("Trim queue write active"),
    unit=unit_count,
    color=Color.DARK_BLUE,
)

metric_rebuildq_write_pend = Metric(
    name="oposs_zpool_rebuildq_write_pend",
    title=Title("Rebuild queue write pending"),
    unit=unit_count,
    color=Color.LIGHT_PURPLE,
)

metric_rebuildq_write_activ = Metric(
    name="oposs_zpool_rebuildq_write_activ",
    title=Title("Rebuild queue write active"),
    unit=unit_count,
    color=Color.PURPLE,
)

# Define graphs - organized into 5 logical groups

# 1. Capacity - Storage allocation and usage
graph_zpool_capacity = Graph(
    name="oposs_zpool_capacity",
    title=Title("ZFS Pool Capacity"),
    simple_lines=[
        "oposs_zpool_allocated",
        "oposs_zpool_free",
    ],
    minimal_range=MinimalRange(
        lower=0,
        upper=1000000000000,  # 1TB default upper limit
    ),
)

# 2. Operations - Read/write operations per second
graph_zpool_operations = Graph(
    name="oposs_zpool_operations",
    title=Title("ZFS Pool Operations"),
    simple_lines=[
        "oposs_zpool_read_ops",
        "oposs_zpool_write_ops",
    ],
    minimal_range=MinimalRange(
        lower=0,
        upper=1000,
    ),
)

# 3. Bandwidth - Read/write throughput
graph_zpool_bandwidth = Bidirectional(
    name="oposs_zpool_bandwidth",
    title=Title("ZFS Pool Bandwidth"),
    lower=Graph(
        name="oposs_zpool_bandwidth_read",
        title=Title("Read Bandwidth"),
        simple_lines=["oposs_zpool_read_throughput"],
    ),
    upper=Graph(
        name="oposs_zpool_bandwidth_write", 
        title=Title("Write Bandwidth"),
        simple_lines=["oposs_zpool_write_throughput"],
    ),
)

# 4. Wait Times - Combined graph for all working wait time metrics

graph_zpool_wait_times = Graph(
    name="oposs_zpool_wait_times",
    title=Title("ZFS Pool Wait Times"),
    simple_lines=[
        # Total wait times
        "oposs_zpool_read_wait_s",
        "oposs_zpool_write_wait_s",
        # Disk wait times
        "oposs_zpool_disk_read_wait_s",
        "oposs_zpool_disk_write_wait_s",
        # Sync queue wait times
        "oposs_zpool_syncq_read_wait_s",
        "oposs_zpool_syncq_write_wait_s",
        # Async queue wait times
        "oposs_zpool_asyncq_read_wait_s",
        "oposs_zpool_asyncq_write_wait_s",
        # Special operation wait times
        "oposs_zpool_scrub_wait_s",
        "oposs_zpool_trim_wait_s",
        "oposs_zpool_rebuild_wait_s",
    ],
    optional=[
        # All metrics are optional - graph displays even if some are missing
        "oposs_zpool_read_wait_s",
        "oposs_zpool_write_wait_s",
        "oposs_zpool_disk_read_wait_s",
        "oposs_zpool_disk_write_wait_s",
        "oposs_zpool_syncq_read_wait_s",
        "oposs_zpool_syncq_write_wait_s",
        "oposs_zpool_asyncq_read_wait_s",
        "oposs_zpool_asyncq_write_wait_s",
        "oposs_zpool_scrub_wait_s",
        "oposs_zpool_trim_wait_s",
        "oposs_zpool_rebuild_wait_s",
    ],
    minimal_range=MinimalRange(
        lower=0,
        upper=0.001,  # 1ms upper limit - typical for fast storage
    ),
)

# 5. Task Queues - Combined graph for sync and async queues

graph_zpool_queue_depths = Graph(
    name="oposs_zpool_queue_depths",
    title=Title("ZFS Pool Queue Depths"),
    simple_lines=[
        # Sync queue depths
        "oposs_zpool_syncq_read_pend",
        "oposs_zpool_syncq_read_activ",
        "oposs_zpool_syncq_write_pend",
        "oposs_zpool_syncq_write_activ",
        # Async queue depths
        "oposs_zpool_asyncq_read_pend",
        "oposs_zpool_asyncq_read_activ",
        "oposs_zpool_asyncq_write_pend",
        "oposs_zpool_asyncq_write_activ",
        # Scrub queue depths  
        "oposs_zpool_scrubq_read_pend",
        "oposs_zpool_scrubq_read_activ",
        # Trim queue depths (will be NaN until agent is updated)
        "oposs_zpool_trimq_write_pend",
        "oposs_zpool_trimq_write_activ",
        # Rebuild queue depths (will be NaN until agent is updated)
        "oposs_zpool_rebuildq_write_pend",
        "oposs_zpool_rebuildq_write_activ",
    ],
    optional=[
        # All metrics are optional - graph displays even if some are missing
        "oposs_zpool_syncq_read_pend",
        "oposs_zpool_syncq_read_activ",
        "oposs_zpool_syncq_write_pend",
        "oposs_zpool_syncq_write_activ",
        "oposs_zpool_asyncq_read_pend",
        "oposs_zpool_asyncq_read_activ",
        "oposs_zpool_asyncq_write_pend",
        "oposs_zpool_asyncq_write_activ",
        "oposs_zpool_scrubq_read_pend",
        "oposs_zpool_scrubq_read_activ",
        "oposs_zpool_trimq_write_pend",
        "oposs_zpool_trimq_write_activ",
        "oposs_zpool_rebuildq_write_pend",
        "oposs_zpool_rebuildq_write_activ",
    ],
    minimal_range=MinimalRange(
        lower=0,
        upper=100,  # 100 operations upper limit
    ),
)

# Define perfometers
perfometer_zpool_operations = Perfometer(
    name="oposs_zpool_operations",
    focus_range=FocusRange(
        lower=Closed(0),
        upper=Closed(1000),
    ),
    segments=[
        "oposs_zpool_read_ops",
        "oposs_zpool_write_ops",
    ],
)

perfometer_zpool_storage = Perfometer(
    name="oposs_zpool_storage",
    focus_range=FocusRange(
        lower=Closed(0),
        upper=Closed(1000000000000),  # 1TB
    ),
    segments=[
        "oposs_zpool_allocated",
        "oposs_zpool_free",
    ],
)

perfometer_zpool_wait_times = Perfometer(
    name="oposs_zpool_wait_times",
    focus_range=FocusRange(
        lower=Closed(0),
        upper=Closed(0.1),  # 100ms in seconds
    ),
    segments=[
        "oposs_zpool_read_wait_s",
        "oposs_zpool_write_wait_s",
    ],
)

# Stacked perfometer for comprehensive view
perfometer_zpool_comprehensive = Stacked(
    name="oposs_zpool_comprehensive",
    lower=Perfometer(
        name="oposs_zpool_ops_lower",
        focus_range=FocusRange(
            lower=Closed(0),
            upper=Closed(1000),
        ),
        segments=["oposs_zpool_read_ops", "oposs_zpool_write_ops"],
    ),
    upper=Perfometer(
        name="oposs_zpool_storage_upper",
        focus_range=FocusRange(
            lower=Closed(0),
            upper=Closed(1000000000000),  # 1TB
        ),
        segments=["oposs_zpool_allocated", "oposs_zpool_free"],
    ),
)