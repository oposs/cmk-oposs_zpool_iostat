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
        title=Title("OPOSS zpool iostat Agent Configuration"),
        help_text=Help(
            "Configure the OPOSS zpool iostat monitoring agent plugin for automated deployment. "
            "This plugin collects detailed I/O statistics from ZFS storage pools including "
            "operations per second, throughput, wait times, and queue depths."
        ),
        elements={
            "interval": DictElement(
                parameter_form=TimeSpan(
                    title=Title("Execution interval"),
                    label=Label("How often to collect zpool iostat data"),
                    help_text=Help("0 means every agent run."),
                    displayed_magnitudes=[TimeMagnitude.SECOND, TimeMagnitude.MINUTE],
                    prefill=DefaultValue(300.0),
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
                )
            ),
        }
    )

# Register the bakery rule specification
rule_spec_oposs_zpool_iostat_bakery = AgentConfig(
    name="oposs_zpool_iostat",
    title=Title("OPOSS zpool iostat Agent Deployment"),
    topic=Topic.GENERAL,
    parameter_form=_parameter_form_oposs_zpool_iostat_bakery,
)