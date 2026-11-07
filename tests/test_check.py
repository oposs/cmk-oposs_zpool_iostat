"""Tests for the check plugin (runs on the Checkmk server)."""

import importlib.util
import json
import math
import pathlib
import sys
from importlib.machinery import SourceFileLoader

import pytest
import zpool_samples as zs
from cmk.agent_based.v2 import Metric, Result, Service, State

ROOT = pathlib.Path(__file__).resolve().parent.parent
CHECK = ROOT / "local/lib/python3/cmk_addons/plugins/oposs_zpool_iostat/agent_based/oposs_zpool_iostat.py"
AGENT = ROOT / "local/share/check_mk/agents/plugins/oposs_zpool_iostat"


@pytest.fixture(scope="module")
def check():
    name = "test_oposs_zpool_iostat_check"
    spec = importlib.util.spec_from_file_location(name, CHECK)
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    yield module
    sys.modules.pop(name, None)


@pytest.fixture(scope="module")
def agent_lines():
    """What the agent plugin prints for the tank and rpool samples, as the
    string table Checkmk builds from it with sep(124)."""
    loader = SourceFileLoader("oposs_zpool_iostat_agent_for_check", str(AGENT))
    agent = importlib.util.module_from_spec(importlib.util.spec_from_loader(loader.name, loader))
    loader.exec_module(agent)
    rows = [("tank", zs.TANK), ("rpool", zs.RPOOL)]
    fields = agent.parse_headers(*zs.header([n for n, _ in rows])[:2])
    pools = agent.parse_iostat_output(zs.scripted(rows).strip(), fields)
    return [[name, json.dumps(data, separators=(",", ":"))] for name, data in pools.items()]


@pytest.fixture(scope="module")
def section(check, agent_lines):
    return check.parse_oposs_zpool_iostat(agent_lines)


def _defaults(check):
    return dict(check.check_plugin_oposs_zpool_iostat.check_default_parameters)


def _run(check, section, item="tank", **params):
    return list(check.check_oposs_zpool_iostat(item, {**_defaults(check), **params}, section))


def _results(out):
    return [r for r in out if isinstance(r, Result)]


def _metrics(out):
    return {m.name: m.value for m in out if isinstance(m, Metric)}


# --- parse ---------------------------------------------------------------------

def test_parse_agent_output(section):
    assert set(section) == {"tank", "rpool"}
    assert section["tank"]["read_ops"] == 152
    assert section["rpool"]["write_wait"] == 312000


def test_parse_bad_json(check):
    section = check.parse_oposs_zpool_iostat([["tank", "{broken"]])
    assert section["tank"]["_error"].startswith("JSON parsing failed")


def test_parse_json_that_is_not_an_object(check):
    assert check.parse_oposs_zpool_iostat([["tank", "[1, 2]"]]) == {
        "tank": {"_error": "Invalid JSON structure"}}


def test_parse_skips_short_lines(check):
    assert check.parse_oposs_zpool_iostat([["tank"], []]) == {}


def test_parse_error_line(check):
    assert check.parse_oposs_zpool_iostat([["ERROR", "No pools found"]]) == {
        "_parse_error": "No pools found"}


# --- discovery -----------------------------------------------------------------

def test_discovery_one_service_per_pool(check, section):
    assert list(check.discover_oposs_zpool_iostat(section)) == [
        Service(item="tank"), Service(item="rpool")]


def test_discovery_skips_broken_pools_and_errors(check):
    section = check.parse_oposs_zpool_iostat([
        ["tank", "{broken"], ["ERROR", "x"], ["rpool", json.dumps({"alloc": 1, "free": 1})]])
    assert list(check.discover_oposs_zpool_iostat(section)) == [Service(item="rpool")]


def test_service_name(check):
    assert check.check_plugin_oposs_zpool_iostat.service_name == "ZPool I/O %s"


# --- check: defaults -------------------------------------------------------------

