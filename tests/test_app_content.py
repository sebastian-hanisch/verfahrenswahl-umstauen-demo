"""Inhalt der App an festen Fällen (DEMO-PLAYBOOK §12): was im Ergebnis, in den Tabellen und in den Verdikten steht."""

from pathlib import Path

import pytest
from streamlit.testing.v1 import AppTest

APP = str(Path(__file__).resolve().parent.parent / "app.py")


def _run(preset=None):
    at = AppTest.from_file(APP, default_timeout=300)
    at.run()
    assert not at.exception, [str(e) for e in at.exception]
    if preset:
        at.sidebar.button(key=f"preset_{preset}").click().run()
        assert not at.exception, [str(e) for e in at.exception]
    return at


def _text(at):
    return "\n".join(e.value for kind in (at.markdown, at.caption, at.info, at.success, at.warning) for e in kind)


def _metrics(at):
    return {m.label: (m.value, m.delta) for m in at.metric}


def test_default_page_has_the_sections_and_the_default_result():
    at = _run()
    subs = [s.value for s in at.subheader]
    assert [s for s in subs if s.startswith("🔬")] == ["🔬 Experiment: Die eigene Zelle live", "🔬 Experiment: Die gemessene Karte"]
    assert "🗺️ Die Verfahrenskarte der Linie" in subs and "🚧 Wo die Annahmen enden" in subs
    m = _metrics(at)
    assert m["Regel"][0] == "10" and m["Untergrenze LB2"] == ("9", "LB1: 7") and m["Exakte Suche"] == ("10", "58 Knoten, Budget 100 000") and m["Container"] == ("12", "Höchsthöhe 5")
    assert any(s.value.startswith("**Exakte Suche.** Sie löst die Bucht mit 58 Knoten (Budget 100 000): Optimum 10. Die Regel (10) war schon optimal") for s in at.success)


def test_default_page_map_table_and_verdict_quote_the_stored_numbers():
    text = _text(_run())
    assert "| 3 × 2 (6) | 25 | 38 | 2 | 0 | 10 / 10 | 1,4 % | 1,4 % |" in text and "| 12 × 3 (36) | 16 | 25 | 15 | 0 | 83 / 13 724 | 0,3 % | 3,6 % |" in text
    assert "| 12 × 5 (60) | 0 | 1 | 5 | 34 | 20 184 / 68 958 | 2,5 % | 18 % |" in text and "| 8 × 4 (32) | 2 | 4 | 34 | 2 | 1 445,5 / 73 789 | 1,8 % | 16 % |" in text
    assert ("4 × 3: In 27 von 40 Buchten ist die Regel bewiesen optimal, in 13 löst die Suche, in 0 bleibt sie am Limit. Die Regel liegt im Mittel 0,6 % über dem Optimum und 10 % über LB2: "
            "als Gütebeweis ist LB2 hier brauchbar. Die exakte Suche trägt hier.") in text


def test_methods_table_lists_all_fourteen_pieces_with_links():
    text = _text(_run())
    assert "| 11 | [Pre-Marshalling](https://sebastianhanisch-vorsortieren-umstauen-demo.streamlit.app/) |" in text and "| 14 | [Gelernter Verzweiger](https://sebastianhanisch-gelernter-verzweiger-umstauen-demo.streamlit.app/) |" in text
    assert text.count("streamlit.app/) |") == 14


def test_sample_for_the_default_cell_is_computed_live():
    text = _text(_run())
    assert "20 Buchten ab der Bucht-Nummer 0 (Platz 2), Knotenbudget 100 000." in text and "4 × 3, Stichprobe: In " in text


def test_two_layers_preset_shows_the_rule_is_enough():
    at = _run("Zwei Lagen (8 Stapel, 2 Lagen)")
    assert _metrics(at)["Exakte Suche"] == ("nicht nötig", "Regel = LB2") and any(s.value.startswith("**Regel genügt.**") for s in at.success)


def test_the_search_does_not_carry_preset_shows_the_warning_and_no_sample():
    at = _run("Die Suche trägt nicht mehr (8 Stapel, 5 Lagen)")
    assert _metrics(at)["Exakte Suche"] == ("nicht entschieden", "10 000 Knoten, Budget 10 000") and any(w.value.startswith("**Nur die Regel mit Schranke.**") for w in at.warning)
    text = _text(at)
    assert "wird live nur bis 24 Container gerechnet; 8 × 5 hat 40." in text and "8 × 5: In 0 von 40 Buchten ist die Regel bewiesen optimal, in 12 löst die Suche, in 28 bleibt sie am Limit." in text


@pytest.mark.parametrize("extra,budget", [(1, 10_000), (3, 1_000_000)])
def test_other_platz_and_budget_are_noted_and_do_not_crash(extra, budget):
    at = _run()
    at.sidebar.slider(key="extra_slider").set_value(extra).run()
    at.sidebar.select_slider(key="budget_slider").set_value(budget).run()
    assert not at.exception and "Die Karte gilt für Platz 2 und 100 000 Knoten" in _text(at)
