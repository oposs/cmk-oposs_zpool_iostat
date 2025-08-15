#!/usr/bin/env python3
"""
CheckMK Ruleset for OPOSS zpool iostat monitoring parameters
Provides GUI configuration interface for zpool iostat thresholds and monitoring options
"""

from cmk.rulesets.v1 import Title, Help, Label
from cmk.rulesets.v1.form_specs import (
    BooleanChoice,
    DefaultValue,
    DictElement,
    Dictionary,
    Float,
    Integer,
    SimpleLevels,
    LevelDirection,
    validators,
)
from cmk.rulesets.v1.rule_specs import (
    CheckParameters,
    HostAndItemCondition,
    Topic,
)

def _parameter_form_oposs_zpool_iostat():
    """Configuration form for zpool iostat check parameters."""
    return Dictionary(
        title=Title("OPOSS zpool iostat Ruleset Configuration"),
        help_text=Help(
            "Configure thresholds and monitoring options for ZFS zpool I/O statistics. "
            "This check monitors pool I/O operations, throughput, latency, and storage utilization."
        ),
        elements={
            "storage_levels": DictElement(
                parameter_form=SimpleLevels(
                    title=Title("Storage utilization levels"),
                    help_text=Help(
                        "Set warning and critical thresholds for storage pool utilization percentage. "
                        "These thresholds help monitor when pools are approaching capacity limits."
                    ),
                    level_direction=LevelDirection.UPPER,
                    form_spec_template=Float(
                        unit_symbol="%",
                        custom_validate=[
                            validators.NumberInRange(min_value=0.0, max_value=100.0)
                        ],
                    ),
                    prefill_fixed_levels=DefaultValue((80.0, 90.0)),
                ),
                required=True,
            ),
            "read_ops_levels": DictElement(
                parameter_form=SimpleLevels(
                    title=Title("Read operations per second levels"),
                    help_text=Help(
                        "Set warning and critical thresholds for read I/O operations per second. "
                        "High read operation rates may indicate performance bottlenecks."
                    ),
                    level_direction=LevelDirection.UPPER,
                    form_spec_template=Integer(
                        unit_symbol="ops/s",
                        custom_validate=[
                            validators.NumberInRange(min_value=0)
                        ],
                    ),
                    prefill_fixed_levels=DefaultValue((1000, 2000)),
                ),
                required=False,
            ),
            "write_ops_levels": DictElement(
                parameter_form=SimpleLevels(
                    title=Title("Write operations per second levels"),
                    help_text=Help(
                        "Set warning and critical thresholds for write I/O operations per second. "
                        "High write operation rates may indicate performance bottlenecks."
                    ),
                    level_direction=LevelDirection.UPPER,
                    form_spec_template=Integer(
                        unit_symbol="ops/s",
                        custom_validate=[
                            validators.NumberInRange(min_value=0)
                        ],
                    ),
                    prefill_fixed_levels=DefaultValue((500, 1000)),
                ),
                required=False,
            ),
            "read_wait_levels": DictElement(
                parameter_form=SimpleLevels(
                    title=Title("Read wait time levels"),
                    help_text=Help(
                        "Set warning and critical thresholds for read I/O wait times in milliseconds. "
                        "High wait times indicate storage performance issues. "
                        "Note: Thresholds are configured in milliseconds for user convenience, "
                        "while internally the metrics are stored in seconds."
                    ),
                    level_direction=LevelDirection.UPPER,
                    form_spec_template=Float(
                        unit_symbol="ms",
                        custom_validate=[
                            validators.NumberInRange(min_value=0.0)
                        ],
                    ),
                    prefill_fixed_levels=DefaultValue((50.0, 100.0)),
                ),
                required=False,
            ),
            "write_wait_levels": DictElement(
                parameter_form=SimpleLevels(
                    title=Title("Write wait time levels"),
                    help_text=Help(
                        "Set warning and critical thresholds for write I/O wait times in milliseconds. "
                        "High wait times indicate storage performance issues. "
                        "Note: Thresholds are configured in milliseconds for user convenience, "
                        "while internally the metrics are stored in seconds."
                    ),
                    level_direction=LevelDirection.UPPER,
                    form_spec_template=Float(
                        unit_symbol="ms",
                        custom_validate=[
                            validators.NumberInRange(min_value=0.0)
                        ],
                    ),
                    prefill_fixed_levels=DefaultValue((100.0, 200.0)),
                ),
                required=False,
            ),
            "read_throughput_levels": DictElement(
                parameter_form=SimpleLevels(
                    title=Title("Read throughput levels"),
                    help_text=Help(
                        "Set warning and critical thresholds for read throughput in bytes per second. "
                        "Monitors the read_bytes metric from zpool iostat."
                    ),
                    level_direction=LevelDirection.UPPER,
                    form_spec_template=Integer(
                        unit_symbol="B/s",
                        custom_validate=[
                            validators.NumberInRange(min_value=0)
                        ],
                    ),
                    prefill_fixed_levels=DefaultValue((100000000, 200000000)),  # 100MB/s, 200MB/s
                ),
                required=False,
            ),
            "write_throughput_levels": DictElement(
                parameter_form=SimpleLevels(
                    title=Title("Write throughput levels"),
                    help_text=Help(
                        "Set warning and critical thresholds for write throughput in bytes per second. "
                        "Monitors the write_bytes metric from zpool iostat."
                    ),
                    level_direction=LevelDirection.UPPER,
                    form_spec_template=Integer(
                        unit_symbol="B/s",
                        custom_validate=[
                            validators.NumberInRange(min_value=0)
                        ],
                    ),
                    prefill_fixed_levels=DefaultValue((50000000, 100000000)),  # 50MB/s, 100MB/s
                ),
                required=False,
            ),
            "disk_wait_levels": DictElement(
                parameter_form=SimpleLevels(
                    title=Title("Disk I/O wait time levels"),
                    help_text=Help(
                        "Set warning and critical thresholds for disk-level I/O wait times in milliseconds. "
                        "Monitors disk_read_wait and disk_write_wait metrics from zpool iostat. "
                        "Note: Thresholds are configured in milliseconds for user convenience, "
                        "while internally the metrics are stored in seconds."
                    ),
                    level_direction=LevelDirection.UPPER,
                    form_spec_template=Float(
                        unit_symbol="ms",
                        custom_validate=[
                            validators.NumberInRange(min_value=0.0)
                        ],
                    ),
                    prefill_fixed_levels=DefaultValue((20.0, 50.0)),
                ),
                required=False,
            ),
            "syncq_read_wait_levels": DictElement(
                parameter_form=SimpleLevels(
                    title=Title("Sync read queue wait time levels"),
                    help_text=Help(
                        "Thresholds for synchronous read queue wait times in milliseconds. "
                        "Note: Configured in milliseconds, internally stored in seconds."
                    ),
                    level_direction=LevelDirection.UPPER,
                    form_spec_template=Float(unit_symbol="ms"),
                    prefill_fixed_levels=DefaultValue((10.0, 25.0)),
                ),
                required=False,
            ),
            "syncq_write_wait_levels": DictElement(
                parameter_form=SimpleLevels(
                    title=Title("Sync write queue wait time levels"),
                    help_text=Help(
                        "Thresholds for synchronous write queue wait times in milliseconds. "
                        "Note: Configured in milliseconds, internally stored in seconds."
                    ),
                    level_direction=LevelDirection.UPPER,
                    form_spec_template=Float(unit_symbol="ms"),
                    prefill_fixed_levels=DefaultValue((10.0, 25.0)),
                ),
                required=False,
            ),
            "asyncq_read_wait_levels": DictElement(
                parameter_form=SimpleLevels(
                    title=Title("Async read queue wait time levels"),
                    help_text=Help(
                        "Thresholds for asynchronous read queue wait times in milliseconds. "
                        "Note: Configured in milliseconds, internally stored in seconds."
                    ),
                    level_direction=LevelDirection.UPPER,
                    form_spec_template=Float(unit_symbol="ms"),
                    prefill_fixed_levels=DefaultValue((5.0, 15.0)),
                ),
                required=False,
            ),
            "asyncq_write_wait_levels": DictElement(
                parameter_form=SimpleLevels(
                    title=Title("Async write queue wait time levels"),
                    help_text=Help(
                        "Thresholds for asynchronous write queue wait times in milliseconds. "
                        "Note: Configured in milliseconds, internally stored in seconds."
                    ),
                    level_direction=LevelDirection.UPPER,
                    form_spec_template=Float(unit_symbol="ms"),
                    prefill_fixed_levels=DefaultValue((5.0, 15.0)),
                ),
                required=False,
            ),
            "scrub_wait_levels": DictElement(
                parameter_form=SimpleLevels(
                    title=Title("Scrub operation wait time levels"),
                    help_text=Help(
                        "Thresholds for scrub operation wait times in milliseconds. "
                        "Note: Configured in milliseconds, internally stored in seconds."
                    ),
                    level_direction=LevelDirection.UPPER,
                    form_spec_template=Float(unit_symbol="ms"),
                    prefill_fixed_levels=DefaultValue((50.0, 100.0)),
                ),
                required=False,
            ),
            "trim_wait_levels": DictElement(
                parameter_form=SimpleLevels(
                    title=Title("Trim operation wait time levels"),
                    help_text=Help(
                        "Thresholds for trim operation wait times in milliseconds. "
                        "Note: Configured in milliseconds, internally stored in seconds."
                    ),
                    level_direction=LevelDirection.UPPER,
                    form_spec_template=Float(unit_symbol="ms"),
                    prefill_fixed_levels=DefaultValue((30.0, 60.0)),
                ),
                required=False,
            ),
            "rebuild_wait_levels": DictElement(
                parameter_form=SimpleLevels(
                    title=Title("Rebuild operation wait time levels"),
                    help_text=Help(
                        "Thresholds for rebuild operation wait times in milliseconds. "
                        "Note: Configured in milliseconds, internally stored in seconds."
                    ),
                    level_direction=LevelDirection.UPPER,
                    form_spec_template=Float(unit_symbol="ms"),
                    prefill_fixed_levels=DefaultValue((30.0, 60.0)),
                ),
                required=False,
            ),
            "syncq_read_pend_levels": DictElement(
                parameter_form=SimpleLevels(
                    title=Title("Sync read queue pending levels"),
                    help_text=Help("Thresholds for pending synchronous read operations."),
                    level_direction=LevelDirection.UPPER,
                    form_spec_template=Integer(unit_symbol="operations"),
                    prefill_fixed_levels=DefaultValue((16, 32)),
                ),
                required=False,
            ),
            "syncq_read_activ_levels": DictElement(
                parameter_form=SimpleLevels(
                    title=Title("Sync read queue active levels"),
                    help_text=Help("Thresholds for active synchronous read operations."),
                    level_direction=LevelDirection.UPPER,
                    form_spec_template=Integer(unit_symbol="operations"),
                    prefill_fixed_levels=DefaultValue((8, 16)),
                ),
                required=False,
            ),
            "syncq_write_pend_levels": DictElement(
                parameter_form=SimpleLevels(
                    title=Title("Sync write queue pending levels"),
                    help_text=Help("Thresholds for pending synchronous write operations."),
                    level_direction=LevelDirection.UPPER,
                    form_spec_template=Integer(unit_symbol="operations"),
                    prefill_fixed_levels=DefaultValue((16, 32)),
                ),
                required=False,
            ),
            "syncq_write_activ_levels": DictElement(
                parameter_form=SimpleLevels(
                    title=Title("Sync write queue active levels"),
                    help_text=Help("Thresholds for active synchronous write operations."),
                    level_direction=LevelDirection.UPPER,
                    form_spec_template=Integer(unit_symbol="operations"),
                    prefill_fixed_levels=DefaultValue((8, 16)),
                ),
                required=False,
            ),
            "asyncq_read_pend_levels": DictElement(
                parameter_form=SimpleLevels(
                    title=Title("Async read queue pending levels"),
                    help_text=Help("Thresholds for pending asynchronous read operations."),
                    level_direction=LevelDirection.UPPER,
                    form_spec_template=Integer(unit_symbol="operations"),
                    prefill_fixed_levels=DefaultValue((32, 64)),
                ),
                required=False,
            ),
            "asyncq_read_activ_levels": DictElement(
                parameter_form=SimpleLevels(
                    title=Title("Async read queue active levels"),
                    help_text=Help("Thresholds for active asynchronous read operations."),
                    level_direction=LevelDirection.UPPER,
                    form_spec_template=Integer(unit_symbol="operations"),
                    prefill_fixed_levels=DefaultValue((16, 32)),
                ),
                required=False,
            ),
            "asyncq_write_pend_levels": DictElement(
                parameter_form=SimpleLevels(
                    title=Title("Async write queue pending levels"),
                    help_text=Help("Thresholds for pending asynchronous write operations."),
                    level_direction=LevelDirection.UPPER,
                    form_spec_template=Integer(unit_symbol="operations"),
                    prefill_fixed_levels=DefaultValue((32, 64)),
                ),
                required=False,
            ),
            "asyncq_write_activ_levels": DictElement(
                parameter_form=SimpleLevels(
                    title=Title("Async write queue active levels"),
                    help_text=Help("Thresholds for active asynchronous write operations."),
                    level_direction=LevelDirection.UPPER,
                    form_spec_template=Integer(unit_symbol="operations"),
                    prefill_fixed_levels=DefaultValue((16, 32)),
                ),
                required=False,
            ),
            "scrubq_read_pend_levels": DictElement(
                parameter_form=SimpleLevels(
                    title=Title("Scrub queue pending levels"),
                    help_text=Help("Thresholds for pending scrub read operations."),
                    level_direction=LevelDirection.UPPER,
                    form_spec_template=Integer(unit_symbol="operations"),
                    prefill_fixed_levels=DefaultValue((4, 8)),
                ),
                required=False,
            ),
            "scrubq_read_activ_levels": DictElement(
                parameter_form=SimpleLevels(
                    title=Title("Scrub queue active levels"),
                    help_text=Help("Thresholds for active scrub read operations."),
                    level_direction=LevelDirection.UPPER,
                    form_spec_template=Integer(unit_symbol="operations"),
                    prefill_fixed_levels=DefaultValue((2, 4)),
                ),
                required=False,
            ),
            "trimq_write_pend_levels": DictElement(
                parameter_form=SimpleLevels(
                    title=Title("Trim queue write pending levels"),
                    help_text=Help("Thresholds for pending trim write operations."),
                    level_direction=LevelDirection.UPPER,
                    form_spec_template=Integer(unit_symbol="operations"),
                    prefill_fixed_levels=DefaultValue((4, 8)),
                ),
                required=False,
            ),
            "trimq_write_activ_levels": DictElement(
                parameter_form=SimpleLevels(
                    title=Title("Trim queue write active levels"),
                    help_text=Help("Thresholds for active trim write operations."),
                    level_direction=LevelDirection.UPPER,
                    form_spec_template=Integer(unit_symbol="operations"),
                    prefill_fixed_levels=DefaultValue((2, 4)),
                ),
                required=False,
            ),
            "rebuildq_write_pend_levels": DictElement(
                parameter_form=SimpleLevels(
                    title=Title("Rebuild queue write pending levels"),
                    help_text=Help("Thresholds for pending rebuild write operations."),
                    level_direction=LevelDirection.UPPER,
                    form_spec_template=Integer(unit_symbol="operations"),
                    prefill_fixed_levels=DefaultValue((4, 8)),
                ),
                required=False,
            ),
            "rebuildq_write_activ_levels": DictElement(
                parameter_form=SimpleLevels(
                    title=Title("Rebuild queue write active levels"),
                    help_text=Help("Thresholds for active rebuild write operations."),
                    level_direction=LevelDirection.UPPER,
                    form_spec_template=Integer(unit_symbol="operations"),
                    prefill_fixed_levels=DefaultValue((2, 4)),
                ),
                required=False,
            ),
        },
    )

# Register the check parameters ruleset
rule_spec_oposs_zpool_iostat = CheckParameters(
    title=Title("OPOSS zpool iostat Ruleset"),
    topic=Topic.STORAGE,
    name="oposs_zpool_iostat",
    parameter_form=_parameter_form_oposs_zpool_iostat,
    condition=HostAndItemCondition(item_title=Title("ZPool name")),
)