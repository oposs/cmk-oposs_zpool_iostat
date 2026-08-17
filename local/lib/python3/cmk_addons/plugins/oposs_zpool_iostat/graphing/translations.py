#!/usr/bin/env python3
"""
Metric translations for the OPOSS zpool iostat plugin.

Version 0.3.0 prefixed every metric name with ``oposs_zpool_`` to avoid
collisions with the built-in Checkmk metrics of the same base name
(``read_ops``, ``free``, ...), which are a hard error on Checkmk 3.0.

Renaming a metric normally orphans its RRD history: the check starts writing
to a new RRD and the old one is no longer queried. These translations prevent
that. RRD files are never renamed on disk; the translation is a query-time
alias, so graphing a new metric name also pulls in the data recorded under the
old one and merges the two series chronologically.

This works here because the check command (``oposs_zpool_iostat``) and the
service name (``ZPool I/O %s``) are unchanged across the rename, so the legacy
RRD files live in the same per-service directory as the new ones. ``check_commands``
must reference the *current* check command -- the one live services have today --
which for this plugin is also the old one.
"""

from cmk.graphing.v1 import translations

translation_oposs_zpool_iostat = translations.Translation(
    name="oposs_zpool_iostat",
    check_commands=[translations.PassiveCheck("oposs_zpool_iostat")],
    translations={
        "allocated": translations.RenameTo("oposs_zpool_allocated"),
        "free": translations.RenameTo("oposs_zpool_free"),
        "storage_used_percent": translations.RenameTo("oposs_zpool_storage_used_percent"),
        "read_ops": translations.RenameTo("oposs_zpool_read_ops"),
        "write_ops": translations.RenameTo("oposs_zpool_write_ops"),
        "read_throughput": translations.RenameTo("oposs_zpool_read_throughput"),
        "write_throughput": translations.RenameTo("oposs_zpool_write_throughput"),
        "read_wait_s": translations.RenameTo("oposs_zpool_read_wait_s"),
        "write_wait_s": translations.RenameTo("oposs_zpool_write_wait_s"),
        "disk_read_wait_s": translations.RenameTo("oposs_zpool_disk_read_wait_s"),
        "disk_write_wait_s": translations.RenameTo("oposs_zpool_disk_write_wait_s"),
        "disk_wait_max_s": translations.RenameTo("oposs_zpool_disk_wait_max_s"),
        "syncq_read_wait_s": translations.RenameTo("oposs_zpool_syncq_read_wait_s"),
        "syncq_write_wait_s": translations.RenameTo("oposs_zpool_syncq_write_wait_s"),
        "asyncq_read_wait_s": translations.RenameTo("oposs_zpool_asyncq_read_wait_s"),
        "asyncq_write_wait_s": translations.RenameTo("oposs_zpool_asyncq_write_wait_s"),
        "scrub_wait_s": translations.RenameTo("oposs_zpool_scrub_wait_s"),
        "trim_wait_s": translations.RenameTo("oposs_zpool_trim_wait_s"),
        "rebuild_wait_s": translations.RenameTo("oposs_zpool_rebuild_wait_s"),
        "syncq_read_pend": translations.RenameTo("oposs_zpool_syncq_read_pend"),
        "syncq_read_activ": translations.RenameTo("oposs_zpool_syncq_read_activ"),
        "syncq_write_pend": translations.RenameTo("oposs_zpool_syncq_write_pend"),
        "syncq_write_activ": translations.RenameTo("oposs_zpool_syncq_write_activ"),
        "asyncq_read_pend": translations.RenameTo("oposs_zpool_asyncq_read_pend"),
        "asyncq_read_activ": translations.RenameTo("oposs_zpool_asyncq_read_activ"),
        "asyncq_write_pend": translations.RenameTo("oposs_zpool_asyncq_write_pend"),
        "asyncq_write_activ": translations.RenameTo("oposs_zpool_asyncq_write_activ"),
        "scrubq_read_pend": translations.RenameTo("oposs_zpool_scrubq_read_pend"),
        "scrubq_read_activ": translations.RenameTo("oposs_zpool_scrubq_read_activ"),
        "trimq_write_pend": translations.RenameTo("oposs_zpool_trimq_write_pend"),
        "trimq_write_activ": translations.RenameTo("oposs_zpool_trimq_write_activ"),
        "rebuildq_write_pend": translations.RenameTo("oposs_zpool_rebuildq_write_pend"),
        "rebuildq_write_activ": translations.RenameTo("oposs_zpool_rebuildq_write_activ"),

        # --- pre-0.2.0 metrics -------------------------------------------
        # Before 0.2.0 wait times were stored as the raw nanosecond values
        # that ZFS reports, under names without the _s suffix. Scale them to
        # seconds (ns * 1e-9) as well as renaming.
        "read_wait": translations.RenameToAndScaleBy("oposs_zpool_read_wait_s", 1e-9),
        "write_wait": translations.RenameToAndScaleBy("oposs_zpool_write_wait_s", 1e-9),
        "disk_read_wait": translations.RenameToAndScaleBy("oposs_zpool_disk_read_wait_s", 1e-9),
        "disk_write_wait": translations.RenameToAndScaleBy("oposs_zpool_disk_write_wait_s", 1e-9),
        "disk_wait_max": translations.RenameToAndScaleBy("oposs_zpool_disk_wait_max_s", 1e-9),
        "syncq_read_wait": translations.RenameToAndScaleBy("oposs_zpool_syncq_read_wait_s", 1e-9),
        "syncq_write_wait": translations.RenameToAndScaleBy("oposs_zpool_syncq_write_wait_s", 1e-9),
        "asyncq_read_wait": translations.RenameToAndScaleBy("oposs_zpool_asyncq_read_wait_s", 1e-9),
        "asyncq_write_wait": translations.RenameToAndScaleBy("oposs_zpool_asyncq_write_wait_s", 1e-9),
        "scrub_wait": translations.RenameToAndScaleBy("oposs_zpool_scrub_wait_s", 1e-9),
        "trim_wait": translations.RenameToAndScaleBy("oposs_zpool_trim_wait_s", 1e-9),

        # Before 0.2.0 the agent used a hardcoded positional field list and
        # labelled the trim queue columns "read". ZFS has no trim read queue;
        # these were always the trim *write* columns, so the old series is the
        # same measurement under a wrong name.
        "trimq_read_pend": translations.RenameTo("oposs_zpool_trimq_write_pend"),
        "trimq_read_activ": translations.RenameTo("oposs_zpool_trimq_write_activ"),
    },
)
