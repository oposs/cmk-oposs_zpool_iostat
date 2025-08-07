#!/usr/bin/env python3
"""
CheckMK Check Plugin for OPOSS zpool iostat monitoring
Processes I/O statistics from zpool iostat command using CheckMK 2.3 v2 API
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
)
from typing import Any, Dict, List, Mapping, Optional, Tuple
import json

# ZFS iostat data is now parsed from JSON format by the agent

def _get_levels_from_params(params: Mapping[str, Any], param_key: str) -> Optional[Tuple[float, float]]:
    """
    Extract levels from parameters, handling both tuple and SimpleLevels dictionary formats.
    
    Args:
        params: Check parameters from ruleset
        param_key: Key to look for in params
        
    Returns:
        Tuple of (warning, critical) levels or None if not found/invalid
    """
    if param_key not in params:
        return None
    
    levels = params[param_key]
    
    # Handle tuple format (old CheckMK or direct tuple)
    if isinstance(levels, tuple) and len(levels) == 2:
        return levels
    
    # Handle dict format (new CheckMK 2.3 SimpleLevels)
    if isinstance(levels, dict) and "levels_upper" in levels:
        levels_upper = levels["levels_upper"]
        if isinstance(levels_upper, tuple) and len(levels_upper) == 2:
            return levels_upper
    
    return None

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
        
        # Check storage levels if configured
        storage_levels = _get_levels_from_params(params, 'storage_levels')
        if storage_levels:
            warn, crit = storage_levels
            if used_percent >= crit:
                yield Result(state=State.CRIT, summary=f"Storage utilization: {used_percent:.1f}% (critical at {crit:.1f}%)")
            elif used_percent >= warn:
                yield Result(state=State.WARN, summary=f"Storage utilization: {used_percent:.1f}% (warning at {warn:.1f}%)")
            else:
                yield Result(state=State.OK, summary=f"Storage utilization: {used_percent:.1f}%")
        else:
            yield Result(state=State.OK, summary=f"Storage utilization: {used_percent:.1f}%")
        
        # Always yield storage metrics
        yield Metric("storage_used_percent", used_percent)
    
    # I/O Operation metrics and levels
    yield Metric("read_ops", read_ops)
    yield Metric("write_ops", write_ops)
    
    # Check I/O operation levels if configured
    read_ops_levels = _get_levels_from_params(params, 'read_ops_levels')
    if read_ops_levels:
        warn, crit = read_ops_levels
        if read_ops >= crit:
            yield Result(state=State.CRIT, summary=f"Read operations: {read_ops:.1f}/s (critical at {crit:.1f}/s)")
        elif read_ops >= warn:
            yield Result(state=State.WARN, summary=f"Read operations: {read_ops:.1f}/s (warning at {warn:.1f}/s)")
        
    write_ops_levels = _get_levels_from_params(params, 'write_ops_levels')
    if write_ops_levels:
        warn, crit = write_ops_levels
        if write_ops >= crit:
            yield Result(state=State.CRIT, summary=f"Write operations: {write_ops:.1f}/s (critical at {crit:.1f}/s)")
        elif write_ops >= warn:
            yield Result(state=State.WARN, summary=f"Write operations: {write_ops:.1f}/s (warning at {warn:.1f}/s)")
    
    # Throughput metrics and levels
    yield Metric("read_throughput", read_bytes)
    yield Metric("write_throughput", write_bytes)
    
    # Check throughput levels if configured
    read_throughput_levels = _get_levels_from_params(params, 'read_throughput_levels')
    if read_throughput_levels:
        warn, crit = read_throughput_levels
        if read_bytes >= crit:
            yield Result(state=State.CRIT, summary=f"Read throughput: {render.bytes(read_bytes)} (critical at {render.bytes(crit)})")
        elif read_bytes >= warn:
            yield Result(state=State.WARN, summary=f"Read throughput: {render.bytes(read_bytes)} (warning at {render.bytes(warn)})")
        
    write_throughput_levels = _get_levels_from_params(params, 'write_throughput_levels')
    if write_throughput_levels:
        warn, crit = write_throughput_levels
        if write_bytes >= crit:
            yield Result(state=State.CRIT, summary=f"Write throughput: {render.bytes(write_bytes)} (critical at {render.bytes(crit)})")
        elif write_bytes >= warn:
            yield Result(state=State.WARN, summary=f"Write throughput: {render.bytes(write_bytes)} (warning at {render.bytes(warn)})")
    
    # Storage metrics
    yield Metric("allocated", alloc)
    yield Metric("free", free)
    
    # Wait time metrics and levels
    read_wait = pool_data.get('read_wait', 0)
    write_wait = pool_data.get('write_wait', 0)
    
    yield Metric("read_wait", read_wait)
    yield Metric("write_wait", write_wait)
    
    # Check wait time levels if configured
    read_wait_levels = _get_levels_from_params(params, 'read_wait_levels')
    if read_wait_levels and read_wait > 0:
        warn, crit = read_wait_levels
        if read_wait >= crit:
            yield Result(state=State.CRIT, summary=f"Read wait time: {read_wait:.2f}ms (critical at {crit:.2f}ms)")
        elif read_wait >= warn:
            yield Result(state=State.WARN, summary=f"Read wait time: {read_wait:.2f}ms (warning at {warn:.2f}ms)")
        
    write_wait_levels = _get_levels_from_params(params, 'write_wait_levels')
    if write_wait_levels and write_wait > 0:
        warn, crit = write_wait_levels
        if write_wait >= crit:
            yield Result(state=State.CRIT, summary=f"Write wait time: {write_wait:.2f}ms (critical at {crit:.2f}ms)")
        elif write_wait >= warn:
            yield Result(state=State.WARN, summary=f"Write wait time: {write_wait:.2f}ms (warning at {warn:.2f}ms)")
    
    # Disk-level wait times
    disk_read_wait = pool_data.get('disk_read_wait', 0)
    disk_write_wait = pool_data.get('disk_write_wait', 0)
    
    yield Metric("disk_read_wait", disk_read_wait)
    yield Metric("disk_write_wait", disk_write_wait)
    
    # Check disk wait levels if configured
    disk_wait_levels = _get_levels_from_params(params, 'disk_wait_levels')
    if disk_wait_levels:
        max_disk_wait = max(disk_read_wait, disk_write_wait)
        if max_disk_wait > 0:
            warn, crit = disk_wait_levels
            if max_disk_wait >= crit:
                yield Result(state=State.CRIT, summary=f"Disk wait time: {max_disk_wait:.2f}ms (critical at {crit:.2f}ms)")
            elif max_disk_wait >= warn:
                yield Result(state=State.WARN, summary=f"Disk wait time: {max_disk_wait:.2f}ms (warning at {warn:.2f}ms)")
    
    # Individual queue wait time metrics
    queue_wait_metrics = [
        ('syncq_read_wait', 'syncq_read_wait_levels'),
        ('syncq_write_wait', 'syncq_write_wait_levels'),
        ('asyncq_read_wait', 'asyncq_read_wait_levels'),
        ('asyncq_write_wait', 'asyncq_write_wait_levels'),
        ('scrub_wait', 'scrub_wait_levels'),
        ('trim_wait', 'trim_wait_levels')
    ]
    
    for metric_name, param_name in queue_wait_metrics:
        value = pool_data.get(metric_name, 0)
        if value > 0:
            yield Metric(metric_name, value)
            
            # Check individual levels if configured
            levels = _get_levels_from_params(params, param_name)
            if levels:
                warn, crit = levels
                if value >= crit:
                    yield Result(state=State.CRIT, summary=f"{metric_name.replace('_', ' ').title()}: {value:.2f}ms (critical at {crit:.2f}ms)")
                elif value >= warn:
                    yield Result(state=State.WARN, summary=f"{metric_name.replace('_', ' ').title()}: {value:.2f}ms (warning at {warn:.2f}ms)")
    
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
        ('trimq_read_pend', 'trimq_read_pend_levels'),
        ('trimq_read_activ', 'trimq_read_activ_levels')
    ]
    
    for metric_name, param_name in queue_depth_metrics:
        value = pool_data.get(metric_name, 0)
        if value > 0:
            yield Metric(metric_name, value)
            
            # Check individual levels if configured
            levels = _get_levels_from_params(params, param_name)
            if levels:
                warn, crit = levels
                if value >= crit:
                    yield Result(state=State.CRIT, summary=f"{metric_name.replace('_', ' ').title()}: {value:.0f} (critical at {crit:.0f})")
                elif value >= warn:
                    yield Result(state=State.WARN, summary=f"{metric_name.replace('_', ' ').title()}: {value:.0f} (warning at {warn:.0f})")

# Create the check plugin
check_plugin_oposs_zpool_iostat = CheckPlugin(
    name="oposs_zpool_iostat",
    service_name="ZPool I/O %s",
    sections=["oposs_zpool_iostat"],
    discovery_function=discover_oposs_zpool_iostat,
    check_function=check_oposs_zpool_iostat,
    check_ruleset_name="oposs_zpool_iostat",
    check_default_parameters={
        'storage_levels': (80.0, 90.0),  # Default storage usage levels
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
        'trimq_read_pend_levels': None,
        'trimq_read_activ_levels': None,
    },
)