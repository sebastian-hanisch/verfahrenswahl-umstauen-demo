"""Konstanten: Regler-Grenzen, feste Annahmen, Farben, Presets und die Verfahrenskarte der Linie."""

STACK_OPTIONS = (3, 4, 5, 6, 8, 12)                       # Zahl der Stapel (Stufen des Reglers)
DEFAULT_STACKS = 4
LAYERS_MIN, LAYERS_MAX, DEFAULT_LAYERS = 2, 5, 3          # Anfangsfüllung je Stapel (Lagen)
EXTRA_MIN, EXTRA_MAX, DEFAULT_EXTRA = 1, 3, 2             # Platz: Höchsthöhe = Lagen + Zuschlag (Standard 2 wie in Stück 1 bis 14)
BUDGET_OPTIONS = (10_000, 100_000, 1_000_000)             # Knotenbudget der exakten Suche (Stufen des Reglers)
DEFAULT_BUDGET = 100_000
DEFAULT_SEED = 0
SEED_MAX = 999999

SAMPLE_BAYS = 20                                          # Stichprobe live: so viele Buchten
SAMPLE_MAX_CONTAINERS = 24                                # die Stichprobe wird live nur bis zu dieser Containerzahl gerechnet

# Zellen der vorberechneten Karte: Stapel (STACK_OPTIONS) × Lagen 2 bis 5, Platz 2, Seeds ab 0
KARTE_LAYERS = (2, 3, 4, 5)
KARTE_BAYS = 40
KARTE_BUDGET = 100_000                                    # Knotenlimit der Suche in der Vorberechnung

# Schwellen der Verdikte
CARRY_GOOD = 0.9                                          # „die Suche trägt“: Anteil der Buchten mit Ergebnis (bewiesen oder gelöst) mindestens so groß
CARRY_OK = 0.5                                            # „zum Teil“; darunter „trägt nicht“
GAP_GOOD = 0.15                                           # Abstand der Regel zu LB2 (Mittel) bis hier: brauchbarer Gütebeweis; darüber grob

COLOR_CELL = "#7a8fa6"
COLOR_BLOCK = "#b5545a"        # blockierend (liegt über einem früher abzurufenden)
COLOR_TARGET = "#2F6B65"       # nächster Abruf
COLOR_SCALE = [[0.0, "#b5545a"], [0.5, "#e8d9a8"], [1.0, "#2F6B65"]]      # schlecht … gut (für die Karte „trägt“)
COLOR_SCALE_REV = [[0.0, "#2F6B65"], [0.5, "#e8d9a8"], [1.0, "#b5545a"]]  # gut … schlecht (für die Karte „Regel über Optimum“: wenig ist gut)

# Presets (Eigenschaften in tests/test_presets.py)
PRESETS = {
    "Alltag (4 Stapel, 3 Lagen)": {"stacks": 4, "layers": 3, "extra": DEFAULT_EXTRA, "budget": 100_000, "seed": 0},
    "Zwei Lagen (8 Stapel, 2 Lagen)": {"stacks": 8, "layers": 2, "extra": DEFAULT_EXTRA, "budget": 100_000, "seed": 0},
    "Die Suche trägt (6 Stapel, 3 Lagen)": {"stacks": 6, "layers": 3, "extra": DEFAULT_EXTRA, "budget": 100_000, "seed": 2},
    "Die Regel braucht Hilfe (4 Stapel, 5 Lagen)": {"stacks": 4, "layers": 5, "extra": DEFAULT_EXTRA, "budget": 100_000, "seed": 6},
    "Die Suche trägt nicht mehr (8 Stapel, 5 Lagen)": {"stacks": 8, "layers": 5, "extra": DEFAULT_EXTRA, "budget": 10_000, "seed": 0},
}
PRESET_HELP = {
    "Alltag (4 Stapel, 3 Lagen)": "12 Container: Die Regel (10 Hübe) ist schon optimal, die Untergrenze LB2 liegt bei 9; die exakte Suche bestätigt es mit 58 Knoten.",
    "Zwei Lagen (8 Stapel, 2 Lagen)": "16 Container: Die Regel gleicht der Untergrenze (LB2) und ist damit ohne jede Suche bewiesen optimal.",
    "Die Suche trägt (6 Stapel, 3 Lagen)": "18 Container: Die Regel (5 Hübe) ist nicht bewiesen und nicht optimal (Optimum 4); die exakte Suche findet es mit 12 Knoten.",
    "Die Regel braucht Hilfe (4 Stapel, 5 Lagen)": "20 Container: Die Regel kostet 25 Hübe, das Optimum ist 19 (LB2: 18); die Suche löst die Bucht mit 640 Knoten.",
    "Die Suche trägt nicht mehr (8 Stapel, 5 Lagen)": "40 Container, Knotenbudget 10 000: Die Suche bricht ab, es bleibt die Regel mit ihrem Abstand zur Untergrenze.",
}

