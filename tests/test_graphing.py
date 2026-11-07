"""Metric names: prefixed, declared, and translated from the old names."""

import importlib.util
import pathlib
import sys

import pytest
from cmk.agent_based.v2 import Metric
from cmk.graphing.v1 import graphs, metrics, perfometers, translations

ROOT = pathlib.Path(__file__).resolve().parent.parent
PLUGIN = ROOT / "local/lib/python3/cmk_addons/plugins/oposs_zpool_iostat"

# The metric names releases 0.2.0 to 0.2.1 emitted, read from running their
# check modules with every level set (git tags v0.2.0, v0.2.1).
NAMES_0_2 = [
    "allocated", "free", "storage_used_percent",
    "read_ops", "write_ops", "read_throughput", "write_throughput",
    "read_wait_s", "write_wait_s", "disk_read_wait_s", "disk_write_wait_s", "disk_wait_max_s",
    "syncq_read_wait_s", "syncq_write_wait_s", "asyncq_read_wait_s", "asyncq_write_wait_s",
    "scrub_wait_s", "trim_wait_s", "rebuild_wait_s",
    "syncq_read_pend", "syncq_read_activ", "syncq_write_pend", "syncq_write_activ",
    "asyncq_read_pend", "asyncq_read_activ", "asyncq_write_pend", "asyncq_write_activ",
    "scrubq_read_pend", "scrubq_read_activ", "trimq_write_pend", "trimq_write_activ",
    "rebuildq_write_pend", "rebuildq_write_activ",
]
# Releases 0.1.0 to 0.1.5 wrote the latencies in nanoseconds without the _s
# suffix and named the trim queue columns "read" (git tags v0.1.0, v0.1.5).
WAITS_0_1 = [
    "read_wait", "write_wait", "disk_read_wait", "disk_write_wait", "disk_wait_max",
    "syncq_read_wait", "syncq_write_wait", "asyncq_read_wait", "asyncq_write_wait",
    "scrub_wait", "trim_wait",
]
TRIM_0_1 = {"trimq_read_pend": "trimq_write_pend", "trimq_read_activ": "trimq_write_activ"}
NAMES_0_1 = sorted(
    set(NAMES_0_2) - {n for n in NAMES_0_2 if n.endswith("_s") or n.startswith(("rebuild", "trimq"))}
    | set(WAITS_0_1) | set(TRIM_0_1))


def _load(path):
    name = "test_graphing_" + path.stem + "_" + path.parent.name
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


@pytest.fixture(scope="module")
def check():
    return _load(PLUGIN / "agent_based/oposs_zpool_iostat.py")


@pytest.fixture(scope="module")
def graphing_objects():
    objects = []
    for path in sorted((PLUGIN / "graphing").glob("*.py")):
        objects.extend(vars(_load(path)).values())
    return objects


@pytest.fixture(scope="module")
def declared(graphing_objects):
    return {o.name for o in graphing_objects if isinstance(o, metrics.Metric)}


@pytest.fixture(scope="module")
def translation(graphing_objects):
    (found,) = [o for o in graphing_objects if isinstance(o, translations.Translation)]
    return found


@pytest.fixture(scope="module")
def emitted(check):
    """Every metric the check yields when every field is present and every level set."""
    fields = [n.removesuffix("_s") for n in NAMES_0_2] + ["read_bytes", "write_bytes", "alloc"]
    data = {f: 1000 for f in fields}
    params = {k: ("fixed", (1, 2)) for k in check.check_plugin_oposs_zpool_iostat.check_default_parameters}
    out = check.check_oposs_zpool_iostat("tank", params, {"tank": data})
    return [m.name for m in out if isinstance(m, Metric)]


def test_every_emitted_metric_is_prefixed(emitted):
    assert emitted
    assert [n for n in emitted if not n.startswith("oposs_zpool_")] == []


def test_every_emitted_metric_is_declared(emitted, declared):
    assert sorted(set(emitted) - declared) == []


def test_every_declared_metric_is_emitted(emitted, declared):
    assert sorted(declared - set(emitted)) == []


def test_each_metric_is_emitted_once(emitted):
    assert len(emitted) == len(set(emitted))


def test_every_declared_name_is_prefixed(graphing_objects):
    kinds = (metrics.Metric, graphs.Graph, graphs.Bidirectional, perfometers.Perfometer,
             perfometers.Stacked)
    names = [o.name for o in graphing_objects if isinstance(o, kinds)]
    assert names
    assert [n for n in names if not n.startswith("oposs_zpool_")] == []


def test_names_are_unique_per_kind(graphing_objects):
    # Checkmk refuses a second plug-in of the same class and name
    keys = [(type(o), o.name) for o in graphing_objects
            if isinstance(o, (metrics.Metric, graphs.Graph, graphs.Bidirectional,
                              perfometers.Perfometer, perfometers.Stacked))]
    assert len(keys) == len(set(keys))


def _graph_metrics(graph):
    return set(graph.simple_lines) | set(graph.compound_lines or ())


def test_graphs_and_perfometers_use_declared_metrics(graphing_objects, declared):
    used = set()
    for o in graphing_objects:
        if isinstance(o, graphs.Graph):
            used |= _graph_metrics(o)
        elif isinstance(o, graphs.Bidirectional):
            used |= _graph_metrics(o.lower) | _graph_metrics(o.upper)
        elif isinstance(o, perfometers.Perfometer):
            used.update(o.segments)
        elif isinstance(o, perfometers.Stacked):
            used.update(o.lower.segments)
            used.update(o.upper.segments)
    assert used
    assert sorted(used - declared) == []


def test_translation_applies_to_the_live_check_command(translation):
    assert translation.check_commands == [translations.PassiveCheck("oposs_zpool_iostat")]


def test_names_of_0_2_are_renamed(translation, declared):
    for old in NAMES_0_2:
        assert translation.translations[old] == translations.RenameTo(f"oposs_zpool_{old}"), old
        assert f"oposs_zpool_{old}" in declared


def test_waits_of_0_1_are_renamed_and_scaled_to_seconds(translation, declared):
    for old in WAITS_0_1:
        rule = translation.translations[old]
        assert rule == translations.RenameToAndScaleBy(f"oposs_zpool_{old}_s", 1e-9), old
        assert rule.metric_name in declared


def test_trim_queue_of_0_1_is_renamed(translation):
    for old, new in TRIM_0_1.items():
        assert translation.translations[old] == translations.RenameTo(f"oposs_zpool_{new}")


def test_every_old_name_is_translated_and_nothing_else(translation):
    assert sorted(translation.translations) == sorted(set(NAMES_0_1) | set(NAMES_0_2))


def test_every_translation_targets_a_declared_metric(translation, declared):
    assert sorted({r.metric_name for r in translation.translations.values()} - declared) == []
