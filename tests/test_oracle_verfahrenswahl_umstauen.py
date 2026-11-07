"""Orakel-Test verfahrenswahl-umstauen-demo (ORACLE-PLAYBOOK, DEMO-PLAYBOOK §12): obere und untere Schranke gegen ANDERE Rechenwege.

Eigene, unabhängige Umsetzungen im Test: (a) das Optimum jedes Zustands per vollständiger Rekursion über alle Platzierungen (ohne Untergrenze, ohne IDA*), (b) die Regel „engste Passung“
als Auswahl über die Zielstapel mit min() statt Sortieren. Vorher an den Handzahlen geprüft: Hand-Bucht LB1 3, LB2 4, Regel 4, Optimum 4."""

import functools
import itertools

import pytest

import uvw_algorithm as A
import uvw_evaluation as ev
from uvw_scenario import make_bay

INF = 10 ** 9


def pop_all(state):
    st = [list(s) for s in state]
    while True:
        nums = [c for s in st for c in s]
        if not nums:
            return tuple(tuple(s) for s in st)
        t = min(nums)
        k = next(i for i, s in enumerate(st) if t in s)
        if st[k][-1] != t:
            return tuple(tuple(s) for s in st)
        st[k].pop()


def moves(state, height):
    nums = [c for s in state for c in s]
    t = min(nums)
    k = next(i for i, s in enumerate(state) if t in s)
    out = []
    for j in range(len(state)):
        if j != k and len(state[j]) < height:
            new = [list(s) for s in state]
            new[j].append(new[k].pop())
            out.append(pop_all(new))
    return out


@functools.lru_cache(maxsize=None)
def exact_cost(state, height):
    if not any(state):
        return 0
    return min(1 + exact_cost(tuple(sorted(n)), height) for n in moves(state, height)) if moves(state, height) else INF


def opt(bay, height):
    return exact_cost(tuple(sorted(pop_all(bay))), height)


def blockers(state):
    out = 0
    for s in state:
        lowest = INF
        for c in s:
            out += c > lowest
            lowest = min(lowest, c)
    return out


def ref_greedy(bay, height):
    """Regel „engste Passung“, eigene Auswahl: unter den Stapeln mit späterem frühestem Abruf der mit dem kleinsten, sonst der mit dem größten frühesten Abruf; leerer Stapel = unendlich;
    bei Gleichstand der kleinste Index."""
    st = pop_all(bay)
    cost = 0
    while any(st):
        nums = [c for s in st for c in s]
        t = min(nums)
        k = next(i for i, s in enumerate(st) if t in s)
        c = st[k][-1]
        cands = [(min(s) if s else INF, j) for j, s in enumerate(st) if j != k and len(s) < height]
        safe = [x for x in cands if x[0] > c]
        m, j = min(safe) if safe else (min(cands, key=lambda x: (-x[0], x[1])))
        new = [list(s) for s in st]
        new[k].pop()
        new[j].append(c)
        st = pop_all(new)
        cost += 1
    return cost


def opt_of(bay, height):
    return opt(bay, height)


def all_3x2():
    return sorted({tuple(sorted(tuple(p[i * 2:(i + 1) * 2]) for i in range(3))) for p in itertools.permutations(range(1, 7))})


def test_the_independent_optimum_matches_the_search_on_all_bays_3x2():
    bays = all_3x2()
    assert len(bays) == 120
    for bay in bays:
        assert opt(bay, 4) == A.search(bay, 4, "LB1").optimum == A.search(bay, 4, "LB2").optimum


def test_the_rule_equals_an_independent_implementation_on_many_bays():
    n = 0
    for stacks, layers, extra, seeds in ((3, 2, 2, 120), (4, 3, 2, 60), (8, 3, 2, 40), (16, 4, 1, 15), (32, 5, 2, 6), (3, 3, 1, 60)):
        for sd in range(seeds):
            bay = make_bay(stacks, layers, sd)
            assert A.greedy(bay, layers + extra) == ref_greedy(bay, layers + extra), (stacks, layers, extra, sd)
            n += 1
    assert n > 300


def test_lower_bounds_optimum_and_rule_are_ordered_on_every_bay_3x2_and_samples():
    for bay in all_3x2():
        st = pop_all(bay)
        assert A.lb1(st) == blockers(st) <= A.lb2(st) <= opt(bay, 4) <= A.greedy(bay, 4)
    for sd in range(60):
        for stacks, layers in ((4, 2), (3, 3), (4, 3)):
            bay = make_bay(stacks, layers, sd)
            st = pop_all(bay)
            assert A.lb1(st) <= A.lb2(st) <= opt(bay, layers + 2) <= A.greedy(bay, layers + 2)


def test_classify_equals_the_independent_values_and_the_status_rule():
    """Status und Optimum der Verfahrenswahl gegen die unabhängigen Teile: Regel, Zählung, Rekursion. Proven genau dann, wenn Regel = LB2 (dann Optimum = Regel), sonst Suche."""
    counts = {"proven": 0, "solved": 0}
    for stacks, layers in ((3, 2), (4, 2), (3, 3), (4, 3), (5, 3)):
        h = layers + 2
        for sd in range(30):
            bay = make_bay(stacks, layers, sd)
            rule, l1, l2, status, opt, nodes = ev.classify(bay, h, 100_000)
            st = pop_all(bay)
            assert (rule, l1) == (ref_greedy(bay, h), blockers(st))
            assert l1 <= l2 <= opt_of(bay, h) <= rule
            ref = opt_of(bay, h)
            if rule == l2:
                assert status == "proven" and opt == rule == ref and nodes == 0
                counts["proven"] += 1
            else:
                assert status == "solved" and opt == ref and nodes > 0
                counts["solved"] += 1
    assert counts["proven"] > 60 and counts["solved"] > 20


def test_classify_reports_the_node_budget_as_unsolved():
    bay = make_bay(4, 4, 23)
    rule, l1, l2, status, opt, nodes = ev.classify(bay, 6, 50)
    assert (status, opt, nodes) == ("unsolved", None, 50) and rule > l2


def test_sorted_and_trivial_bays_have_every_value_zero():
    for bay in (((2, 1), (3,)), ((2,), (1,)), ((1,),), ((3, 2), (1,))):
        assert opt(bay, 3) == A.greedy(bay, 3) == 0 and A.lb1(A.autopop(bay)[0]) == 0
