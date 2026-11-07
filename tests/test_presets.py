"""Presets: jede Einstellung hat die Eigenschaft, für die sie steht (DEMO-PLAYBOOK §12), und die Hilfetexte nennen nur gemessene Zahlen."""

import pytest

import uvw_constants as C
import uvw_evaluation as ev
import uvw_presets as P


def _analyse(name):
    p = C.PRESETS[name]
    return ev.analyse(ev.Settings(p["stacks"], p["layers"], p["extra"], p["budget"], p["seed"]))


def test_every_preset_is_inside_the_slider_bounds_and_on_a_step_and_has_help():
    for name, p in C.PRESETS.items():
        for key, state_key in P.PRESET_KEYS.items():
            lo, hi = P.bounds(state_key)
            assert lo <= p[key] <= hi and P.snap(state_key, p[key]) == p[key], (name, key)
    assert set(C.PRESET_HELP) == set(C.PRESETS) and all(C.PRESET_HELP.values())


def test_everyday_bay_the_rule_is_optimal_but_only_the_search_proves_it():
    a = _analyse("Alltag (4 Stapel, 3 Lagen)")
    assert (a.status, a.rule, a.lb1, a.lb2, a.optimum, a.nodes) == ("solved", 10, 7, 9, 10, 58) and ev.verdict_bay(a)[0] == "success"


def test_two_layers_bay_is_proven_by_the_rule():
    a = _analyse("Zwei Lagen (8 Stapel, 2 Lagen)")
    assert (a.status, a.rule, a.lb2, a.optimum, a.nodes, a.containers) == ("proven", 3, 3, 3, 0, 16) and ev.verdict_bay(a)[0] == "success"


def test_the_search_carries_bay():
    a = _analyse("Die Suche trägt (6 Stapel, 3 Lagen)")
    assert (a.status, a.rule, a.lb2, a.optimum, a.nodes) == ("solved", 5, 3, 4, 12) and a.rule > a.optimum and ev.verdict_bay(a)[0] == "info"


def test_the_rule_needs_help_bay():
    a = _analyse("Die Regel braucht Hilfe (4 Stapel, 5 Lagen)")
    assert (a.status, a.rule, a.lb1, a.lb2, a.optimum, a.nodes) == ("solved", 25, 15, 18, 19, 640) and round(a.rule / a.optimum - 1, 2) == 0.32


def test_the_search_does_not_carry_bay():
    a = _analyse("Die Suche trägt nicht mehr (8 Stapel, 5 Lagen)")
    assert (a.status, a.optimum, a.nodes, a.rule, a.lb2, a.containers) == ("unsolved", None, 10_000, 34, 28, 40) and ev.verdict_bay(a)[0] == "warning"


def test_the_default_settings_are_the_first_preset():
    assert {s: P.SETTING_SPECS[s].default for s in P.SETTING_SPECS} == {"stacks_slider": 4, "layers_slider": 3, "extra_slider": 2, "budget_slider": 100_000, "seed_input": 0}
    assert next(iter(C.PRESETS.values())) == {"stacks": 4, "layers": 3, "extra": 2, "budget": 100_000, "seed": 0}


def test_the_methods_table_covers_stueck_1_to_14_with_unique_repos():
    assert [m[0] for m in C.METHODS] == list(range(1, 15)) and len({m[4] for m in C.METHODS}) == 14
    assert all(len(m) == 5 and all(m) for m in C.METHODS) and C.METHODS[10][4] == "vorsortieren-umstauen-demo" and C.METHODS[13][1] == "Gelernter Verzweiger"


@pytest.mark.parametrize("name", list(C.PRESETS))
def test_apply_preset_writes_every_setting(name, monkeypatch):
    state = {}
    monkeypatch.setattr(P.st, "session_state", state)
    P.apply_preset(name)
    assert {k: state[sk] for k, sk in P.PRESET_KEYS.items()} == {k: C.PRESETS[name][k] for k in P.PRESET_KEYS}
    assert P.aktives_preset() == name
