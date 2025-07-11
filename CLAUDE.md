# Claude Development Notes

This document contains development notes and configuration information for Claude when working on this CheckMK OPOSS zpool iostat plugin.

## Project Structure

```
cmk-oposs_zpool_iostat/
├── local/
│   ├── share/check_mk/agents/plugins/
│   │   └── oposs_zpool_iostat                     # Agent plugin (Python)
│   └── lib/python3/cmk_addons/plugins/
│       ├── agent_based/
│       │   └── oposs_zpool_iostat.py              # Check plugin
│       ├── rulesets/
│       │   ├── oposs_zpool_iostat.py              # Check parameters ruleset
│       │   └── oposs_zpool_iostat_bakery.py       # Agent bakery ruleset
│       └── checkman/
│           └── oposs_zpool_iostat                 # Documentation
├── LICENSE                                        # MIT License
├── README.md                                      # User documentation
└── CLAUDE.md                                      # This file
```

## Key Components

### 1. Agent Plugin (`local/share/check_mk/agents/plugins/oposs_zpool_iostat`)
- **Purpose**: Collects ZFS pool I/O statistics using `zpool iostat -Hylpq`
- **Configuration**: Reads from `/etc/check_mk/oposs_zpool_iostat.json`
- **Supported Config Options**:
  - `enabled`: Enable/disable monitoring (default: true)
  - `timeout`: Command timeout in seconds (default: 30)
  - `sampling_duration`: Iostat sampling duration (default: 10)
- **Output Format**: JSON per pool with pipe separator

### 2. Check Plugin (`agent_based/oposs_zpool_iostat.py`)
- **Purpose**: Processes agent data and performs threshold checking
- **Key Functions**:
  - `parse_oposs_zpool_iostat()`: Parses JSON agent data
  - `discover_oposs_zpool_iostat()`: Discovers ZFS pools
  - `check_oposs_zpool_iostat()`: Performs monitoring checks
- **Behavior**: Only yields Result objects when specific thresholds are configured

### 3. Check Parameters Ruleset (`rulesets/oposs_zpool_iostat.py`)
- **Purpose**: Defines GUI configuration for monitoring thresholds
- **Parameter Groups**:
  - Basic: storage_levels, *_ops_levels, *_wait_levels, *_throughput_levels
  - Advanced: disk_wait_levels, individual queue metrics
- **Alignment**: All parameters correspond to actual `zpool iostat` fields

### 4. Agent Bakery Ruleset (`rulesets/oposs_zpool_iostat_bakery.py`)
- **Purpose**: Automated agent deployment configuration
- **Supported Options**: Only options actually implemented in agent plugin
  - `enabled`, `timeout`, `sampling_duration`
- **Removed**: Fictional options like retry logic, version checking

## Data Flow

1. **Agent Plugin**: Runs `zpool iostat -Hylpq {sampling_duration} 1`
2. **Agent Plugin**: Parses output into structured JSON per pool
3. **Agent Plugin**: Outputs in CheckMK section format with pipe separator
4. **Check Plugin**: Parses JSON data from agent section
5. **Check Plugin**: Calculates derived metrics (e.g., storage utilization %)
6. **Check Plugin**: Applies configured thresholds and yields results

## Available Metrics

### From zpool iostat -Hylpq:
```python
field_names = [
    'pool', 'alloc', 'free', 'read_ops', 'write_ops', 'read_bytes', 'write_bytes',
    'read_wait', 'write_wait', 'disk_read_wait', 'disk_write_wait',
    'syncq_read_wait', 'syncq_write_wait', 'asyncq_read_wait', 'asyncq_write_wait',
    'scrub_wait', 'trim_wait', 'syncq_read_pend', 'syncq_read_activ',
    'syncq_write_pend', 'syncq_write_activ', 'asyncq_read_pend', 'asyncq_read_activ',
    'asyncq_write_pend', 'asyncq_write_activ', 'scrubq_read_pend', 'scrubq_read_activ',
    'trimq_read_pend', 'trimq_read_activ'
]
```

### Derived Metrics:
- `storage_used_percent`: Calculated as `(alloc / (alloc + free)) * 100`

## Configuration Principles

### Ruleset Parameters
- **Only Real Data**: All parameters correspond to actual zpool iostat fields
- **Granular Control**: Individual parameters for each queue metric type
- **Sensible Defaults**: Default thresholds based on metric characteristics
- **Optional**: All parameters optional (None by default except storage_levels)

### Agent Configuration
- **Minimal**: Only options actually implemented in agent
- **Clear Naming**: `sampling_duration` (not `interval`) to avoid confusion with CheckMK plugin intervals

## Important Notes

### Parameter Alignment
- All ruleset parameters must correspond to actual data from `zpool iostat`
- Removed fictional parameters like `collect_detailed_metrics`, `ignore_zero_metrics`
- Agent always collects all available metrics with hardcoded `-Hylpq` flags

### Status Reporting
- No combined status summaries - only yield Result objects for configured thresholds
- Always yield Metric objects for performance data
- Individual threshold checking for each queue metric type

### Testing Commands
```bash
# Test agent plugin manually
/usr/lib/check_mk_agent/plugins/oposs_zpool_iostat

# Check actual zpool iostat output
zpool iostat -Hylpq 10 1

# Verify field count matches agent parsing
zpool iostat -Hylpq 10 1 | awk '{print NF}' | head -1
```

## Development Guidelines

1. **Data Alignment**: Always verify parameters match actual `zpool iostat` output
2. **Error Handling**: Robust error handling with clear error messages
3. **Performance**: Efficient data collection and processing
4. **Documentation**: Keep documentation in sync with actual implementation
5. **Testing**: Test with various ZFS configurations and edge cases

## Future Enhancements

- Support for additional zpool iostat options if needed
- Pool-specific configuration options
- Historical data collection and trending
- Integration with ZFS pool health monitoring