# Die Verfahrenskarte der Linie: (Stück, Name, Frage, Faustregel, Repo-Name). Die Faustregeln fassen die Befunde der Stücke in Worten zusammen (ohne deren Zahlen).
METHODS = (
    (1, "Zielstapel wählen", "Wohin mit dem Blocker, wenn man die Abrufreihenfolge kennt?", "Die Regel „engste Passung“ ist billig und meist nahe am Optimum; es gibt Gegenbeispiele.", "umstauen-regeln-demo"),
    (2, "Untergrenze", "Wie viele Hübe sind mindestens nötig?", "Die Zahl der Blocker beweist die Regel optimal, wo sie sie trifft; die Lücke wächst mit den Lagen.", "untergrenze-umstauen-demo"),
    (3, "Restricted gegen unrestricted", "Was bringt die Freiheit, auch andere Container umzulagern?", "Bei niedrigen Stapeln nichts, bei hohen etwas; die Lücke zur Untergrenze schließt sie nur zum kleinen Teil.", "umlagern-freiheit-demo"),
    (4, "Tiefensuche", "Wie schnell explodiert die Suche?", "Ohne Untergrenze schnell; die Schranke aus der besten Lösung hilft mehr als die Reihenfolge der Kinder.", "knotenexplosion-umstauen-demo"),
    (5, "IDA* mit Untergrenze", "Wie macht die Untergrenze die Suche klein?", "Die Untergrenze spart den Großteil der Knoten; das Wachstum bleibt exponentiell.", "iterative-vertiefung-umstauen-demo"),
    (6, "Gleiche Zustände", "Wie viele Konfigurationen sind gleich?", "Das Merken gleicher Zustände spart vor allem Mehrfachwege und ersetzt sich zum Teil mit der Untergrenze.", "gleiche-zustaende-umstauen-demo"),
    (7, "ILP-Modell", "Wo bricht das Modell ein?", "Korrekt, aber groß und mit schwerem Schwanz; die Suche trägt deutlich weiter.", "ilp-modell-umstauen-demo"),
    (8, "Spaltenformulierung", "Trägt die Spaltenformulierung?", "Die Schranke ist nie schwächer und oft stärker, aber der Stapelgraph wächst schnell.", "stapelgraph-spalten-umstauen-demo"),
    (9, "Schärfere Untergrenzen", "Wie schließt man die Lücke von Stück 2?", "Blocker ohne sicheren Stapel mitzählen ist der beste Tausch; weitere Schärfe kostet je Knoten mehr, als sie spart.", "schaerfere-untergrenzen-umstauen-demo"),
    (10, "Asymptotik", "Wird die einfache Untergrenze bei vielen Stapeln scharf?", "Im Verhältnis ja, absolut bei hohen Stapeln nicht.", "stapelzahl-asymptotik-umstauen-demo"),
    (11, "Pre-Marshalling", "Wie sortiert man vor dem Abruf mit wenig Hüben um?", "Geht nur mit genug freien Plätzen und kostet mehr Hübe als das Umlagern beim Abruf.", "vorsortieren-umstauen-demo"),
    (12, "Einlagern", "Was ist eine Abfahrtsschätzung wert, wenn man sie nur zum Einlagern hat?", "Bei kleinem Schätzfehler fast das volle Wissen wert, bei großem nichts.", "einlagern-schaetzung-umstauen-demo"),
    (13, "Unbekannte Abrufreihenfolge", "Was ist frühe Information wert?", "In kleinen Buchten schließen schon wenige vorab bekannte Abrufe den größten Teil der Lücke; bei 5 Stapeln und mehr braucht es deutlich mehr.", "abrufreihenfolge-unbekannt-umstauen-demo"),
    (14, "Gelernter Verzweiger", "Wann lohnt Lernen, wenn die Untergrenze schon da ist?", "Eine bessere Reihenfolge kann im Wesentlichen nur den Fund verkürzen, nicht den Beweis; die Regel wählt meist ein optimales Kind zuerst, lässt aber gegenüber einem perfekten Orakel noch einen Teil der Knoten liegen.", "gelernter-verzweiger-umstauen-demo"),
)
