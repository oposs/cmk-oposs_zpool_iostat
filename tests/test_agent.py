"""Tests for the agent plugin (runs on the monitored host)."""

import json
import re
import subprocess
from importlib.machinery import SourceFileLoader
from importlib.util import module_from_spec, spec_from_loader
from pathlib import Path

import pytest
import zpool_samples as zs

ROOT = Path(__file__).resolve().parent.parent
AGENT = ROOT / "local/share/check_mk/agents/plugins/oposs_zpool_iostat"
BAKERY = ROOT / "local/lib/python3/cmk/base/cee/plugins/bakery/oposs_zpool_iostat.py"

# The field names the agent sends for the full OpenZFS 2.x layout; the check
# plugin reads exactly these keys.
FIELDS_ZFS_2 = [
    "pool", "alloc", "free", "read_ops", "write_ops", "read_bytes", "write_bytes",
    "read_wait", "write_wait", "disk_read_wait", "disk_write_wait",
    "syncq_read_wait", "syncq_write_wait", "asyncq_read_wait", "asyncq_write_wait",
    "scrub_wait", "trim_wait", "rebuild_wait",
    "syncq_read_pend", "syncq_read_activ", "syncq_write_pend", "syncq_write_activ",
    "asyncq_read_pend", "asyncq_read_activ", "asyncq_write_pend", "asyncq_write_activ",
    "scrubq_read_pend", "scrubq_read_activ", "trimq_write_pend", "trimq_write_activ",
    "rebuildq_write_pend", "rebuildq_write_activ",
]
FIELDS_ZFS_08 = [f for f in FIELDS_ZFS_2 if not f.startswith("rebuild")]


def _load(path, name):
    loader = SourceFileLoader(name, str(path))
    module = module_from_spec(spec_from_loader(loader.name, loader))
    loader.exec_module(module)
    return module


@pytest.fixture
def agent(tmp_path, monkeypatch):
    module = _load(AGENT, "oposs_zpool_iostat_agent")
    # Never read the host's baked settings
    monkeypatch.setattr(module, "CONFIG_FILE", str(tmp_path / "unbaked" / Path(module.CONFIG_FILE).name))
    return module


def _fake_run(rows, layout=zs.ZFS_2, calls=None, header_rc=0, data_rc=0):
    """A subprocess.run replacement answering the two zpool iostat calls."""

    def run(cmd, **kwargs):
        if calls is not None:
            calls.append((cmd, kwargs))
        if "-ylpq" in cmd:
            return subprocess.CompletedProcess(cmd, header_rc, stdout=zs.table(rows, layout),
                                               stderr="" if header_rc == 0 else "no pools available\n")
        if "-Hylpq" in cmd:
            return subprocess.CompletedProcess(cmd, data_rc, stdout=zs.scripted(rows),
                                               stderr="" if data_rc == 0 else "interval cannot be zero\n")
        raise AssertionError(f"unexpected command {cmd}")

    return run


def _records(capsys):
    lines = capsys.readouterr().out.splitlines()
    assert lines[0] == "<<<oposs_zpool_iostat:sep(124)>>>"
    out = {}
    for line in lines[1:]:
        name, payload = line.split("|", 1)
        out[name] = json.loads(payload)
    return out


# --- header parsing ------------------------------------------------------------

def test_header_names_for_openzfs_2():
    lines = zs.header(["tank"])
    assert zs.columns() + 1 == len(FIELDS_ZFS_2)
    assert _load(AGENT, "a").parse_headers(lines[0], lines[1]) == FIELDS_ZFS_2


def test_header_names_for_openzfs_08_without_rebuild_columns():
    lines = zs.header(["tank"], zs.ZFS_08)
    assert _load(AGENT, "a").parse_headers(lines[0], lines[1]) == FIELDS_ZFS_08


def test_header_names_with_a_long_pool_name():
    # The name column grows with the longest pool name and shifts every label
    lines = zs.header(["backup-pool-on-the-jbod"])
    assert _load(AGENT, "a").parse_headers(lines[0], lines[1]) == FIELDS_ZFS_2


def test_header_names_without_parsable_widths():
    # The 5 wide columns of a run without -p, where "rebuild" overhangs its column
    lines = zs.header(["tank"], literal=False)
    assert lines[0].startswith("              capacity     operations     bandwidth")
    assert _load(AGENT, "a").parse_headers(lines[0], lines[1]) == FIELDS_ZFS_2


