"""Untergrenzen, Regel und Suche gegen Handrechnung (DEMO-PLAYBOOK §1b und §12)."""

import pytest

import uvw_algorithm as A
from uvw_scenario import make_bay


def test_autopop_target_stack_and_blockers():
    assert A.autopop(((1,), (2,))) == (((), ()), [1, 2])
    assert A.autopop(((2, 1), (3,))) == (((), ()), [1, 2, 3])
    st, popped = A.autopop(((7, 1, 4), (2, 3, 9), (6, 5, 8)))
    assert st == ((7, 1, 4), (2, 3, 9), (6, 5, 8)) and popped == []
    assert A.target_stack(st) == (1, 0) and A.blocker_count(st) == 4 and A.stack_blockers((2, 3, 9)) == 2
    assert A.stack_min(()) == A.INF and A.stack_min((7, 1, 4)) == 1 and A.canon(((3,), (1,))) == ((1,), (3,))


def test_bounds_by_hand(hand, counter):
    bay, _ = hand
    assert A.lb1(bay) == 3 and A.lb2(bay) == 4
    bay, _ = counter
    assert A.lb1(bay) == 3 and A.lb2(bay) == 4
    assert A.lb2(((1, 3), (2, 4), (5, 6))) == A.lb1(((1, 3), (2, 4), (5, 6)))            # die 3 ist kleiner als 5: sicher auf Stapel 3
    assert A.lb2(((1, 5), (2,), ())) == A.lb1(((1, 5), (2,), ()))                        # ein leerer Stapel ist immer sicher
    assert A.lb2(((1, 6, 5), (2, 3), (4, 7))) == A.lb1(((1, 6, 5), (2, 3), (4, 7))) + 2   # über der 1: 5 und 6, beide größer als die Minima 2 und 4
    assert A.lb2(()) == 0 and A.lb2(((),)) == 0


def test_greedy_by_hand(hand, counter):
    assert A.greedy(*hand) == 4 == A.search(*hand).optimum
    assert A.greedy(*counter) == 5 and A.search(*counter).optimum == 4                   # die Regel verfehlt das Optimum (Stück 1)
    assert A.greedy(((2, 1), (3,)), 3) == 0 and A.greedy(((3, 2, 1),), 3) == 0


def test_greedy_is_an_upper_bound_and_lb1_a_lower_bound_on_many_bays():
    for sd in range(30):
        bay = make_bay(3, 3, sd)
        opt = A.search(bay, 5).optimum
        assert A.lb1(A.autopop(bay)[0]) <= A.lb2(A.autopop(bay)[0]) <= opt <= A.greedy(bay, 5)


def test_greedy_refuses_a_bay_without_room():
    with pytest.raises(ValueError):
        A.greedy(((1, 5), (2, 3)), 2)                                                    # beide Stapel voll: die 5 findet keinen Platz


def test_child_targets_follow_the_tightest_fit_and_respect_capacity():
    base = ((), (2, 3), (4,), (5, 6, 7, 8))                                              # Stapel 4 ist bei Höchsthöhe 4 voll
    assert A.child_targets(base, 0, 4, 1) == [1, 2]                                      # Blocker 1: Stapel 2 (Minimum 2) vor Stapel 3 (Minimum 4)
    assert A.child_targets(base, 1, 4, 9) == [0, 2]                                      # Blocker 9: nur der leere Stapel ist sicher
    wide = ((9,), (), (4,), (2, 3))
    assert A.child_targets(wide, 0, 5, 1) == [3, 2, 1] and A.child_targets(wide, 0, 5, 3) == [2, 1, 3]


def test_search_with_both_bounds_finds_the_same_optimum(hand, counter):
    for bay, h in (hand, counter):
        r1, r2 = A.search(bay, h, "LB1"), A.search(bay, h, "LB2")
        assert r1.optimum == r2.optimum == 4 and not r1.capped and not r2.capped
    assert (A.search(*hand, "LB1").stages, A.search(*hand, "LB2").stages) == (2, 1)       # LB1 startet bei 3 und braucht ein Budget mehr


def test_search_returns_no_optimum_at_the_node_limit():
    r = A.search(((1, 6, 7, 8), (2, 3), (4, 5)), 4, "LB1", cap=3)
    assert r.optimum is None and r.capped and r.nodes == 3
    assert A.search(((1, 6, 7, 8), (2, 3), (4, 5)), 4, "LB1").optimum == 8


@pytest.mark.parametrize("sd", range(5))
def test_search_agrees_between_the_bounds_on_random_bays(sd):
    bay = make_bay(3, 3, sd)
    assert A.search(bay, 5, "LB1").optimum == A.search(bay, 5, "LB2").optimum
