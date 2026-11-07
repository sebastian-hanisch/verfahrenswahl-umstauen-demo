"""Gemeinsame Fixtures: die Buchten, an denen jede Einheit von Hand geprüft wird (DEMO-PLAYBOOK §1b)."""

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))


@pytest.fixture
def hand():
    """Die Bucht von Hand: (1, 5), (2, 3), (4, 6), Höchsthöhe 4 (von unten nach oben). Blocker: 5, 3 und 6, also LB1 = 3; die 5 hat keinen sicheren Stapel (Minima 2 und 4): LB2 = 4.
    Regel „engste Passung“: die 5 auf Stapel 3 (größtes Minimum unter den unsicheren), dann die 3 auf Stapel 3 (Minimum 4: sicher, engste Passung), nach dem Abruf der 4 die 5 und die 6
    auf die leeren Stapel: 4 Hübe = Optimum 4."""
    return ((1, 5), (2, 3), (4, 6)), 4


@pytest.fixture
def counter():
    """Das Gegenbeispiel aus Stück 1: (3, 6), (2, 4), (1, 5), Höchsthöhe 4. LB1 = 3, LB2 = 4 = Optimum; die Regel braucht 5."""
    return ((3, 6), (2, 4), (1, 5)), 4
