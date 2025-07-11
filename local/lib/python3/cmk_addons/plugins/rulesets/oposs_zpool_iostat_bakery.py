#!/usr/bin/env python3
"""
CheckMK Agent Bakery ruleset for OPOSS zpool iostat monitoring
Provides GUI configuration interface for Agent Bakery deployment
"""

from cmk.rulesets.v1 import Label, Title, Help
from cmk.rulesets.v1.form_specs import (
    BooleanChoice,
    DefaultValue,
    DictElement,
    Dictionary,
    Integer,
    TimeSpan,
    TimeMagnitude,
    validators,
)
from cmk.rulesets.v1.rule_specs import AgentConfig, Topic

def _parameter_form_oposs_zpool_iostat_bakery():
    """Configuration interface for zpool iostat agent plugin."""
    return Dictionary(
        title=Title("OPOSS zpool iostat Agent Plugin"),
        help_text=Help(
            "Configure the OPOSS zpool iostat monitoring agent plugin for automated deployment. "
            "This plugin collects detailed I/O statistics from ZFS storage pools including "
            "operations per second, throughput, wait times, and queue depths."
        ),
        elements={
            "enabled": DictElement(
                parameter_form=BooleanChoice(
                    title=Title("Enable zpool iostat monitoring"),
                    label=Label("Enable monitoring"),
                    help_text=Help(
                        "Enable or disable OPOSS zpool iostat monitoring on target hosts. "
                        "Requires ZFS to be installed and at least one zpool to be configured."
                    ),
                    prefill=DefaultValue(True),
                )
            ),
            "timeout": DictElement(
                parameter_form=TimeSpan(
                    title=Title("Command execution timeout"),
                    label=Label("Maximum time to wait for zpool iostat command"),
                    help_text=Help(
                        "Timeout for the zpool iostat command execution. If the command takes longer "
                        "than this value, it will be terminated and an error reported."
                    ),
                    displayed_magnitudes=[TimeMagnitude.SECOND],
                    prefill=DefaultValue(30.0),
                    custom_validate=[
                        validators.NumberInRange(min_value=5.0, max_value=300.0)
                    ],
                )
            ),
            "sampling_duration": DictElement(
                parameter_form=Integer(
                    title=Title("zpool iostat sampling duration"),
                    label=Label("How long iostat collects data before reporting"),
                    help_text=Help(
                        "Duration in seconds for zpool iostat to collect data before reporting "
                        "averaged statistics. Higher values provide more stable averages but may "
                        "delay detection of short-term issues. This is the 'interval' parameter "
                        "passed to the zpool iostat command."
                    ),
                    unit_symbol="seconds",
                    prefill=DefaultValue(10),
                    custom_validate=[
                        validators.NumberInRange(min_value=1, max_value=60)
                    ],
                )
            ),
        }
    )

# Register the bakery rule specification
rule_spec_oposs_zpool_iostat_bakery = AgentConfig(
    name="oposs_zpool_iostat",
    title=Title("OPOSS zpool iostat Agent Plugin"),
    topic=Topic.GENERAL,
    parameter_form=_parameter_form_oposs_zpool_iostat_bakery,
)