"""The rule forms build, and every check default has a matching form field."""

import importlib.util
import json
import pathlib
import sys

import pytest
from cmk.rulesets.v1.form_specs import SimpleLevels, validators
from cmk.rulesets.v1.rule_specs import HostAndItemCondition

ROOT = pathlib.Path(__file__).resolve().parent.parent
PLUGIN = ROOT / "local/lib/python3/cmk_addons/plugins/oposs_zpool_iostat"
BAKERY = ROOT / "local/lib/python3/cmk/base/cee/plugins/bakery/oposs_zpool_iostat.py"


def _load(path, name):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


@pytest.fixture(scope="module")
def rulesets():
    return _load(PLUGIN / "rulesets/oposs_zpool_iostat.py", "test_oposs_zpool_iostat_rulesets")


@pytest.fixture(scope="module")
def bakery_rulesets():
    return _load(PLUGIN / "rulesets/oposs_zpool_iostat_bakery.py", "test_oposs_zpool_iostat_bakery_rs")


@pytest.fixture(scope="module")
def check():
    return _load(PLUGIN / "agent_based/oposs_zpool_iostat.py", "test_oposs_zpool_iostat_check_rs")


@pytest.fixture(scope="module")
def form(rulesets):
    return rulesets.rule_spec_oposs_zpool_iostat.parameter_form()


def test_check_uses_the_ruleset(rulesets, check):
    assert check.check_plugin_oposs_zpool_iostat.check_ruleset_name == rulesets.rule_spec_oposs_zpool_iostat.name


def test_ruleset_matches_items(rulesets):
    # The check has one service per pool, so the rule needs an item condition
    assert isinstance(rulesets.rule_spec_oposs_zpool_iostat.condition, HostAndItemCondition)


def test_defaults_match_form(form, check):
    assert set(check.check_plugin_oposs_zpool_iostat.check_default_parameters) == set(form.elements)


def test_every_field_is_simple_levels(form):
    assert {type(e.parameter_form) for e in form.elements.values()} == {SimpleLevels}


def test_defaults_are_simple_levels_values(check):
    for key, default in check.check_plugin_oposs_zpool_iostat.check_default_parameters.items():
        assert default == ("no_levels", None) or (default[0] == "fixed" and len(default[1]) == 2), key


def test_storage_default_matches_prefill(form, check):
    default = check.check_plugin_oposs_zpool_iostat.check_default_parameters["storage_levels"]
    assert form.elements["storage_levels"].parameter_form.prefill_fixed_levels.value == default[1]


def test_bakery_form_builds(bakery_rulesets):
    form = bakery_rulesets.rule_spec_oposs_zpool_iostat_bakery.parameter_form()
    assert set(form.elements) == {"interval", "timeout", "sampling_duration"}
    assert bakery_rulesets.rule_spec_oposs_zpool_iostat_bakery.name == "oposs_zpool_iostat"


def _baked(conf):
    bakery = _load(BAKERY, "test_oposs_zpool_iostat_bakery")
    files = list(bakery.get_oposs_zpool_iostat_files(conf))
    (config,) = [f for f in files if "lines" in f.kwargs]
    (plugin,) = [f for f in files if "lines" not in f.kwargs]
    return dict(json.loads("\n".join(config.kwargs["lines"])), interval=plugin.kwargs["interval"])


def test_bakery_writes_the_settings():
    assert _baked({"interval": 600.0, "timeout": 45.0, "sampling_duration": 20}) == {
        "interval": 600, "timeout": 45, "sampling_duration": 20}


@pytest.mark.parametrize("key", [
    "timeout",
    "interval",
    "sampling_duration",
])
def test_bakery_form_prefill_matches_bakery_default(bakery_rulesets, key):
    form = bakery_rulesets.rule_spec_oposs_zpool_iostat_bakery.parameter_form()
    assert form.elements[key].parameter_form.prefill.value == _baked({})[key]


def _minimum(spec):
    ranges = [v.range for v in (spec.custom_validate or ()) if isinstance(v, validators.NumberInRange)]
    return ranges[0][0] if ranges else None


def test_bakery_sampling_duration_has_a_minimum(bakery_rulesets):
    spec = bakery_rulesets.rule_spec_oposs_zpool_iostat_bakery.parameter_form().elements["sampling_duration"]
    minimum = _minimum(spec.parameter_form)
    assert minimum is not None and minimum >= 1


def test_bakery_timeout_has_a_minimum(bakery_rulesets):
    spec = bakery_rulesets.rule_spec_oposs_zpool_iostat_bakery.parameter_form().elements["timeout"]
    minimum = _minimum(spec.parameter_form)
    assert minimum is not None and minimum >= 1


def _form_errors(bakery_rulesets, value):
    """Run the bakery form's own validators on a rule value; return the messages."""
    form = bakery_rulesets.rule_spec_oposs_zpool_iostat_bakery.parameter_form()
    errors = []
    for validate in form.custom_validate or ():
        try:
            validate(value)
        except validators.ValidationError as exc:
            errors.append(exc.message.localize(lambda s: s))
    return errors


@pytest.mark.parametrize("value", [
    {"timeout": 10.0, "sampling_duration": 10},
    {"timeout": 5.0, "sampling_duration": 10},
    {"timeout": 20.0, "sampling_duration": 60},
    {"sampling_duration": 30},      # unset timeout bakes 30 s
    {"timeout": 10.0},              # unset sampling duration bakes 10 s
])
def test_bakery_form_refuses_timeout_not_longer_than_sampling(bakery_rulesets, value):
    (message,) = _form_errors(bakery_rulesets, value)
    assert message.startswith("The command execution timeout (")
    assert "must be longer than the zpool iostat sampling duration" in message


@pytest.mark.parametrize("value", [
    {},                                          # the defaults: 30 s and 10 s
    {"timeout": 30.0, "sampling_duration": 10},  # the prefills
    {"timeout": 11.0, "sampling_duration": 10},
    {"timeout": 90.0, "sampling_duration": 60, "interval": 600.0},
])
def test_bakery_form_accepts_timeout_longer_than_sampling(bakery_rulesets, value):
    assert _form_errors(bakery_rulesets, value) == []


def test_validator_defaults_are_the_bakery_defaults(bakery_rulesets):
    baked = _baked({})
    assert bakery_rulesets.DEFAULT_TIMEOUT == baked["timeout"]
    assert bakery_rulesets.DEFAULT_SAMPLING_DURATION == baked["sampling_duration"]