def test_defaults_ok_with_storage_summary(check, section):
    out = _run(check, section)
    (result,) = _results(out)
    # 3298534883328 / (3298534883328 + 4698694819840)
    assert result.state is State.OK
    assert result.summary == "Storage utilization: 41.25%"


def test_default_metrics(check, section):
    m = _metrics(_run(check, section))
    assert m["oposs_zpool_storage_used_percent"] == pytest.approx(41.2459, abs=1e-3)
    assert m["oposs_zpool_allocated"] == 3298534883328
    assert m["oposs_zpool_free"] == 4698694819840
    assert m["oposs_zpool_read_ops"] == 152
    assert m["oposs_zpool_write_ops"] == 873
    assert m["oposs_zpool_read_throughput"] == 9961472
    assert m["oposs_zpool_write_throughput"] == 52428800
    # ZFS reports nanoseconds, the metrics are seconds
    assert m["oposs_zpool_read_wait_s"] == pytest.approx(0.002412345)
    assert m["oposs_zpool_write_wait_s"] == pytest.approx(0.008123456)
    assert m["oposs_zpool_disk_read_wait_s"] == pytest.approx(0.00183)
    assert m["oposs_zpool_asyncq_write_wait_s"] == pytest.approx(0.003456789)
    assert m["oposs_zpool_scrub_wait_s"] == 0
    assert m["oposs_zpool_rebuild_wait_s"] == 0
    assert m["oposs_zpool_asyncq_write_pend"] == 12
    assert m["oposs_zpool_asyncq_write_activ"] == 4
    # Only computed when disk wait levels are set
    assert "oposs_zpool_disk_wait_max_s" not in m


@pytest.mark.parametrize("alloc,state", [(79, State.OK), (80, State.WARN), (90, State.CRIT)])
def test_default_storage_levels(check, alloc, state):
    section = {"tank": {"alloc": alloc, "free": 100 - alloc}}
    (result,) = _results(_run(check, section))
    assert result.state is state


def test_storage_levels_off(check):
    section = {"tank": {"alloc": 99, "free": 1}}
    out = _run(check, section, storage_levels=("no_levels", None))
    assert [r.state for r in _results(out)] == [State.OK]


def test_empty_pool_has_no_utilization(check):
    m = _metrics(_run(check, {"tank": {"alloc": 0, "free": 0}}))
    assert "oposs_zpool_storage_used_percent" not in m
    assert m["oposs_zpool_allocated"] == 0


def test_missing_latency_and_queue_fields_graph_as_gaps(check):
    # An agent on OpenZFS 0.8 sends no rebuild fields
    out = _run(check, {"tank": {"alloc": 1, "free": 1, "read_wait": 1000}})
    m = _metrics(out)
    assert m["oposs_zpool_read_wait_s"] == pytest.approx(1e-6)
    assert math.isnan(m["oposs_zpool_rebuild_wait_s"])
    assert math.isnan(m["oposs_zpool_rebuildq_write_pend"])


# --- check: levels -------------------------------------------------------------

@pytest.mark.parametrize("param,levels,state,text", [
    ("read_ops_levels", (100, 200), State.WARN, "Read operations: 152.0/s (warn/crit at 100.0/s/200.0/s)"),
    ("write_ops_levels", (500, 800), State.CRIT, "Write operations: 873.0/s (warn/crit at 500.0/s/800.0/s)"),
    ("read_throughput_levels", (5000000, 20000000), State.WARN, "Read throughput: 9.50 MiB"),
    ("write_throughput_levels", (10000000, 50000000), State.CRIT, "Write throughput: 50.0 MiB"),
    ("asyncq_write_pend_levels", (10, 20), State.WARN, "Asyncq Write Pend: 12 (warn/crit at 10/20)"),
    ("asyncq_write_activ_levels", (2, 4), State.CRIT, "Asyncq Write Activ: 4 (warn/crit at 2/4)"),
])
def test_levels(check, section, param, levels, state, text):
    out = _run(check, section, **{param: ("fixed", levels)})
    (hit,) = [r for r in _results(out) if r.state is not State.OK]
    assert hit.state is state
    assert hit.summary.startswith(text)


