"""Kennzahlen, Verdikt-Logik, vorberechnete Karte. Reine Funktionen: die App ruft st.<Art>(Text), die Tests prüfen jede Zahl und jede Schwelle."""

import json
from dataclasses import dataclass
from decimal import ROUND_HALF_UP, Decimal
from pathlib import Path
from statistics import mean, median

import uvw_algorithm as A
import uvw_constants as C
from uvw_scenario import make_bay, max_height

BANDS_FILE = Path(__file__).resolve().parent / "uvw_bands.json"


@dataclass(frozen=True)
class Settings:
    stacks: int = C.DEFAULT_STACKS
    layers: int = C.DEFAULT_LAYERS
    extra: int = C.DEFAULT_EXTRA
    budget: int = C.DEFAULT_BUDGET
    seed: int = C.DEFAULT_SEED


@dataclass(frozen=True)
class Analysis:
    bay: tuple
    height: int
    containers: int
    budget: int
    rule: int               # Kosten der Regel „engste Passung“
    lb1: int
    lb2: int
    status: str             # "proven" (Regel = LB2, keine Suche), "solved" (Suche im Budget), "unsolved" (Budget erreicht)
    optimum: int | None     # bei proven die Kosten der Regel, bei solved das Optimum, sonst None
    nodes: int              # Knoten der Suche (0 bei proven; bei unsolved das Budget)

    @property
    def gap_lb2(self) -> float | None:
        """Regel über LB2 (relativ), None bei LB2 = 0."""
        return None if self.lb2 == 0 else self.rule / self.lb2 - 1


def classify(bay, height: int, budget: int):
    """(Regel, LB1, LB2, Status, Optimum, Knoten) einer Bucht: gleicht die Regel LB2, ist sie bewiesen optimal; sonst die exakte Suche im Knotenbudget."""
    st = A.autopop(bay)[0]
    rule, l1, l2 = A.greedy(bay, height), A.lb1(st), A.lb2(st)
    if rule == l2:
        return rule, l1, l2, "proven", rule, 0
    r = A.search(bay, height, "LB2", budget)
    if r.optimum is None:
        return rule, l1, l2, "unsolved", None, r.nodes
    return rule, l1, l2, "solved", r.optimum, r.nodes


def analyse(settings: Settings) -> Analysis:
    height = max_height(settings.layers, settings.extra)
    bay = make_bay(settings.stacks, settings.layers, settings.seed)
    return Analysis(bay, height, settings.stacks * settings.layers, settings.budget, *classify(bay, height, settings.budget))


# ---------------------------------------------------------------- Formate

def num(n: int) -> str:
    """Ganze Zahl mit Leerzeichen als Tausendertrenner."""
    return f"{n:,}".replace(",", " ")


def _half_up(x: float, digits: int) -> str:
    """Kaufmännisch gerundet (…5 rundet auf) mit `digits` Nachkommastellen."""
    d = Decimal(repr(round(float(x), 9))).quantize(Decimal(1).scaleb(-digits), rounding=ROUND_HALF_UP)
    return f"{d:.{digits}f}"


def num_f(x: float) -> str:
    """Zahl mit Leerzeichen als Tausendertrenner; mit Nachkommaanteil (Median einer geraden Zahl) eine Nachkommastelle mit Komma."""
    x = round(float(x), 6)
    if x.is_integer():
        return num(int(x))
    whole, frac = _half_up(x, 1).split(".")
    return f"{num(int(whole))},{frac}"


def percent_text(x: float) -> str:
    """Anteil als Prozent: unter 10 % mit einer Nachkommastelle, sonst ganzzahlig (Komma)."""
    p = x * 100
    return (_half_up(p, 1) if abs(p) < 10 else _half_up(p, 0)).replace(".", ",") + " %"


def _ge(x: float, limit: float) -> bool:
    """x >= limit mit Toleranz für Gleitkommarauschen."""
    return round(x, 9) >= limit


def _le(x: float, limit: float) -> bool:
    return round(x, 9) <= limit


# ---------------------------------------------------------------- Empfehlung für eine Bucht

def verdict_bay(a: Analysis) -> tuple[str, str]:
    """Empfehlung für die Bucht in drei Zuständen: Regel genügt (bewiesen), exakte Suche trägt, nur Regel mit Schranke."""
    if a.status == "proven":
        return "success", (f"**Regel genügt.** Sie kostet {a.rule} Hübe und gleicht der Untergrenze LB2 ({a.lb2}): bewiesen optimal, ohne jede Suche.")
    if a.status == "solved":
        if a.optimum == a.rule:
            return "success", (f"**Exakte Suche.** Sie löst die Bucht mit {num(a.nodes)} Knoten (Budget {num(a.budget)}): Optimum {a.optimum}. Die Regel ({a.rule}) war schon optimal, "
                               f"bewiesen ist das erst durch die Suche (Untergrenze LB2 {a.lb2}).")
        gap = a.rule / a.optimum - 1
        tail = f", die Untergrenze LB2 ({a.lb2}) {percent_text(a.optimum / a.lb2 - 1)} darunter" if a.lb2 else ""
        return "info", f"**Exakte Suche.** Sie löst die Bucht mit {num(a.nodes)} Knoten (Budget {num(a.budget)}): Optimum {a.optimum}. Die Regel ({a.rule}) liegt {percent_text(gap)} darüber{tail}."
    gap = a.gap_lb2
    gap_text = "mehr als eine Untergrenze von 0" if gap is None else f"höchstens {percent_text(gap)} über dem Optimum"
    return "warning", (f"**Nur die Regel mit Schranke.** Die exakte Suche kommt im Budget von {num(a.budget)} Knoten nicht zum Ziel. Die Regel kostet {a.rule} Hübe, die Untergrenze LB2 liegt bei "
                       f"{a.lb2}: die Regel liegt {gap_text}.")