# --- full agent run ------------------------------------------------------------

def test_agent_reports_every_pool(agent, monkeypatch, capsys):
    monkeypatch.setattr(agent.subprocess, "run", _fake_run([("tank", zs.TANK), ("rpool", zs.RPOOL)]))
    agent.main()
    data = _records(capsys)
    assert list(data) == ["tank", "rpool"]
    tank = data["tank"]
    assert list(tank) == FIELDS_ZFS_2
    assert tank["pool"] == "tank"
    assert tank["alloc"] == 3298534883328
    assert tank["free"] == 4698694819840
    assert tank["read_ops"] == 152
    assert tank["write_bytes"] == 52428800
    assert tank["read_wait"] == 2412345          # nanoseconds, converted by the check
    assert tank["asyncq_write_pend"] == 12
    assert tank["asyncq_write_activ"] == 4


def test_idle_latency_dash_becomes_zero(agent, monkeypatch, capsys):
    monkeypatch.setattr(agent.subprocess, "run", _fake_run([("rpool", zs.RPOOL)]))
    agent.main()
    rpool = _records(capsys)["rpool"]
    assert rpool["read_wait"] == 0
    assert rpool["write_wait"] == 312000
    assert rpool["scrub_wait"] == 0
    assert rpool["rebuild_wait"] == 0


def test_agent_on_openzfs_08(agent, monkeypatch, capsys):
    values = [v for i, v in enumerate(zs.TANK) if FIELDS_ZFS_2[i + 1] in FIELDS_ZFS_08]
    monkeypatch.setattr(agent.subprocess, "run", _fake_run([("tank", values)], zs.ZFS_08))
    agent.main()
    tank = _records(capsys)["tank"]
    assert list(tank) == FIELDS_ZFS_08
    assert tank["trimq_write_activ"] == 0
    assert tank["asyncq_write_pend"] == 12


def test_pool_name_with_spaces_and_dots(agent, monkeypatch, capsys):
    # zpool create allows space, dot, colon, dash and underscore in a name
    monkeypatch.setattr(agent.subprocess, "run", _fake_run([("data pool.v2", zs.TANK)]))
    agent.main()
    assert _records(capsys)["data pool.v2"]["read_ops"] == 152


def test_unparsable_value_becomes_zero(agent):
    fields = ["pool", "alloc", "read_ops"]
    assert agent.parse_iostat_output("tank\t12G\t7", fields) == {
        "tank": {"pool": "tank", "alloc": 0, "read_ops": 7}}


def test_short_lines_are_skipped(agent):
    fields = ["pool", "alloc", "free"]
    assert agent.parse_iostat_output("\ntank\t1\n\nrpool\t1\t2\n", fields) == {
        "rpool": {"pool": "rpool", "alloc": 1, "free": 2}}


# --- failures ------------------------------------------------------------------

def _failed_run(agent, capsys):
    with pytest.raises(SystemExit) as exc:
        agent.main()
    out = capsys.readouterr()
    # The section header still goes out, the reason goes to stderr
    assert out.out.splitlines() == ["<<<oposs_zpool_iostat:sep(124)>>>"]
    assert exc.value.code == 1
    return out.err


def test_header_call_fails(agent, monkeypatch, capsys):
    monkeypatch.setattr(agent.subprocess, "run", _fake_run([("tank", zs.TANK)], header_rc=1))
    err = _failed_run(agent, capsys)
    assert "zpool iostat (headers) failed with code 1: no pools available" in err


def test_data_call_fails(agent, monkeypatch, capsys):
    monkeypatch.setattr(agent.subprocess, "run", _fake_run([("tank", zs.TANK)], data_rc=2))
    err = _failed_run(agent, capsys)
    assert "zpool iostat failed with code 2: interval cannot be zero" in err


def test_zpool_missing(agent, monkeypatch, capsys):
    def run(cmd, **kwargs):
        raise FileNotFoundError(cmd[0])
    monkeypatch.setattr(agent.subprocess, "run", run)
    assert "zpool command not found" in _failed_run(agent, capsys)


def test_zpool_times_out(agent, monkeypatch, capsys):
    def run(cmd, **kwargs):
        raise subprocess.TimeoutExpired(cmd, kwargs["timeout"])
    monkeypatch.setattr(agent.subprocess, "run", run)
    assert "timed out after 30 seconds" in _failed_run(agent, capsys)