@pytest.mark.parametrize("param,metric,levels_ms,state,text", [
    # Levels are milliseconds in the rule, values nanoseconds from ZFS
    ("read_wait_levels", "oposs_zpool_read_wait_s", (2.0, 5.0), State.WARN,
     "Read wait time: 2.41ms (warn/crit at 2.00ms/5.00ms)"),
    ("write_wait_levels", "oposs_zpool_write_wait_s", (5.0, 8.0), State.CRIT,
     "Write wait time: 8.12ms (warn/crit at 5.00ms/8.00ms)"),
    ("asyncq_write_wait_levels", "oposs_zpool_asyncq_write_wait_s", (3.0, 10.0), State.WARN,
     "Async Queue Write Wait: 3.46ms"),
    ("syncq_read_wait_levels", "oposs_zpool_syncq_read_wait_s", (0.01, 0.1), State.WARN,
     "Sync Queue Read Wait: 0.02ms"),
])
def test_wait_levels_in_milliseconds(check, section, param, metric, levels_ms, state, text):
    out = _run(check, section, **{param: ("fixed", levels_ms)})
    (hit,) = [r for r in _results(out) if r.state is not State.OK]
    assert hit.state is state
    assert hit.summary.startswith(text)
    (m,) = [o for o in out if isinstance(o, Metric) and o.name == metric]
    assert m.levels == pytest.approx((levels_ms[0] / 1000, levels_ms[1] / 1000))


def test_wait_levels_not_crossed(check, section):
    out = _run(check, section, read_wait_levels=("fixed", (50.0, 100.0)))
    assert [r.state for r in _results(out)] == [State.OK, State.OK]
    assert _results(out)[1].summary == "Read wait time: 2.41ms"


def test_disk_wait_levels_use_the_slower_direction(check, section):
    out = _run(check, section, disk_wait_levels=("fixed", (4.0, 10.0)))
    (hit,) = [r for r in _results(out) if r.state is not State.OK]
    assert hit.state is State.WARN
    assert hit.summary.startswith("Disk wait time: 4.21ms")
    assert _metrics(out)["oposs_zpool_disk_wait_max_s"] == pytest.approx(0.00421)


def test_disk_wait_levels_on_idle_pool(check, section):
    # rpool read nothing; only the write direction counts
    out = _run(check, section, "rpool", disk_wait_levels=("fixed", (0.1, 1.0)))
    assert _results(out)[-1].state is State.WARN
    assert _metrics(out)["oposs_zpool_disk_wait_max_s"] == pytest.approx(0.00025)


def test_levels_off_give_metrics_only(check, section):
    params = {k: ("no_levels", None) for k in _defaults(check)}
    out = list(check.check_oposs_zpool_iostat("tank", params, section))
    assert [r.summary for r in _results(out)] == ["Storage utilization: 41.25%"]
    # Every declared metric except the disk wait maximum, which needs its levels
    assert len(_metrics(out)) == 32


# --- check: missing or broken data -------------------------------------------------

def test_pool_gone(check, section):
    (result,) = _run(check, section, "backup")
    assert result == Result(state=State.UNKNOWN, summary="Pool backup not found")


def test_pool_with_broken_payload(check):
    section = check.parse_oposs_zpool_iostat([["tank", "{broken"]])
    (result,) = _run(check, section)
    assert result.state is State.UNKNOWN
    assert result.summary.startswith("Pool tank error: JSON parsing failed")


def test_agent_error_line(check):
    section = check.parse_oposs_zpool_iostat([["ERROR", "No pools found"], ["tank", "{}"]])
    (result,) = _run(check, section)
    assert result == Result(state=State.UNKNOWN, summary="Parse error: No pools found")

