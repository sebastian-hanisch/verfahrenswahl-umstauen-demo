"""Verdikte an von Hand gesetzten Werten (DEMO-PLAYBOOK §12): jede Zahl im Text und jede Schwelle der Art steht hier."""

import uvw_constants as C
import uvw_evaluation as ev


def _a(status, rule=15, lb1=10, lb2=12, opt=None, nodes=0, budget=100_000):
    return ev.Analysis(((1,),), 5, 20, budget, rule, lb1, lb2, status, opt, nodes)


def test_bay_verdict_three_states_and_numbers():
    kind, text = ev.verdict_bay(_a("proven", 3, 3, 3, 3))
    assert kind == "success" and text == "**Regel genügt.** Sie kostet 3 Hübe und gleicht der Untergrenze LB2 (3): bewiesen optimal, ohne jede Suche."
    kind, text = ev.verdict_bay(_a("solved", 25, 15, 18, 19, 640))
    assert kind == "info" and text == ("**Exakte Suche.** Sie löst die Bucht mit 640 Knoten (Budget 100 000): Optimum 19. Die Regel (25) liegt 32 % darüber, die Untergrenze LB2 (18) 5,6 % darunter.")
    kind, text = ev.verdict_bay(_a("solved", 15, 10, 12, 15, 812))
    assert kind == "success" and text == ("**Exakte Suche.** Sie löst die Bucht mit 812 Knoten (Budget 100 000): Optimum 15. Die Regel (15) war schon optimal, bewiesen ist das erst durch die Suche "
                                          "(Untergrenze LB2 12).")
    kind, text = ev.verdict_bay(_a("unsolved", 34, 25, 28, None, 10_000, 10_000))
    assert kind == "warning" and text == ("**Nur die Regel mit Schranke.** Die exakte Suche kommt im Budget von 10 000 Knoten nicht zum Ziel. Die Regel kostet 34 Hübe, die Untergrenze LB2 liegt bei 28: "
                                          "die Regel liegt höchstens 21 % über dem Optimum.")


def test_bay_verdict_with_lb2_zero():
    kind, text = ev.verdict_bay(_a("unsolved", 3, 0, 0, None, 5, 5))
    assert kind == "warning" and "mehr als eine Untergrenze von 0" in text
    kind, text = ev.verdict_bay(_a("solved", 4, 1, 0, 3, 7))
    assert kind == "info" and text == "**Exakte Suche.** Sie löst die Bucht mit 7 Knoten (Budget 100 000): Optimum 3. Die Regel (4) liegt 33 % darüber."


def test_result_rows_by_hand():
    rows = ev.result_rows(_a("solved", 25, 15, 18, 19, 640))
    assert [r["name"] for r in rows] == ["Regel „engste Passung“ (Stück 1)", "Untergrenze LB1 (Blocker, Stück 2)", "Untergrenze LB2 (Stück 9)", "Exakte Suche (Stück 5 bis 9)"]
    assert rows[0]["value"] == "25" and rows[3] == {"name": "Exakte Suche (Stück 5 bis 9)", "value": "19", "effort": "640 Knoten (Budget 100 000)"}
    assert ev.result_rows(_a("proven", 3, 3, 3, 3))[3] == {"name": "Exakte Suche (Stück 5 bis 9)", "value": "3 (bewiesen durch Regel = LB2)", "effort": "nicht nötig"}
    assert ev.result_rows(_a("unsolved", budget=10_000))[3] == {"name": "Exakte Suche (Stück 5 bis 9)", "value": "nicht entschieden", "effort": "Budget 10 000 Knoten erreicht"}


def _stats(proven, solved, unsolved, excess=0.05, gap=0.1, n=None):
    n = n or proven + solved + unsolved
    return {"n": n, "rule_eq_lb1": 0, "proven": proven, "solved": solved, "unsolved": unsolved, "nodes_median": 10.0, "nodes_max": 100, "excess": excess, "gap_lb2": gap}


def test_cell_verdict_three_states_and_numbers():
    kind, text = ev.verdict_cell(_stats(4, 36, 0, 0.05, 0.394), "4 × 3")
    assert kind == "success" and text == ("4 × 3: In 4 von 40 Buchten ist die Regel bewiesen optimal, in 36 löst die Suche, in 0 bleibt sie am Limit. Die Regel liegt im Mittel 5,0 % über dem Optimum "
                                          "und 39 % über LB2: als Gütebeweis ist LB2 hier grob. Die exakte Suche trägt hier.")
    kind, text = ev.verdict_cell(_stats(7, 14, 19, 0.009, 0.113), "4 × 12")
    assert kind == "info" and text.endswith("Die exakte Suche trägt hier nur zum Teil.") and "als Gütebeweis ist LB2 hier brauchbar" in text
    assert "Bei den ungelösten Buchten ist das Optimum unbekannt; der Wert gilt nur für die übrigen und ist eher zu niedrig." in text                          # Hinweis nur bei ungelösten Buchten
    assert "ungelösten" not in ev.verdict_cell(_stats(4, 36, 0, 0.05, 0.394), "4 × 3")[1]
    kind, text = ev.verdict_cell(_stats(0, 12, 28, 0.055, 0.246), "5 × 8")
    assert kind == "warning" and text.endswith("Die exakte Suche trägt hier nicht mehr.")


def test_cell_verdict_thresholds_are_inclusive():
    assert ev.verdict_cell(_stats(0, 36, 4), "x")[0] == "success" and C.CARRY_GOOD == 0.9                # genau 90 % zählt als „trägt“
    assert ev.verdict_cell(_stats(0, 35, 5), "x")[0] == "info"
    assert ev.verdict_cell(_stats(0, 20, 20), "x")[0] == "info" and C.CARRY_OK == 0.5                    # genau 50 % zählt als „zum Teil“
    assert ev.verdict_cell(_stats(0, 19, 21), "x")[0] == "warning"
    assert "hier brauchbar" in ev.verdict_cell(_stats(10, 0, 0, gap=0.15), "x")[1] and C.GAP_GOOD == 0.15      # genau 15 % ist noch brauchbar
    assert "hier grob" in ev.verdict_cell(_stats(10, 0, 0, gap=0.151), "x")[1]


def test_cell_verdict_without_excess_leaves_out_the_sentence():
    text = ev.verdict_cell(_stats(10, 0, 0, excess=None, gap=None), "2 × 4")[1]
    assert text == "2 × 4: In 10 von 10 Buchten ist die Regel bewiesen optimal, in 0 löst die Suche, in 0 bleibt sie am Limit. Die exakte Suche trägt hier."
