"""Kern (Stück 1, 2, 5, 6 und 9, verschlankt): Untergrenzen LB1 und LB2, die Regel „engste Passung“ und die exakte Suche (IDA* mit Zustandsmerken).

Eine Bucht besteht aus Stapeln (Tupel von unten nach oben). Die Abrufnummer 1 kommt zuerst dran; nur der oberste Container eines Stapels ist erreichbar.
Liegt die nächste Nummer nicht oben, wird der oberste Container ihres Stapels (ein Blocker über dem Ziel) auf einen anderen Stapel mit Platz gesetzt, jeder Hub kostet 1;
die nächste Nummer wird kostenlos entnommen, sobald sie oben liegt (restricted: nur Container über dem gesuchten werden bewegt).

  lb1      Zahl der blockierenden Container (Stück 2).
  lb2      lb1 plus die Zahl der Container über dem Ziel, die größer sind als die früheste Nummer jedes anderen Stapels (Stück 9).
  greedy   die Regel „engste Passung“ (Stück 1): Kosten einer vollständigen Abarbeitung; eine obere Schranke des Optimums.
  search   exakte Suche: IDA* mit Untergrenze und Zustandsmerken (Stück 5 und 6). Knoten = Aufrufe der Suche, Summe über alle Stufen.
"""

from dataclasses import dataclass

INF = 10 ** 9


def autopop(stacks):
    """Ruft ab, was oben liegt und gerade dran ist. Gibt (neue Stapel, abgerufene Nummern in Reihenfolge) zurück."""
    st = [list(s) for s in stacks]
    popped = []
    while True:
        present = [c for s in st for c in s]
        if not present:
            return tuple(tuple(s) for s in st), popped
        t = min(present)
        for s in st:
            if s and s[-1] == t:
                s.pop()
                popped.append(t)
                break
        else:
            return tuple(tuple(s) for s in st), popped


def stack_blockers(stack):
    """Container in einem Stapel (unten nach oben), die über einem früher abzurufenden liegen."""
    total, lowest = 0, INF
    for c in stack:
        if c > lowest:
            total += 1
        else:
            lowest = c
    return total


def blocker_count(stacks):
    """Zahl der blockierenden Container (Untergrenze der Hubzahl, Stück 2)."""
    return sum(stack_blockers(s) for s in stacks)


def target_stack(stacks):
    """(nächste Abrufnummer, Index ihres Stapels). Die Bucht darf nicht leer sein."""
    t = min(c for s in stacks for c in s)
    for i, s in enumerate(stacks):
        if t in s:
            return t, i


def canon(stacks):
    """Kanonische Form: die Stapel sortiert."""
    return tuple(sorted(stacks))


def stack_min(stack):
    """Früheste Abrufnummer im Stapel; leer = unendlich."""
    return min(stack) if stack else INF


def lb1(stacks):
    return blocker_count(stacks)


def lb2(stacks):
    if not any(stacks):
        return 0
    t, i = target_stack(stacks)
    s = stacks[i]
    above = s[s.index(t) + 1:]
    others = [stack_min(x) for k, x in enumerate(stacks) if k != i]
    top = max(others) if others else -1
    return blocker_count(stacks) + sum(1 for c in above if c > top)


BOUND_FUNCS = {"LB1": lb1, "LB2": lb2}


def _fit_key(stacks, j, c):
    m = stack_min(stacks[j])
    return (0, m) if m > c else (1, -m)


def child_targets(stacks, src, height, c):
    """Zielstapel für den Blocker c (Stapel `src`, Bucht ohne c) in der Reihenfolge der engsten Passung (Stück 1); nur Stapel mit Platz."""
    dests = [j for j in range(len(stacks)) if j != src and len(stacks[j]) < height]
    dests.sort(key=lambda j: (_fit_key(stacks, j, c), j))
    return dests


def greedy(bay, height):
    """Kosten der Regel „engste Passung“ an einer Bucht; wirft ValueError, wenn ein Blocker nirgends Platz findet."""
    st, _ = autopop(bay)
    cost = 0
    while any(st):
        _, i = target_stack(st)
        lst = [list(s) for s in st]
        c = lst[i].pop()
        base = tuple(tuple(s) for s in lst)
        dests = child_targets(base, i, height, c)
        if not dests:
            raise ValueError("kein Stapel mit Platz")
        lst[dests[0]].append(c)
        st = autopop(tuple(tuple(s) for s in lst))[0]
        cost += 1
    return cost


@dataclass(frozen=True)
class SearchResult:
    optimum: int | None     # None, wenn das Knotenlimit erreicht wurde
    nodes: int              # Zahl der besuchten Knoten (bei capped: das Limit); Summe über alle Budgetstufen
    capped: bool
    stages: int             # Zahl der Budgetstufen (bei capped: die begonnenen)


class _CapReached(Exception):
    pass


class _Found(Exception):
    pass


def search(stacks, height, bound="LB2", cap=1_000_000) -> SearchResult:
    """IDA* mit der gewählten Untergrenze und Zustandsmerken (kanonisch), engste Passung zuerst."""
    lb = BOUND_FUNCS[bound]
    start = tuple(tuple(s) for s in stacks)
    budget = lb(autopop(start)[0])
    total, stages = 0, 0
    while True:
        stages += 1
        b = budget
        nodes = [0]
        table = {}
        found = []

        def rec(state, g):
            nodes[0] += 1
            if total + nodes[0] > cap:
                raise _CapReached
            st, _ = autopop(state)
            if not any(st):
                found.append(g)
                raise _Found
            if g + lb(st) > b:
                return
            key = canon(st)
            if table.get(key, INF) <= g:
                return
            table[key] = g
            _, i = target_stack(st)
            lst = [list(s) for s in st]
            c = lst[i].pop()
            base = tuple(tuple(s) for s in lst)
            for j in child_targets(base, i, height, c):
                nxt = [list(s) for s in lst]
                nxt[j].append(c)
                rec(tuple(tuple(s) for s in nxt), g + 1)

        try:
            rec(start, 0)
        except _Found:
            pass
        except _CapReached:
            return SearchResult(None, cap, True, stages)
        total += nodes[0]
        if found:
            return SearchResult(found[0], total, False, stages)
        budget += 1
