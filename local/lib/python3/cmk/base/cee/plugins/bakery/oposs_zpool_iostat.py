#!/usr/bin/env python3
"""
CheckMK Agent Bakery plugin for OPOSS zpool iostat monitoring
Provides centralized deployment and configuration management for zpool iostat agent plugin
"""

import json
from cmk.base.plugins.bakery.bakery_api.v1 import (
    register,
    Plugin,
    PluginConfig,
    OS,
)
from pathlib import Path
from typing import Any, Dict

def get_oposs_zpool_iostat_files(conf: Dict[str, Any]):
    """
    Files function for zpool iostat bakery plugin.
    
    Args:
        conf: Configuration dictionary from ruleset
        
    Yields:
        Plugin and configuration objects for deployment
    """
    if conf is None:
        return

    # Get configuration values with defaults
    interval = conf.get("interval", 60)
    timeout = conf.get("timeout", 30)
    sampling_duration = conf.get("sampling_duration", 10)
    
    # Generate JSON configuration file for the agent
    config_content = json.dumps({
        "timeout": int(timeout),
        "sampling_duration": int(sampling_duration),
    }, indent=2)
    
    # Deploy configuration file
    yield PluginConfig(
        base_os=OS.LINUX,
        target=Path("oposs_zpool_iostat.json"),
        lines=config_content.splitlines(),
    )
    
    # Deploy the Python agent plugin
    # This references the source file in local/share/check_mk/agents/plugins/
    yield Plugin(
        base_os=OS.LINUX,
        source=Path('oposs_zpool_iostat'),  # Source file name
        target=Path('oposs_zpool_iostat'),  # Target deployment name
        interval=interval,
    )

# Register the bakery plugin using the official API
register.bakery_plugin(
    name="oposs_zpool_iostat",
    files_function=get_oposs_zpool_iostat_files,
)