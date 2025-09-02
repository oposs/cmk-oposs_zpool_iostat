#!/usr/bin/env python3
"""
CheckMK Check Plugin for OPOSS zpool iostat monitoring
Processes I/O statistics from zpool iostat command using CheckMK 2.3 v2 API

Note: ZFS reports wait times in nanoseconds. This plugin converts them to seconds
for internal storage and graphing. Thresholds are configured in milliseconds for
user convenience and converted to seconds internally for comparison.

Time-based metrics are stored with _s suffix to indicate seconds unit.
"""

from cmk.agent_based.v2 import (
    AgentSection,
    CheckPlugin,
    CheckResult,
    DiscoveryResult,
    Result,
    Service,
    State,
    Metric,
    render,
    check_levels,
)
from typing import Any, Dict, List, Mapping, Optional, Tuple
import json

# ZFS iostat data is now parsed from JSON format by the agent

def _render_operations_per_second(value: float) -> str:
    """Render operations per second with 1 decimal place."""
    return f"{value:.1f}/s"

def _render_milliseconds(value: float) -> str:
    """Render value as milliseconds with 2 decimal places.
    Input value is in seconds, convert to milliseconds for display.
    """
    return f"{value * 1000:.2f}ms"

def _render_count(value: float) -> str:
    """Render value as count with no decimal places."""
    return f"{value:.0f}"

def _extract_levels(levels_param):
    """
    Extract levels from parameter in various formats.
    
    SimpleLevels produces:
    - ("fixed", (warn, crit)) - fixed levels
    - None - when not configured
    
    This function is now simplified since SimpleLevels already produces
    the correct format for check_levels().
    
    Args:
        levels_param: Levels parameter from ruleset
        
    Returns:
        Levels parameter directly (already in correct format) or None
    """
    # SimpleLevels already produces the correct format, just return it
    return levels_param

def _convert_ms_levels_to_seconds(levels_param):
    """
    Convert millisecond levels to seconds for wait time thresholds.
    
    Args:
        levels_param: Levels parameter with millisecond values
        
    Returns:
        Levels parameter with values converted to seconds, or None
    """
    if not levels_param:
        return None
    
    if isinstance(levels_param, tuple) and levels_param[0] == "fixed" and levels_param[1]:
        warn, crit = levels_param[1]
        return ("fixed", (warn / 1000, crit / 1000))
    
    # Return as-is for other formats (predictive, no_levels, etc.)
    return levels_param

def _check_wait_time_metric(
    value_ns: Optional[float],
    levels_param: Any,
    metric_name: str,
    label: str
) -> CheckResult:
    """
    Helper function to consistently handle wait time metrics.
    
    Args:
        value_ns: Raw value in nanoseconds from zpool iostat (None if metric doesn't exist)
        levels_param: Levels parameter from ruleset (in milliseconds)
        metric_name: Name for the metric (will have _s suffix added)
        label: Human-readable label for check output
        
    Yields:
        Check results and metrics
    """
    # Handle missing metrics
    if value_ns is None:
        yield Metric(metric_name + "_s", float('nan'))
        return
    
    # Convert from nanoseconds to seconds
    value_s = value_ns / 1e9 if value_ns != 0 else 0
    
    # Convert levels if configured
    if levels_param:
        # Convert millisecond thresholds to seconds
        levels_in_seconds = _convert_ms_levels_to_seconds(levels_param)
        yield from check_levels(
            value_s,
            levels_upper=levels_in_seconds,
            metric_name=metric_name + "_s",
            label=label,
            render_func=_render_milliseconds,
        )
    else:
        # Always yield metric for graph display
        yield Metric(metric_name + "_s", value_s)


def parse_oposs_zpool_iostat(string_table: List[List[str]]) -> Dict[str, Any]:
    """
    Parse oposs_zpool_iostat agent data from JSON format.
    
    Args:
        string_table: Raw agent data as list of lines split by separator
        
    Returns:
        Dictionary with pool names as keys and metrics as values
    """
    pools = {}
    
    for line in string_table:
        if len(line) < 2:
            continue
            
        # Handle error lines
        if line[0] == "ERROR":
            error_msg = line[1] if len(line) > 1 else "Unknown error"
            pools['_parse_error'] = error_msg
            continue
            
        # Extract pool name and JSON data
        pool_name = line[0]
        json_data = line[1]
        
        try:
            # Parse JSON payload
            pool_data = json.loads(json_data)
            
            # Validate that we have the expected structure
            if isinstance(pool_data, dict):
                pools[pool_name] = pool_data
            else:
                pools[pool_name] = {'_error': 'Invalid JSON structure'}
                
        except json.JSONDecodeError as e:
            pools[pool_name] = {'_error': f'JSON parsing failed: {str(e)}'}
        except Exception as e:
            pools[pool_name] = {'_error': f'Unexpected error: {str(e)}'}
    
    return pools

