# Verfahrenswahl: Regel, Suche oder Schranke? – Streamlit-Demo

**[→ Demo live ausprobieren](https://sebastianhanisch-verfahrenswahl-umstauen-demo.streamlit.app/)**

Fünfzehntes und letztes Stück der Konzepte-Reihe **„Umstauen: Untergrenze und Suche“** für die Website „Sebastian Hanisch – Operations Research und Machine Learning“. Die Reihe hat Verfahren gebaut: die **Regel „engste Passung“**, die **Untergrenze**, die **exakte Suche**, das **ILP**, die **Spaltenformulierung** und mehr. **Welches genügt wann?** Die Demo gibt keine Gewinnerin an, sondern eine **Karte**: Sie **rechnet** an einer Bucht die Regel, die Untergrenze und die exakte Suche im gewählten **Knotenbudget**, **empfiehlt** und zeigt die **gemessene Karte** über Stapel und Lagen. Dazu die **Verfahrenskarte der ganzen Linie** mit Frage, Faustregel und Link je Stück.

## Warum dieses Problem

Am Ende einer Reihe über Verfahren steht die Frage, welches man nimmt. Die Messung gibt eine Antwort in drei Teilen. **Bei zwei Lagen** genügt die Regel: Sie ist ab 4 Stapeln in jeder gemessenen Bucht **bewiesen optimal**, weil sie der Untergrenze LB2 (Stück 9) gleicht, ganz ohne Suche. **Bei drei Lagen** trägt die **exakte Suche** bis 36 Container in jeder Bucht (höchstens 13 724 Knoten). **Bei vier und fünf Lagen** trägt sie nur bis etwa 24 beziehungsweise 20 Container zuverlässig; dahinter bleibt die **Regel mit ihrem Abstand zur Untergrenze** als einzige Garantie, und dieser Abstand ist bei vier und fünf Lagen **grob** (11 bis 64 %), obwohl die Regel dort höchstens 13 % über dem Optimum liegt. Die **Lagen** entscheiden mehr als die Stapel.

## Methode

- **Regel:** Kosten der Regel „engste Passung“ (Stück 1) an der Bucht; eine obere Schranke des Optimums.
- **Untergrenze:** LB1 = Zahl der Blocker (Stück 2), LB2 zählt die Blocker ohne sicheren Stapel mit (Stück 9). **Gleicht die Regel LB2, ist sie bewiesen optimal, ohne Suche.**
- **Exakte Suche:** IDA\* mit LB2 und Zustandsmerken (Stück 5, 6, 9) im **Knotenbudget** (10 000, 100 000 oder 1 000 000); „trägt“ heißt: Das Ergebnis kommt innerhalb des Budgets.
- **Empfehlung** in drei Zuständen: Regel bewiesen → *Regel genügt*; Suche im Budget → *exakte Suche*; sonst *nur die Regel mit Schranke* (die Regel liegt höchstens so weit über dem Optimum wie über LB2).
- **Verdikt einer Zelle:** Anteil der Buchten mit Ergebnis (bewiesen oder gelöst): mindestens 90 % „trägt“, mindestens 50 % „zum Teil“, sonst „nicht mehr“; dazu, ob der Abstand der Regel zu LB2 als Gütebeweis brauchbar ist (höchstens 15 %).
- **Live:** die Bucht, dazu eine Stichprobe von 20 Buchten bis 24 Container. **Vorberechnet** (`uvw_bands.json`, erzeugt von `generate_precomputed.py`, einige Minuten in mehreren Prozessen): die Karte über Stapel 3, 4, 5, 6, 8, 12 und Lagen 2 bis 5, je 40 feste Buchten (Platz 2, Seeds ab 0), Knotenlimit 100 000.
- Es gibt **nur Knotenzahlen, keine Zeiten**. **Keine Zahlen der anderen Stücke:** Die Verfahrenskarte nennt je Stück Frage und Faustregel in Worten und verlinkt es.

## Befunde (gemessen, keine Behauptungen)

Alle Zahlen sind Messungen an festen Buchten, nachgerechnet in `tests/test_claims.py` und `tests/test_presets.py`; die Regel gegen eine zweite Umsetzung und das Optimum gegen eine eigene Rekursion in `tests/test_oracle_verfahrenswahl_umstauen.py`.

**Die Karte** (40 Buchten je Zelle, Platz 2; „Regel = LB2“ = bewiesen optimal ohne Suche; „Suche löst“ im Knotenlimit 100 000; Knoten Median / Maximum über die Buchten mit Suche; „Regel über Optimum“ Mittel über die Buchten mit bekanntem Optimum > 0, „Regel über LB2“ Mittel über Buchten mit LB2 > 0):

| Zelle (Container) | Regel = LB1 | Regel = LB2 (bewiesen) | Suche löst | nicht entschieden | Knoten Median / Maximum | Regel über Optimum | Regel über LB2 |
|---|---|---|---|---|---|---|---|
| 3 × 2 (6) | 25 | 38 | 2 | 0 | 10 / 10 | 1,4 % | 1,4 % |
| 4 × 2 (8) | 29 | 40 | 0 | 0 | – | 0,0 % | 0,0 % |
| 5 × 2 (10) | 28 | 40 | 0 | 0 | – | 0,0 % | 0,0 % |
| 6 × 2 (12) | 29 | 40 | 0 | 0 | – | 0,0 % | 0,0 % |
| 8 × 2 (16) | 31 | 40 | 0 | 0 | – | 0,0 % | 0,0 % |
| 12 × 2 (24) | 33 | 40 | 0 | 0 | – | 0,0 % | 0,0 % |
| 3 × 3 (9) | 13 | 23 | 17 | 0 | 12 / 33 | 2,0 % | 12 % |
| 4 × 3 (12) | 11 | 27 | 13 | 0 | 18 / 135 | 0,6 % | 10 % |
| 5 × 3 (15) | 9 | 25 | 15 | 0 | 32 / 449 | 1,0 % | 8,0 % |
| 6 × 3 (18) | 12 | 27 | 13 | 0 | 26 / 394 | 0,9 % | 6,6 % |
| 8 × 3 (24) | 11 | 20 | 20 | 0 | 76,5 / 3 615 | 0,5 % | 6,7 % |
| 12 × 3 (36) | 16 | 25 | 15 | 0 | 83 / 13 724 | 0,3 % | 3,6 % |
| 3 × 4 (12) | 0 | 4 | 36 | 0 | 34,5 / 206 | 5,0 % | 39 % |
| 4 × 4 (16) | 2 | 6 | 34 | 0 | 166,5 / 2 608 | 9,6 % | 32 % |
| 5 × 4 (20) | 1 | 6 | 34 | 0 | 192,5 / 28 017 | 5,6 % | 25 % |
| 6 × 4 (24) | 1 | 5 | 34 | 1 | 672,5 / 42 643 | 3,1 % | 23 % |
| 8 × 4 (32) | 2 | 4 | 34 | 2 | 1 445,5 / 73 789 | 1,8 % | 16 % |
| 12 × 4 (48) | 1 | 7 | 14 | 19 | 1 432 / 89 467 | 0,9 % | 11 % |
| 3 × 5 (15) | 0 | 0 | 40 | 0 | 243,5 / 1 525 | 13 % | 64 % |
| 4 × 5 (20) | 0 | 0 | 40 | 0 | 730,5 / 11 224 | 12 % | 46 % |
| 5 × 5 (25) | 1 | 1 | 36 | 3 | 4 364 / 82 538 | 7,9 % | 35 % |
| 6 × 5 (30) | 0 | 1 | 26 | 13 | 19 853 / 81 402 | 7,2 % | 33 % |
| 8 × 5 (40) | 0 | 0 | 12 | 28 | 16 118,5 / 95 449 | 5,5 % | 25 % |
| 12 × 5 (60) | 0 | 1 | 5 | 34 | 20 184 / 68 958 | 2,5 % | 18 % |

- **Zwei Lagen:** ab 4 Stapeln ist die Regel in **allen 40** Buchten bewiesen optimal (bei 3 Stapeln in 38, die übrigen 2 löst die Suche mit 10 Knoten).
- **Drei Lagen:** die Regel ist in 20 bis 27 von 40 Buchten bewiesen optimal, in den übrigen löst die Suche **alle** Buchten mit höchstens 13 724 Knoten (bis 36 Container); die Regel liegt höchstens 2 % über dem Optimum.
- **Vier Lagen:** bewiesen in 4 bis 7 von 40; die Suche löst bis 20 Container alle Buchten, bei 24 und 32 Containern fehlen je 1 und 2, bei 48 Containern löst sie nur 14 von 40 (19 am Limit); die Regel liegt 1 bis 10 % über dem Optimum.
- **Fünf Lagen:** fast nie bewiesen (0 bis 1 von 40); die Suche löst bis 20 Container alle Buchten, bei 25 Containern 36, bei 30 Containern 26, bei 40 nur 12 und bei 60 nur 5 von 40; die Regel liegt 2,5 bis 13 % über dem Optimum.
- **Gütebeweis:** Der Abstand der Regel zu LB2 ist bei 2 und 3 Lagen klein (0 bis 12 %), bei 4 und 5 Lagen **grob** (11 bis 64 %), weil LB2 dort weit unter dem Optimum liegt (Stück 9).
- **Verdikte der Karte:** 20 der 24 Zellen „trägt“, 2 (4 × 12 und 6 × 5) „zum Teil“, 2 (8 × 5 und 12 × 5) „trägt nicht mehr“.

| Frage | Befund |
|---|---|
| **Genügt die Regel?** | Bei 2 Lagen ab 4 Stapeln in jeder Bucht, bewiesen. Bei 3 Lagen in 20 bis 27 von 40 bewiesen, sonst höchstens 2 % über dem Optimum. Bei 4 und 5 Lagen fast nie bewiesen und bis 13 % über dem Optimum. |
| **Trägt die exakte Suche?** | Bei 3 Lagen bis 36 Container immer; bei 4 Lagen bis 20 Container immer, bei 48 nur zur Hälfte; bei 5 Lagen bis 20 Container immer, bei 40 Containern 12 von 40. |
| **Was bleibt, wenn die Suche nicht trägt?** | Die Regel mit der Untergrenze: höchstens so viel über dem Optimum wie über LB2 (bei 5 Lagen und 40 Containern 25 %). |
| **Was zählt mehr, Stapel oder Lagen?** | Die Lagen: Zusätzliche Stapel machen die Suche größer, aber die Regel besser (Regel über Optimum sinkt mit den Stapeln); zusätzliche Lagen machen beides schwerer. |

**Presets** (Eigenschaften in `tests/test_presets.py`): „Alltag“ (4 × 3, Bucht 0: Regel 10 ist optimal, LB2 9, die Suche bestätigt mit 58 Knoten), „Zwei Lagen“ (8 × 2, Bucht 0: Regel 3 = LB2, bewiesen), „Die Suche trägt“ (6 × 3, Bucht 2: Regel 5, Optimum 4, 12 Knoten), „Die Regel braucht Hilfe“ (4 × 5, Bucht 6: Regel 25, Optimum 19, LB2 18, 640 Knoten), „Die Suche trägt nicht mehr“ (8 × 5, Bucht 0, Budget 10 000: Regel 34, LB2 28).

**Korrektur gegenüber dem Plan:** Die Zahlen stimmen mit der Vormessung überein (deterministisch). Der Plan nannte bei 4 Lagen „bei 24 und 32 Containern 34 von 35 beziehungsweise 34 von 36 gelöst“ (je Suche nötig) und die App zeigt dasselbe in der Tabelle als „Suche löst 34, nicht entschieden 1 beziehungsweise 2“.

## Ehrliche Grenzen

- **40 Buchten je Zelle:** Die Anteile sind grob; ein einzelner Eintrag („36 von 40“) kann um einige Buchten schwanken.
- **Knotenbudget statt Zeit:** „Die Suche trägt“ heißt: Das Ergebnis kommt innerhalb von 100 000 Knoten, kein Zeitbudget (Python, Einzelmessungen schwanken); mit mehr Budget trägt die Suche weiter.
- **Volle Buchten, Platz 2, restricted;** teilgefüllte Buchten, anderer Platz und andere Hubmengen verschieben die Karte.
- **Nur Regel, Untergrenze und Suche gemessen.** ILP und Spaltenformulierung (Stück 7 und 8), Vorsortieren (Stück 11), Einlagern (Stück 12), unbekannte Reihenfolgen (Stück 13) und gelernte Verzweiger (Stück 14) sind nicht Teil der Karte; ihre Fragen stehen in der Verfahrenskarte mit Link.
- **Gütebeweis über LB2** ist nur bei niedrigen Stapeln brauchbar.

## Verifikation

- **Kern:** Regel, Untergrenzen und Suche aus dem Kern von Stück 10 an Handbuchten, die Klassifikation einer Bucht von Hand (Hand-Bucht bewiesen, das Gegenbeispiel aus Stück 1 gelöst, Budget zu klein nicht entschieden), die Kennzahlen einer Zelle von Hand, Grenzfälle (LB2 gleich 0, keine Suche, kein bekanntes Optimum).
- **Orakel:** Optimum gegen eine **eigene Rekursion über alle Platzierungen** in allen 120 Buchten 3 × 2 und in Stichproben; die Regel gegen eine **zweite Umsetzung** (Auswahl über min()) in über 300 Buchten bis 32 Stapel; **Status und Optimum der Klassifikation** gegen die unabhängigen Teile in 150 Buchten (bewiesen genau dann, wenn Regel = LB2).
- **Zahlen im README:** jede Zahl der Befunde in `tests/test_claims.py` (gespeicherte Karte: 2 Lagen bewiesen, 3 Lagen ohne Limit, die Stufen bei 4 und 5 Lagen, die Spanne des Regelabstands, die Verdikt-Zustände aller 24 Zellen); vier Zellen werden frisch nachgerechnet (Knotenzahlen, keine Zeiten).
- **Verdikte:** reine Funktionen, jede Schwelle (90 %, 50 %, Gütebeweis 15 %, jeweils genau an der Grenze) und jede genannte Zahl an von Hand gesetzten Werten (`tests/test_verdicts.py`).
- **Presets und Oberfläche:** AppTest-Rauchtest (jeder Button, jeder Regler an Minimum und Maximum), Inhalt (Kennzahlen je Preset, Kartenzeilen, Verfahrenskarte mit 14 Links), Layout, Footer, Laufzeit-Importe, Abbildungen (Karten als Heatmaps, gesperrte Achsen).

## Dateistruktur

| Datei | Zweck |
|---|---|
| `.github/workflows/tests.yml` | CI: Push, Pull Request, wöchentlicher Canary |
| `.gitignore` | venv, Caches, Streamlit-Secrets |
| `.streamlit/config.toml` | Streamlit-Einstellungen (keine Nutzungsstatistik) |
| `app.py` | Streamlit-App (Aufbau nach DEMO-PLAYBOOK §2) |
| `generate_precomputed.py` | erzeugt `uvw_bands.json` (die Karte) |
| `requirements-dev.txt` | Laufzeit plus pytest |
| `requirements.txt` | Laufzeit-Bibliotheken (ungepinnt): streamlit, plotly |
| `uvw_algorithm.py` | LB1, LB2, die Regel „engste Passung“ und die exakte Suche |
| `uvw_bands.json` | die vorberechnete Karte |
| `uvw_constants.py` | Regler-Stufen, Limits, Schwellen, Farben, Presets, die Verfahrenskarte der Linie |
| `uvw_evaluation.py` | Klassifikation einer Bucht, Zellen, Verdikte (reine Funktionen) |
| `uvw_layout.py` | Fester Kopf (Stylesheet) |
| `uvw_presets.py` | Permalink (auf Stufen gerückt), Presets (Schnellstart in der Seitenleiste), Zufalls-Seed-Button |
| `uvw_scenario.py` | Buchten (volle Buchten) |
| `uvw_visualization.py` | Plotly-Abbildungen (Karten als Heatmaps, Achsen gesperrt) |
| `tests/` | Handrechnung, Orakel, Randfälle, Behauptungen, Verdikte, Presets, Abbildungen, AppTest, Layout, Footer, Laufzeit-Importe |

## Bewusst nicht umgesetzt

- **Ein gemeinsamer Vergleich mit ILP und Spaltenformulierung** auf demselben Kern (ihre Zahlen stehen in den Stücken 7 und 8).
- **Eine Zeitmessung:** nur Knoten.
- **PDF-Export:** nicht vorgesehen.

## Lokal ausführen

```bash
python3 -m venv venv
source venv/bin/activate          # Windows: venv\Scripts\activate

pip install -r requirements.txt
streamlit run app.py
```

## Tests ausführen

```bash
pip install -r requirements-dev.txt
pytest tests/ -v
```

86 Tests, rund zwei Minuten.

Gebaut mit Streamlit und Plotly.

---

Diese Demo ist Teil des Portfolios von [Sebastian Hanisch](https://sebastianhanisch.net) – Operations Research und Machine Learning ([Über mich](https://sebastianhanisch.net/ueber-mich.html)). Mehr zu den Demos: [Interaktive Demos](https://sebastianhanisch.net/demos.html).
