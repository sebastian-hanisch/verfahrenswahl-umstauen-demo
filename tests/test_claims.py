"""Aussagen der Demo und des READMEs gegen die vorberechnete Karte und gegen eine frische Nachrechnung kleiner Zellen (DEMO-PLAYBOOK §5, §12).

Alle Größen sind deterministisch (feste Seeds, Knotenzahlen, keine Zeiten) und müssen bei der Nachrechnung gleich sein."""

import pytest

import uvw_constants as C
import uvw_evaluation as ev


def K(s, l):
    return ev.key(s, l)


def _karte():
    return ev.load_bands()["karte"]


def test_the_stored_cells_cover_exactly_the_grid_of_the_constants():
    k = _karte()
    assert set(k) == {K(s, l) for s in C.STACK_OPTIONS for l in C.KARTE_LAYERS} and all(c["n"] == C.KARTE_BAYS == 40 for c in k.values())
    for c in k.values():
        assert c["proven"] + c["solved"] + c["unsolved"] == c["n"] and c["rule_eq_lb1"] <= c["proven"] + c["solved"] + c["unsolved"]


def test_two_layers_the_rule_is_proven_optimal_in_every_bay_from_four_stacks():
    k = _karte()
    assert all(k[K(s, 2)]["proven"] == 40 and k[K(s, 2)]["excess"] == 0.0 for s in (4, 5, 6, 8, 12)) and k[K(3, 2)]["proven"] == 38 and k[K(3, 2)]["solved"] == 2


def test_three_layers_the_search_solves_every_bay_up_to_36_containers():
    k = _karte()
    for s in C.STACK_OPTIONS:
        c = k[K(s, 3)]
        assert c["unsolved"] == 0 and 20 <= c["proven"] <= 27 and c["nodes_max"] <= 13724 and round(c["excess"], 3) <= 0.02
    assert k[K(12, 3)]["nodes_max"] == 13724 and [k[K(s, 3)]["proven"] for s in C.STACK_OPTIONS] == [23, 27, 25, 27, 20, 25]


def test_four_and_five_layers_the_search_carries_less_and_the_rule_gap_to_lb2_is_coarse():
    k = _karte()
    assert [k[K(s, 4)]["unsolved"] for s in C.STACK_OPTIONS] == [0, 0, 0, 1, 2, 19] and k[K(12, 4)]["solved"] == 14
    assert [k[K(s, 5)]["solved"] for s in C.STACK_OPTIONS] == [40, 40, 36, 26, 12, 5] and [k[K(s, 5)]["unsolved"] for s in C.STACK_OPTIONS] == [0, 0, 3, 13, 28, 34]
    gaps = [k[K(s, l)]["gap_lb2"] for s in C.STACK_OPTIONS for l in (4, 5)]
    assert round(min(gaps), 2) == 0.11 and round(max(gaps), 2) == 0.64                                       # der Regelabstand zu LB2 liegt bei 4 und 5 Lagen zwischen 11 und 64 %
    assert max(k[K(s, l)]["excess"] for s in C.STACK_OPTIONS for l in (4, 5)) < 0.14 and round(k[K(3, 5)]["excess"], 3) == 0.132


def test_the_verdict_states_of_the_map_the_readme_quotes():
    k = _karte()
    states = {key: ev.verdict_cell(c, key)[0] for key, c in k.items()}
    assert sorted(key for key, v in states.items() if v == "warning") == ["12,5", "8,5"]
    assert sorted(key for key, v in states.items() if v == "info") == ["12,4", "6,5"] and sum(1 for v in states.values() if v == "success") == 20


@pytest.mark.parametrize("stacks,layers", [(3, 2), (3, 3), (4, 4), (6, 3)])
def test_a_fresh_recomputation_of_cells_reproduces_the_stored_band(stacks, layers):
    fresh = ev.cell_stats(ev.bay_rows(stacks, layers, C.DEFAULT_EXTRA, range(C.KARTE_BAYS), C.KARTE_BUDGET))
    assert fresh == _karte()[K(stacks, layers)]