# Create the agent section
agent_section_oposs_zpool_iostat = AgentSection(
    name="oposs_zpool_iostat",
    parse_function=parse_oposs_zpool_iostat,
)

def discover_oposs_zpool_iostat(section: Dict[str, Any]) -> DiscoveryResult:
    """
    Discover zpool iostat services.
    
    Args:
        section: Parsed section data
        
    Yields:
        Service objects for each discovered pool
    """
    # Skip error pools and metadata
    for pool_name, pool_data in section.items():
        if not pool_name.startswith('_') and isinstance(pool_data, dict) and '_error' not in pool_data:
            yield Service(item=pool_name)

def check_oposs_zpool_iostat(
    item: str, 
    params: Mapping[str, Any], 
    section: Dict[str, Any]
) -> CheckResult:
    """
    Check zpool iostat metrics.
    
    Args:
        item: Pool name
        params: Check parameters from ruleset
        section: Parsed section data
        
    Yields:
        Check results and metrics
    """
    # Handle global parsing errors
    if '_parse_error' in section:
        yield Result(
            state=State.UNKNOWN,
            summary=f"Parse error: {section['_parse_error']}"
        )
        return
    
    # Check if pool exists
    if item not in section:
        yield Result(
            state=State.UNKNOWN,
            summary=f"Pool {item} not found"
        )
        return
    
    pool_data = section[item]
    
    # Handle pool-specific errors
    if '_error' in pool_data:
        yield Result(
            state=State.UNKNOWN,
            summary=f"Pool {item} error: {pool_data['_error']}"
        )
        return
    
    # Extract basic metrics
    read_ops = pool_data.get('read_ops', 0)
    write_ops = pool_data.get('write_ops', 0)
    read_bytes = pool_data.get('read_bytes', 0)
    write_bytes = pool_data.get('write_bytes', 0)
    
    
    # Storage capacity metrics
    alloc = pool_data.get('alloc', 0)
    free = pool_data.get('free', 0)
    total = alloc + free
    
    if total > 0:
        used_percent = (alloc / total) * 100
        
        # Check storage levels using check_levels function
        levels_upper = params.get('storage_levels')
            
        yield from check_levels(
            used_percent,
            levels_upper=levels_upper,
            metric_name="storage_used_percent",
            label="Storage utilization",
            boundaries=(0.0, 100.0),
            render_func=render.percent,
        )
    
    # I/O Operation metrics and levels
    read_ops_levels = params.get('read_ops_levels')
    if read_ops_levels:
        yield from check_levels(
            read_ops,
            levels_upper=read_ops_levels,
            metric_name="read_ops",
            label="Read operations",
            render_func=_render_operations_per_second,
        )
    else:
        yield Metric("read_ops", read_ops)
    
    write_ops_levels = params.get('write_ops_levels')
    if write_ops_levels:
        yield from check_levels(
            write_ops,
            levels_upper=write_ops_levels,
            metric_name="write_ops", 
            label="Write operations",
            render_func=_render_operations_per_second,
        )
    else:
        yield Metric("write_ops", write_ops)
    
    # Throughput metrics and levels
    read_throughput_levels = params.get('read_throughput_levels')
    if read_throughput_levels:
        yield from check_levels(
            read_bytes,
            levels_upper=read_throughput_levels,
            metric_name="read_throughput",
            label="Read throughput",
            render_func=render.bytes,
        )
    else:
        yield Metric("read_throughput", read_bytes)
        
    write_throughput_levels = params.get('write_throughput_levels')
    if write_throughput_levels:
        yield from check_levels(
            write_bytes,
            levels_upper=write_throughput_levels,
            metric_name="write_throughput",
            label="Write throughput",
            render_func=render.bytes,
        )
    else:
        yield Metric("write_throughput", write_bytes)
    
    # Storage metrics
    yield Metric("allocated", alloc)
    yield Metric("free", free)
    
    # Wait time metrics and levels
    yield from _check_wait_time_metric(
        pool_data.get('read_wait'),
        params.get('read_wait_levels'),
        "read_wait",
        "Read wait time"
    )
    
    yield from _check_wait_time_metric(
        pool_data.get('write_wait'),
        params.get('write_wait_levels'),
        "write_wait",
        "Write wait time"
    )
    
    # Disk-level wait times
    yield from _check_wait_time_metric(
        pool_data.get('disk_read_wait'),
        None,  # No individual levels for disk_read_wait
        "disk_read_wait",
        "Disk read wait time"
    )
    
    yield from _check_wait_time_metric(
        pool_data.get('disk_write_wait'),
        None,  # No individual levels for disk_write_wait
        "disk_write_wait",
        "Disk write wait time"
    )
    
    # Check combined disk wait levels if configured
    disk_wait_levels = params.get('disk_wait_levels')
    if disk_wait_levels:
        disk_read_wait_ns = pool_data.get('disk_read_wait')
        disk_write_wait_ns = pool_data.get('disk_write_wait')
        
        # Only compute max if both values exist
        if disk_read_wait_ns is not None and disk_write_wait_ns is not None:
            max_disk_wait_ns = max(disk_read_wait_ns, disk_write_wait_ns)
            if max_disk_wait_ns > 0:
                # Use helper function for consistent handling
                yield from _check_wait_time_metric(
                    max_disk_wait_ns,
                    params.get('disk_wait_levels'),
                    "disk_wait_max",
                    "Disk wait time"
                )
    
    # Individual queue wait time metrics
    queue_wait_metrics = [
        ('syncq_read_wait', 'syncq_read_wait_levels', 'Sync Queue Read Wait'),
        ('syncq_write_wait', 'syncq_write_wait_levels', 'Sync Queue Write Wait'),
        ('asyncq_read_wait', 'asyncq_read_wait_levels', 'Async Queue Read Wait'),
        ('asyncq_write_wait', 'asyncq_write_wait_levels', 'Async Queue Write Wait'),
        ('scrub_wait', 'scrub_wait_levels', 'Scrub Wait'),
        ('trim_wait', 'trim_wait_levels', 'Trim Wait'),
        ('rebuild_wait', 'rebuild_wait_levels', 'Rebuild Wait')
    ]
    
    for metric_name, param_name, label in queue_wait_metrics:
        yield from _check_wait_time_metric(
            pool_data.get(metric_name),
            params.get(param_name),
            metric_name,
            label
        )
    
    # Individual queue depth metrics
    queue_depth_metrics = [
        ('syncq_read_pend', 'syncq_read_pend_levels'),
        ('syncq_read_activ', 'syncq_read_activ_levels'),
        ('syncq_write_pend', 'syncq_write_pend_levels'),
        ('syncq_write_activ', 'syncq_write_activ_levels'),
        ('asyncq_read_pend', 'asyncq_read_pend_levels'),
        ('asyncq_read_activ', 'asyncq_read_activ_levels'),
        ('asyncq_write_pend', 'asyncq_write_pend_levels'),
        ('asyncq_write_activ', 'asyncq_write_activ_levels'),
        ('scrubq_read_pend', 'scrubq_read_pend_levels'),
        ('scrubq_read_activ', 'scrubq_read_activ_levels'),
        ('trimq_write_pend', 'trimq_write_pend_levels'),
        ('trimq_write_activ', 'trimq_write_activ_levels'),
        ('rebuildq_write_pend', 'rebuildq_write_pend_levels'),
        ('rebuildq_write_activ', 'rebuildq_write_activ_levels')
    ]
    
    for metric_name, param_name in queue_depth_metrics:
        value = pool_data.get(metric_name)
        
        # Always yield metric, even if NaN (for graph display)
        if value is None:
            yield Metric(metric_name, float('nan'))
            continue
            
        levels_param = params.get(param_name)
        if levels_param:
            yield from check_levels(
                value,
                levels_upper=levels_param,
                metric_name=metric_name,
                label=metric_name.replace('_', ' ').title(),
                render_func=_render_count,
            )
        else:
            yield Metric(metric_name, value)