def result_rows(a: Analysis) -> list[dict]:
    """Zeilen der Ergebnistabelle."""
    rows = [{"name": "Regel „engste Passung“ (Stück 1)", "value": str(a.rule), "effort": "kein Suchaufwand"},
            {"name": "Untergrenze LB1 (Blocker, Stück 2)", "value": str(a.lb1), "effort": "–"},
            {"name": "Untergrenze LB2 (Stück 9)", "value": str(a.lb2), "effort": "–"}]
    if a.status == "proven":
        rows.append({"name": "Exakte Suche (Stück 5 bis 9)", "value": f"{a.optimum} (bewiesen durch Regel = LB2)", "effort": "nicht nötig"})
    elif a.status == "solved":
        rows.append({"name": "Exakte Suche (Stück 5 bis 9)", "value": str(a.optimum), "effort": f"{num(a.nodes)} Knoten (Budget {num(a.budget)})"})
    else:
        rows.append({"name": "Exakte Suche (Stück 5 bis 9)", "value": "nicht entschieden", "effort": f"Budget {num(a.budget)} Knoten erreicht"})
    return rows


# ---------------------------------------------------------------- Stichproben

def key(stacks: int, layers: int) -> str:
    return f"{stacks},{layers}"


def bay_rows(stacks: int, layers: int, extra: int, seeds, budget: int) -> list[dict]:
    """Je Bucht: Regel, LB1, LB2, Status, Optimum (None, wenn nicht entschieden), Knoten."""
    height = max_height(layers, extra)
    out = []
    for sd in seeds:
        rule, l1, l2, status, opt, nodes = classify(make_bay(stacks, layers, sd), height, budget)
        out.append({"seed": sd, "rule": rule, "lb1": l1, "lb2": l2, "status": status, "opt": opt, "nodes": nodes})
    return out


def cell_stats(rows: list[dict]) -> dict:
    """Je Zelle: Buchten, Regel = LB1, bewiesen (Regel = LB2), gelöst (Suche), nicht entschieden, Knoten (Median, Maximum über die gelösten Buchten mit Suche), Regel über Optimum
    (Mittel über gelöste und bewiesene Buchten mit Optimum > 0), Regel über LB2 (Mittel über Buchten mit LB2 > 0)."""
    n = len(rows)
    searched = [r for r in rows if r["status"] == "solved"]
    known = [r for r in rows if r["opt"] and r["opt"] > 0]
    with_lb2 = [r for r in rows if r["lb2"] > 0]
    return {"n": n, "rule_eq_lb1": sum(1 for r in rows if r["rule"] == r["lb1"]), "proven": sum(1 for r in rows if r["status"] == "proven"), "solved": len(searched),
            "unsolved": sum(1 for r in rows if r["status"] == "unsolved"), "nodes_median": float(median(r["nodes"] for r in searched)) if searched else None,
            "nodes_max": max((r["nodes"] for r in searched), default=None), "excess": mean((r["rule"] - r["opt"]) / r["opt"] for r in known) if known else None,
            "gap_lb2": mean(r["rule"] / r["lb2"] - 1 for r in with_lb2) if with_lb2 else None}


def sample_stats(settings: Settings):
    """Stichprobe live (SAMPLE_BAYS Buchten ab der Bucht-Nummer) bis SAMPLE_MAX_CONTAINERS Container; sonst None."""
    if settings.stacks * settings.layers > C.SAMPLE_MAX_CONTAINERS:
        return None
    return cell_stats(bay_rows(settings.stacks, settings.layers, settings.extra, range(settings.seed, settings.seed + C.SAMPLE_BAYS), settings.budget))


def share_ok(stats: dict) -> float:
    """Anteil der Buchten mit Ergebnis (bewiesen oder gelöst)."""
    return (stats["proven"] + stats["solved"]) / stats["n"]


def load_bands() -> dict:
    """Vorberechnete Karte, erzeugt von generate_precomputed.py: {"karte": {"s,l": cell_stats}}."""
    return json.loads(BANDS_FILE.read_text(encoding="utf-8"))


# ---------------------------------------------------------------- Verdikt einer Zelle

def verdict_cell(stats: dict, name: str) -> tuple[str, str]:
    """Verdikt „was trägt in dieser Zelle?“: Anteil der Buchten mit Ergebnis, dazu Regelabstand zu Optimum und LB2."""
    n = stats["n"]
    share = share_ok(stats)
    text = (f"{name}: In {stats['proven']} von {n} Buchten ist die Regel bewiesen optimal, in {stats['solved']} löst die Suche, in {stats['unsolved']} bleibt sie am Limit.")
    if stats["excess"] is not None and stats["gap_lb2"] is not None:
        grob = "brauchbar" if _le(stats["gap_lb2"], C.GAP_GOOD) else "grob"
        text += (f" Die Regel liegt im Mittel {percent_text(stats['excess'])} über dem Optimum und {percent_text(stats['gap_lb2'])} über LB2: als Gütebeweis ist LB2 hier {grob}.")
    if _ge(share, C.CARRY_GOOD):
        return "success", text + " Die exakte Suche trägt hier."
    if _ge(share, C.CARRY_OK):
        return "info", text + " Die exakte Suche trägt hier nur zum Teil."
    return "warning", text + " Die exakte Suche trägt hier nicht mehr."
