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
unit_milliseconds = Unit(DecimalNotation("ms"))
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

# Wait time metrics
metric_read_wait = Metric(
    name="read_wait",
    title=Title("Read wait time"),
    unit=unit_milliseconds,
    color=Color.YELLOW,
)

metric_write_wait = Metric(
    name="write_wait",
    title=Title("Write wait time"),
    unit=unit_milliseconds,
    color=Color.ORANGE,
)

metric_disk_read_wait = Metric(
    name="disk_read_wait",
    title=Title("Disk read wait time"),
    unit=unit_milliseconds,
    color=Color.LIGHT_YELLOW,
)

metric_disk_write_wait = Metric(
    name="disk_write_wait",
    title=Title("Disk write wait time"),
    unit=unit_milliseconds,
    color=Color.LIGHT_ORANGE,
)

# Queue wait time metrics
metric_syncq_read_wait = Metric(
    name="syncq_read_wait",
    title=Title("Sync queue read wait time"),
    unit=unit_milliseconds,
    color=Color.LIGHT_GREEN,
)

metric_syncq_write_wait = Metric(
    name="syncq_write_wait",
    title=Title("Sync queue write wait time"),
    unit=unit_milliseconds,
    color=Color.DARK_GREEN,
)

metric_asyncq_read_wait = Metric(
    name="asyncq_read_wait",
    title=Title("Async queue read wait time"),
    unit=unit_milliseconds,
    color=Color.LIGHT_BLUE,
)

metric_asyncq_write_wait = Metric(
    name="asyncq_write_wait",
    title=Title("Async queue write wait time"),
    unit=unit_milliseconds,
    color=Color.DARK_BLUE,
)

# Special operation wait times
metric_scrub_wait = Metric(
    name="scrub_wait",
    title=Title("Scrub wait time"),
    unit=unit_milliseconds,
    color=Color.LIGHT_RED,
)

metric_trim_wait = Metric(
    name="trim_wait",
    title=Title("Trim wait time"),
    unit=unit_milliseconds,
    color=Color.DARK_RED,
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

metric_trimq_read_pend = Metric(
    name="trimq_read_pend",
    title=Title("Trim queue read pending"),
    unit=unit_count,
    color=Color.LIGHT_BLUE,
)

metric_trimq_read_activ = Metric(
    name="trimq_read_activ",
    title=Title("Trim queue read active"),
    unit=unit_count,
    color=Color.DARK_BLUE,
)

# Define graphs
graph_zpool_operations = Graph(
    name="zpool_operations",
    title=Title("ZFS Pool I/O Operations"),
    compound_lines=[
        "read_ops",
        "write_ops",
    ],
    minimal_range=MinimalRange(
        lower=0,
        upper=100,
    ),
)

graph_zpool_throughput = Bidirectional(
    name="zpool_throughput",
    title=Title("ZFS Pool Throughput"),
    lower=Graph(
        name="zpool_throughput_lower",
        title=Title("Read Throughput"),
        compound_lines=["read_throughput"],
    ),
    upper=Graph(
        name="zpool_throughput_upper", 
        title=Title("Write Throughput"),
        compound_lines=["write_throughput"],
    ),
)

graph_zpool_storage = Graph(
    name="zpool_storage",
    title=Title("ZFS Pool Storage"),
    compound_lines=[
        "allocated",
        "free",
    ],
    minimal_range=MinimalRange(
        lower=0,
        upper=1000000000000,  # 1TB default upper limit
    ),
)

graph_zpool_wait_times = Graph(
    name="zpool_wait_times",
    title=Title("ZFS Pool Wait Times"),
    simple_lines=[
        "read_wait",
        "write_wait",
        "disk_read_wait",
        "disk_write_wait",
    ],
    minimal_range=MinimalRange(
        lower=0,
        upper=1000,  # 1000ms upper limit
    ),
)

graph_zpool_queue_wait_times = Graph(
    name="zpool_queue_wait_times",
    title=Title("ZFS Pool Queue Wait Times"),
    simple_lines=[
        "syncq_read_wait",
        "syncq_write_wait",
        "asyncq_read_wait",
        "asyncq_write_wait",
        "scrub_wait",
        "trim_wait",
    ],
    minimal_range=MinimalRange(
        lower=0,
        upper=500,  # 500ms upper limit for queue wait times
    ),
)

graph_zpool_queue_depths = Graph(
    name="zpool_queue_depths",
    title=Title("ZFS Pool Queue Depths"),
    simple_lines=[
        "syncq_read_pend",
        "syncq_read_activ",
        "syncq_write_pend",
        "syncq_write_activ",
        "asyncq_read_pend",
        "asyncq_read_activ",
        "asyncq_write_pend",
        "asyncq_write_activ",
    ],
    minimal_range=MinimalRange(
        lower=0,
        upper=100,  # 100 operations upper limit for queue depths
    ),
)

graph_zpool_special_queues = Graph(
    name="zpool_special_queues",
    title=Title("ZFS Pool Special Operation Queues"),
    simple_lines=[
        "scrubq_read_pend",
        "scrubq_read_activ",
        "trimq_read_pend",
        "trimq_read_activ",
    ],
    minimal_range=MinimalRange(
        lower=0,
        upper=20,  # 20 operations upper limit for special queues
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
        upper=Closed(100),
    ),
    segments=[
        "storage_used_percent",
    ],
)

perfometer_zpool_wait_times = Perfometer(
    name="zpool_wait_times",
    focus_range=FocusRange(
        lower=Closed(0),
        upper=Closed(100),
    ),
    segments=[
        "read_wait",
        "write_wait",
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
            upper=Closed(100),
        ),
        segments=["storage_used_percent"],
    ),
)