def test_no_pools(agent, monkeypatch, capsys):
    monkeypatch.setattr(agent.subprocess, "run", _fake_run([]))
    assert "No pools found" in _failed_run(agent, capsys)


# --- configuration written by the agent bakery ---------------------------------

@pytest.fixture
def bakery():
    return _load(BAKERY, "oposs_zpool_iostat_bakery")


def _baked_config(bakery, conf):
    files = list(bakery.get_oposs_zpool_iostat_files(conf))
    (config,) = [f for f in files if "lines" in f.kwargs]
    return config.kwargs["target"], config.kwargs["lines"]


def test_agent_uses_the_baked_settings(agent, bakery, monkeypatch, tmp_path, capsys):
    target, lines = _baked_config(bakery, {"timeout": 45.0, "sampling_duration": 20, "interval": 600.0})
    (tmp_path / target).write_text("\n".join(lines))
    monkeypatch.setattr(agent, "CONFIG_FILE", str(tmp_path / target))
    calls = []
    monkeypatch.setattr(agent.subprocess, "run", _fake_run([("tank", zs.TANK)], calls=calls))
    agent.main()
    assert [c[0] for c in calls] == [
        ["/sbin/zpool", "iostat", "-ylpq", "1", "1"],
        ["/sbin/zpool", "iostat", "-Hylpq", "20", "1"],
    ]
    assert [c[1]["timeout"] for c in calls] == [45, 45]


def test_unbaked_defaults(agent, monkeypatch, capsys):
    calls = []
    monkeypatch.setattr(agent.subprocess, "run", _fake_run([("tank", zs.TANK)], calls=calls))
    agent.main()
    assert calls[1][0][-2:] == ["10", "1"]
    assert [c[1]["timeout"] for c in calls] == [30, 30]


def test_broken_config_file_falls_back_to_defaults(agent, monkeypatch, tmp_path):
    broken = tmp_path / "oposs_zpool_iostat.json"
    broken.write_text("{not json")
    monkeypatch.setattr(agent, "CONFIG_FILE", str(broken))
    assert agent.get_config() == {}


def test_bakery_deploys_the_plugin_with_its_interval(bakery):
    files = list(bakery.get_oposs_zpool_iostat_files({"interval": 600.0}))
    (plugin,) = [f for f in files if "lines" not in f.kwargs]
    assert plugin.kwargs["source"] == Path("oposs_zpool_iostat")
    assert plugin.kwargs["interval"] == 600


def test_bakery_without_rule_deploys_nothing(bakery):
    assert list(bakery.get_oposs_zpool_iostat_files(None)) == []


# --- version -----------------------------------------------------------------

def _released_version():
    """The newest released heading of CHANGES.md, the version the publish
    check expects in every version_files target between releases."""
    return re.search(r"^## (\d+\.\d+\.\d+)", (ROOT / "CHANGES.md").read_text(),
                     flags=re.MULTILINE).group(1)


def test_agent_carries_the_released_version():
    # The publish check fails on main when a version file disagrees with
    # the newest released CHANGES.md heading.
    assert re.search(rf'^__version__ = "{re.escape(_released_version())}"$',
                     AGENT.read_text(), flags=re.MULTILINE)


def test_release_writes_version_into_agent(tmp_path):
    """Apply the version_files entry of .github/repo-infra.json to a copy of
    the agent, as Create release PR does (a multiline regex, first match)"""
    config = json.loads((ROOT / ".github/repo-infra.json").read_text())
    (spec,) = [f for f in config["version_files"] if Path(f["path"]).name == AGENT.name]
    stamped = re.sub(spec["pattern"], spec["replacement"].replace("$VERSION", "9.8.7"),
                     AGENT.read_text(), count=1, flags=re.MULTILINE)
    assert re.search(spec["verify"].replace("$VERSION", re.escape("9.8.7")), stamped, flags=re.MULTILINE)
    copy = tmp_path / "oposs_zpool_iostat"
    copy.write_text(stamped)
    assert _load(copy, "stamped_agent").__version__ == "9.8.7"


def test_agent_is_executable_in_git():
    # The Checkmk agent skips plugins without the executable bit; the MKP
    # build takes the mode from git.
    out = subprocess.run(["git", "ls-files", "-s", AGENT.name], cwd=AGENT.parent,
                         capture_output=True, text=True, check=True).stdout
    assert out.split()[0] == "100755"
