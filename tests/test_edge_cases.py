"""Randfälle, an denen Kernroutinen erfahrungsgemäß brechen (DEMO-PLAYBOOK §12)."""

import pytest

import uvw_algorithm as A
import uvw_constants as C
import uvw_evaluation as ev
import uvw_presets as P


def _row(seed, rule, lb1, lb2, status, opt, nodes=0):
    return {"seed": seed, "rule": rule, "lb1": lb1, "lb2": lb2, "status": status, "opt": opt, "nodes": nodes}


def test_classify_by_hand(hand, counter):
    assert ev.classify(*hand, 1000) == (4, 3, 4, "proven", 4, 0)                                   # Regel = LB2: bewiesen optimal ohne Suche
    rule, l1, l2, status, opt, nodes = ev.classify(*counter, 1000)
    assert (rule, l1, l2, status, opt) == (5, 3, 4, "solved", 4) and nodes == 10                    # das Gegenbeispiel aus Stück 1: die Regel braucht 5, das Optimum ist 4
    assert ev.classify(*counter, 3)[3:] == ("unsolved", None, 3)                                    # Budget von 3 Knoten: nicht entschieden
    assert ev.classify(((2, 1), (3,)), 3, 10) == (0, 0, 0, "proven", 0, 0)                          # schon sortiert: Regel = LB2 = 0


def test_cell_stats_by_hand():
    rows = [_row(0, 4, 3, 4, "proven", 4), _row(1, 5, 3, 4, "solved", 4, 10), _row(2, 6, 4, 5, "solved", 5, 30), _row(3, 9, 7, 8, "unsolved", None, 100), _row(4, 0, 0, 0, "proven", 0)]
    s = ev.cell_stats(rows)
    assert (s["n"], s["rule_eq_lb1"], s["proven"], s["solved"], s["unsolved"]) == (5, 1, 2, 2, 1)
    assert s["nodes_median"] == 20.0 and s["nodes_max"] == 30
    assert s["excess"] == pytest.approx((0 + 0.25 + 0.2) / 3)                                       # Regel über Optimum: nur Buchten mit Optimum > 0 (die sortierte und die offene fehlen)
    assert s["gap_lb2"] == pytest.approx((0 + 0.25 + 0.2 + 0.125) / 4)                              # Regel über LB2: nur Buchten mit LB2 > 0
    assert ev.share_ok(s) == pytest.approx(4 / 5)


def test_cell_stats_without_searches_or_known_optima():
    s = ev.cell_stats([_row(0, 0, 0, 0, "proven", 0), _row(1, 7, 5, 6, "unsolved", None, 100)])
    assert s["nodes_median"] is None and s["nodes_max"] is None and s["excess"] is None and s["gap_lb2"] == pytest.approx(7 / 6 - 1)
    all_zero = ev.cell_stats([_row(0, 0, 0, 0, "proven", 0)])
    assert all_zero["excess"] is None and all_zero["gap_lb2"] is None and ev.share_ok(all_zero) == 1.0


def test_analysis_by_hand_and_the_gap_property():
    a = ev.analyse(ev.Settings(8, 2, 2, 100_000, 0))
    assert (a.status, a.rule, a.lb2, a.optimum, a.nodes, a.containers, a.height) == ("proven", 3, 3, 3, 0, 16, 4)
    assert a.gap_lb2 == 0.0
    b = ev.analyse(ev.Settings(4, 5, 2, 100_000, 6))
    assert (b.status, b.rule, b.lb1, b.lb2, b.optimum, b.nodes) == ("solved", 25, 15, 18, 19, 640) and b.gap_lb2 == pytest.approx(25 / 18 - 1)
    c = ev.analyse(ev.Settings(8, 5, 2, 10_000, 0))
    assert (c.status, c.optimum, c.nodes, c.rule, c.lb2) == ("unsolved", None, 10_000, 34, 28)
    zero = ev.Analysis(((),), 3, 1, 10, 0, 0, 0, "proven", 0, 0)
    assert zero.gap_lb2 is None


def test_sample_stats_only_up_to_the_container_limit():
    small = ev.sample_stats(ev.Settings(6, 4, 2, 10_000, 0))                                       # 24 Container: gerechnet
    assert small is not None and small["n"] == C.SAMPLE_BAYS == 20 and C.SAMPLE_MAX_CONTAINERS == 24
    assert ev.sample_stats(ev.Settings(8, 4, 2, 10_000, 0)) is None                                # 32 Container: nicht live
    assert small["proven"] + small["solved"] + small["unsolved"] == 20


def test_snap_moves_values_to_the_nearest_step_or_the_bounds():
    assert P.snap("stacks_slider", 7) == 6 and P.snap("stacks_slider", 10) == 8 and P.snap("stacks_slider", 11) == 12 and P.snap("stacks_slider", 100) == 12 and P.snap("stacks_slider", 1) == 3
    assert P.snap("budget_slider", 50_000) == 10_000 and P.snap("budget_slider", 60_000) == 100_000 and P.snap("budget_slider", 10 ** 9) == 1_000_000
    assert P.snap("layers_slider", 9) == 5 and P.snap("extra_slider", 0) == 1 and P.snap("seed_input", -3) == 0


def test_number_formats():
    assert ev.num(5) == "5" and ev.num(1000000) == "1 000 000" and ev.num_f(34.5) == "34,5" and ev.num_f(76.0) == "76" and ev.num_f(1445.5) == "1 445,5"
    assert ev.percent_text(0.014) == "1,4 %" and ev.percent_text(0.396) == "40 %" and ev.percent_text(0.0625) == "6,3 %" and ev.percent_text(0.0) == "0,0 %"
    assert ev.key(4, 3) == "4,3"
    assert A.greedy(((1, 5), (2, 3), (4, 6)), 4) == 4