# Create the check plugin
check_plugin_oposs_zpool_iostat = CheckPlugin(
    name="oposs_zpool_iostat",
    service_name="ZPool I/O %s",
    sections=["oposs_zpool_iostat"],
    discovery_function=discover_oposs_zpool_iostat,
    check_function=check_oposs_zpool_iostat,
    check_ruleset_name="oposs_zpool_iostat",
    check_default_parameters={
        'storage_levels': ('fixed', (80.0, 90.0)),  # Default storage usage levels
        'read_ops_levels': None,
        'write_ops_levels': None,
        'read_wait_levels': None,
        'write_wait_levels': None,
        'read_throughput_levels': None,
        'write_throughput_levels': None,
        'disk_wait_levels': None,
        # Individual queue wait time levels
        'syncq_read_wait_levels': None,
        'syncq_write_wait_levels': None,
        'asyncq_read_wait_levels': None,
        'asyncq_write_wait_levels': None,
        'scrub_wait_levels': None,
        'trim_wait_levels': None,
        'rebuild_wait_levels': None,
        # Individual queue depth levels
        'syncq_read_pend_levels': None,
        'syncq_read_activ_levels': None,
        'syncq_write_pend_levels': None,
        'syncq_write_activ_levels': None,
        'asyncq_read_pend_levels': None,
        'asyncq_read_activ_levels': None,
        'asyncq_write_pend_levels': None,
        'asyncq_write_activ_levels': None,
        'scrubq_read_pend_levels': None,
        'scrubq_read_activ_levels': None,
        'trimq_write_pend_levels': None,
        'trimq_write_activ_levels': None,
        'rebuildq_write_pend_levels': None,
        'rebuildq_write_activ_levels': None,
    },
)