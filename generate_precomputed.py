"""Erzeugt uvw_bands.json: die Karte der Verfahrenswahl (Stapel x Lagen, Platz 2, Seeds ab 0).

    python generate_precomputed.py

"karte": je Zelle (STACK_OPTIONS x KARTE_LAYERS, KARTE_BAYS Buchten) cell_stats: Regel = LB1, bewiesen (Regel = LB2), gelöst, nicht entschieden, Knoten, Regel über Optimum und über LB2.

Rechenzeit einige Minuten (die Zellen mit 4 und 5 Lagen und vielen Stapeln sind die langsamsten; die Zellen laufen in getrennten Prozessen). Dieselben Funktionen wie die Tests
(`uvw_evaluation.bay_rows`, `cell_stats`); die Datei speichert nur Kennzahlen, keine Zeilen."""

import json
import os
import sys
from concurrent.futures import ProcessPoolExecutor, as_completed

import uvw_constants as C
import uvw_evaluation as ev

sys.stdout.reconfigure(encoding="utf-8")


def job(stacks, layers):
    return ev.key(stacks, layers), ev.cell_stats(ev.bay_rows(stacks, layers, C.DEFAULT_EXTRA, range(C.KARTE_BAYS), C.KARTE_BUDGET))


def main():
    tasks = [(s, l) for l in reversed(C.KARTE_LAYERS) for s in reversed(C.STACK_OPTIONS)]        # die langsamen zuerst
    out = {"karte": {}}
    with ProcessPoolExecutor(max_workers=max(2, (os.cpu_count() or 4) - 2)) as pool:
        futures = {pool.submit(job, *t): t for t in tasks}
        for fut in as_completed(futures):
            k, stats = fut.result()
            out["karte"][k] = stats
            print("Zelle", k, "fertig", flush=True)
    with open("uvw_bands.json", "w", encoding="utf-8") as f:
        json.dump(out, f, ensure_ascii=False, indent=1, sort_keys=True)
    print("geschrieben: uvw_bands.json", flush=True)


if __name__ == "__main__":
    main()
