"""Abbildungen an synthetischen Daten: Werte, Farben, gesperrte Achsen (DEMO-PLAYBOOK §12)."""

import plotly.graph_objects as go
import pytest

import uvw_constants as C
import uvw_visualization as V


def _locked(fig):
    return fig.layout.xaxis.fixedrange is True and fig.layout.yaxis.fixedrange is True


def _karte(missing=()):
    out = {}
    for s in C.STACK_OPTIONS:
        for l in C.KARTE_LAYERS:
            if (s, l) in missing:
                continue
            out[f"{s},{l}"] = {"n": 40, "proven": 40 if l == 2 else 4, "solved": 0 if l == 2 else 20, "unsolved": 0 if l == 2 else 16, "excess": None if l == 2 else 0.01 * l * 4 / s}
    return out


def test_blocker_cells_and_the_bay_chart(hand):
    assert V.blocker_cells(((1, 5), (2, 3), (4, 6))) == {(0, 1), (1, 1), (2, 1)}
    fig = V.build_bay(hand[0], 4, target=1)
    assert _locked(fig) and len(fig.data) == 4 and list(fig.data[0].marker.color) == [C.COLOR_TARGET, C.COLOR_CELL, C.COLOR_CELL] and [s.y0 for s in fig.layout.shapes] == [4]


def test_carry_map_shows_percent_with_results_per_cell():
    fig = V.build_carry(_karte())
    h = fig.data[0]
    assert [c[0] for c in h.colorscale] == [0.0, 0.5, 1.0] and h.colorscale[0][1] == C.COLOR_BLOCK and h.colorscale[2][1] == C.COLOR_TARGET        # wenig ist schlecht (rot), viel gut (grün)
    assert _locked(fig) and isinstance(h, go.Heatmap) and list(h.x) == ["3", "4", "5", "6", "8", "12"] and list(h.y) == ["2 Lagen", "3 Lagen", "4 Lagen", "5 Lagen"]
    assert list(h.z[0]) == [100.0] * 6 and list(h.z[1]) == [60.0] * 6 and h.zmin == 0 and h.zmax == 100                     # 2 Lagen: alle bewiesen; sonst (4 + 20) / 40
    assert h.text[0][0] == "100 %" and h.text[3][5] == "60 %" and fig.layout.yaxis.autorange == "reversed"


def test_excess_map_leaves_out_cells_without_a_value_and_marks_missing_cells_empty():
    fig = V.build_excess(_karte(missing=((12, 5),)))
    h = fig.data[0]
    assert _locked(fig) and list(h.z[0]) == [None] * 6 and h.zmax == 15
    assert [c[0] for c in h.colorscale] == [0.0, 0.5, 1.0] and h.colorscale[0][1] == C.COLOR_TARGET and h.colorscale[2][1] == C.COLOR_BLOCK      # wenig ist gut (grün), viel schlecht (rot)
    assert h.z[3][-1] is None and h.text[3][-1] == "" and h.z[3][0] == pytest.approx(100 * 0.01 * 5 * 4 / 3) and h.text[3][0] == "6.7 %"


def test_both_maps_are_plotly_figures():
    assert all(isinstance(f, go.Figure) for f in (V.build_bay(((1,),), 2), V.build_carry(_karte()), V.build_excess(_karte())))
