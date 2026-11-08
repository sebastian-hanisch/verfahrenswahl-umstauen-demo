"""Verfahrenswahl beim Umstauen: Regel, exakte Suche oder Schranke, gemessen woran? - interaktive Konzept-Demo
Sebastian Hanisch - Operations Research und Machine Learning

Stück 15 der Reihe „Umstauen: Untergrenze und Suche“ (Abschluss). Es gibt kein bestes Verfahren, sondern eine Karte: Welches Verfahren genügt, hängt an den Lagen mehr als an den Stapeln. Die Demo
rechnet an einer Bucht die Regel, die Untergrenze und die exakte Suche im gewählten Knotenbudget, empfiehlt und zeigt die gemessene Karte; dazu die Verfahrenskarte der ganzen Linie.

Lauffähig mit: streamlit run app.py
"""

import streamlit as st

import uvw_constants as C
from uvw_evaluation import (
    Settings,
    analyse,
    key,
    load_bands,
    num,
    num_f,
    percent_text,
    result_rows,
    sample_stats,
    share_ok,
    verdict_bay,
    verdict_cell,
)
from uvw_layout import dunkles_design, kopf_css
from uvw_presets import (
    bounds,
    init_session_state_defaults,
    load_permalink_settings,
    randomize_seed,
    sidebar_presets,
    sync_query_params,
)
from uvw_visualization import build_bay, build_carry, build_excess

st.set_page_config(page_title="Verfahrenswahl – Sebastian Hanisch", layout="wide")


@st.cache_data(show_spinner=False)
def _analysis(settings):
    return analyse(settings)


@st.cache_data(show_spinner=False)
def _sample(settings):
    return sample_stats(settings)


@st.cache_data(show_spinner=False)
def _bands():
    return load_bands()


# Fester Kopf: nur der Titel bleibt beim Scrollen oben (Stylesheet in uvw_layout.py).
st.html(kopf_css(dunkles_design()))
with st.container(key="kopf"):
    st.title("🧭 Verfahrenswahl: Regel, Suche oder Schranke?")
st.markdown(
    """
Die Reihe „Umstauen: Untergrenze und Suche“ hat Verfahren gebaut: die **Regel „engste Passung“**, die **Untergrenze**, die **exakte Suche**, das **ILP**, die **Spaltenformulierung** und mehr. **Welches genügt wann?** Die Demo gibt keine Gewinnerin an, sondern eine **Karte**: Sie **rechnet** an einer Bucht die Regel, die Untergrenze und die exakte Suche im gewählten **Knotenbudget**, **empfiehlt** und zeigt die **gemessene Karte** über Stapel und Lagen. Dazu die **Verfahrenskarte der ganzen Linie** mit Frage, Faustregel und Link je Stück.

Weiter unten: die Abschnitte **🔬 Experiment** (die Stichprobe der eigenen Zelle, die gemessene Karte), **🗺️ Die Verfahrenskarte der Linie**, **🚧 Wo die Annahmen enden** und der Expander **📐 Mathematische Formulierung**. Dies ist das fünfzehnte und letzte Stück der Reihe.
"""
)

with st.expander("So wird gemessen", expanded=True):
    st.markdown(
        """
1. **Regel:** Kosten der Regel „engste Passung“ (Stück 1) an der Bucht; eine obere Schranke des Optimums.
2. **Untergrenze:** LB1 = Zahl der Blocker (Stück 2), LB2 zählt die Blocker ohne sicheren Stapel mit (Stück 9). Gleicht die Regel LB2, ist sie **bewiesen optimal**, ohne Suche.
3. **Exakte Suche:** IDA\\* mit LB2 und Zustandsmerken (Stück 5 und 9) im **Knotenbudget**; „trägt“ heißt: Das Ergebnis kommt innerhalb des Budgets.
4. **Empfehlung:** Regel bewiesen → Regel genügt; Suche im Budget → exakte Suche; sonst die Regel mit ihrem Abstand zur Untergrenze als Güte.
5. **Karte:** je Zelle (Stapel × Lagen) 40 feste Buchten, Platz 2, Budget 100 000 Knoten.
        """
    )

st.caption("🔗 Die Adresszeile oben spiegelt Ihre aktuelle Konfiguration wider – einfach kopieren, um ein Szenario zu teilen.")

load_permalink_settings()
init_session_state_defaults()

with st.sidebar:
    sidebar_presets()  # Schnellstart oben, das aktive Preset ist hervorgehoben
    st.header("⚙️ Einstellungen")
    st.markdown("**Bucht und Budget**")
    stacks = st.select_slider("Stapel", options=C.STACK_OPTIONS, key="stacks_slider", help="Wie viele Stapel die Bucht hat.")
    layers = st.slider("Lagen je Stapel", *bounds("layers_slider"), key="layers_slider", help="So viele Container stehen anfangs auf jedem Stapel.")
    extra = st.slider("Platz (Lagen über der Anfangshöhe)", *bounds("extra_slider"), key="extra_slider", help="Höchsthöhe = Lagen + Platz. Standard 2. Die Karte gilt für Platz 2.")
    budget = st.select_slider("Knotenbudget der Suche", options=C.BUDGET_OPTIONS, key="budget_slider", format_func=num, help="So viele Knoten darf die exakte Suche höchstens besuchen.")
    seed = st.number_input("Bucht-Nummer (Seed)", *bounds("seed_input"), key="seed_input", step=1, help="Die Nummer bestimmt, wie die Abrufnummern auf die Plätze verteilt sind.")
    st.button("🎲 Neue Bucht würfeln", width="stretch", on_click=randomize_seed)

sync_query_params({"stacks_slider": int(stacks), "layers_slider": int(layers), "extra_slider": int(extra), "budget_slider": int(budget), "seed_input": int(seed)})

settings = Settings(int(stacks), int(layers), int(extra), int(budget), int(seed))
with st.spinner("Rechne die Regel, die Untergrenzen und die exakte Suche im Knotenbudget …"):
    a = _analysis(settings)

# --- Ergebnis ------------------------------------------------------------------------------------------------------------------------------

st.markdown("## 🎯 Ergebnis")
m1, m2, m3, m4 = st.columns(4)
m1.metric("Regel", a.rule, delta="engste Passung", delta_color="off", help="Hubzahl der Regel; eine obere Schranke des Optimum.")
m2.metric("Untergrenze LB2", a.lb2, delta=f"LB1: {a.lb1}", delta_color="off", help="Blocker plus Blocker ohne sicheren Stapel; darunter die einfache Zählung.")
m3.metric("Exakte Suche", "nicht nötig" if a.status == "proven" else "nicht entschieden" if a.status == "unsolved" else a.optimum,
          delta="Regel = LB2" if a.status == "proven" else f"{num(a.nodes)} Knoten, Budget {num(a.budget)}", delta_color="off", help="Optimum aus der Suche im Knotenbudget.")
m4.metric("Container", a.containers, delta=f"Höchsthöhe {a.height}", delta_color="off")
st.plotly_chart(build_bay(a.bay, a.height, target=min(c for s in a.bay for c in s)), width="stretch", key="chart_bay")
st.caption("Rot: blockierende Container (liegen über einem früher abzurufenden), grün: der nächste Abruf, grau-blau: alle übrigen.")
table = ["| Verfahren | Wert | Aufwand |", "|---|---|---|"]
for r in result_rows(a):
    table.append(f"| {r['name']} | {r['value']} | {r['effort']} |")
st.markdown("\n".join(table))

st.markdown("## ❓ Kernfrage: Welches Verfahren genügt hier?")
kind, text = verdict_bay(a)
getattr(st, kind)(text)

st.markdown("---")

# --- Experiment: die Stichprobe der eigenen Zelle ------------------------------------------------------------------------------------------------

st.subheader("🔬 Experiment: Die eigene Zelle live")
smp = _sample(settings)
if smp is None:
    st.info(f"Die Stichprobe wird live nur bis {C.SAMPLE_MAX_CONTAINERS} Container gerechnet; {settings.stacks} × {settings.layers} hat {settings.stacks * settings.layers}. Die gemessene Karte unten zeigt diese Zelle.")
else:
    st.caption(f"{C.SAMPLE_BAYS} Buchten ab der Bucht-Nummer {settings.seed} (Platz {settings.extra}), Knotenbudget {num(settings.budget)}.")
    st.markdown(f"| Regel = LB1 | bewiesen (Regel = LB2) | Suche löst | nicht entschieden | Knoten Median / Maximum | Regel über Optimum | Regel über LB2 |\n|---|---|---|---|---|---|---|\n"
                f"| {smp['rule_eq_lb1']} | {smp['proven']} | {smp['solved']} | {smp['unsolved']} | "
                + ("–" if smp["nodes_median"] is None else f"{num_f(smp['nodes_median'])} / {num(smp['nodes_max'])}") + " | "
                + ("–" if smp["excess"] is None else percent_text(smp["excess"])) + " | " + ("–" if smp["gap_lb2"] is None else percent_text(smp["gap_lb2"])) + " |")
    kind, text = verdict_cell(smp, f"{settings.stacks} × {settings.layers}, Stichprobe")
    getattr(st, kind)(text)

st.markdown("---")

# --- Experiment: die gemessene Karte -----------------------------------------------------------------------------------------------------------------

karte = _bands()["karte"]
st.subheader("🔬 Experiment: Die gemessene Karte")
st.caption(f"Je Zelle {C.KARTE_BAYS} feste Buchten (Platz 2), vorberechnet (`generate_precomputed.py`), Knotenbudget {num(C.KARTE_BUDGET)}. Links der Anteil der Buchten mit Ergebnis (Regel bewiesen oder Suche gelöst), rechts, wie weit die Regel im Mittel über dem Optimum liegt (nur über die Buchten mit bekanntem Optimum, bei vielen ungelösten Buchten eher zu niedrig).")
st.plotly_chart(build_carry(karte), width="stretch", key="chart_carry")
st.plotly_chart(build_excess(karte), width="stretch", key="chart_excess")
tk = ["| Zelle (Container) | Regel = LB1 | Regel = LB2 (bewiesen) | Suche löst | nicht entschieden | Knoten Median / Maximum | Regel über Optimum | Regel über LB2 |", "|---|---|---|---|---|---|---|---|"]
for l_ in C.KARTE_LAYERS:
    for s_ in C.STACK_OPTIONS:
        c = karte[key(s_, l_)]
        tk.append(f"| {s_} × {l_} ({s_ * l_}) | {c['rule_eq_lb1']} | {c['proven']} | {c['solved']} | {c['unsolved']} | "
                  + ("–" if c["nodes_median"] is None else f"{num_f(c['nodes_median'])} / {num(c['nodes_max'])}") + " | " + ("–" if c["excess"] is None else percent_text(c["excess"])) + " | "
                  + ("–" if c["gap_lb2"] is None else percent_text(c["gap_lb2"])) + " |")
st.markdown("\n".join(tk))
here = karte.get(key(settings.stacks, settings.layers))
st.markdown(f"**Zelle {settings.stacks} × {settings.layers} (Ihre Einstellung):**")
kind, text = verdict_cell(here, f"{settings.stacks} × {settings.layers}")
getattr(st, kind)(text)
if settings.extra != C.DEFAULT_EXTRA or settings.budget != C.KARTE_BUDGET:
    st.caption(f"Die Karte gilt für Platz {C.DEFAULT_EXTRA} und {num(C.KARTE_BUDGET)} Knoten; eingestellt sind Platz {settings.extra} und {num(settings.budget)} Knoten.")

st.markdown("---")

# --- Die Verfahrenskarte der Linie ---------------------------------------------------------------------------------------------------------------------

st.subheader("🗺️ Die Verfahrenskarte der Linie")
st.caption("Jedes Stück der Reihe „Umstauen: Untergrenze und Suche“ mit seiner Frage und einer Faustregel in Worten (die Zahlen stehen in den Stücken selbst).")
tm = ["| Stück | Verfahren | Frage | Faustregel |", "|---|---|---|---|"]
for nr, name, frage, regel, slug in C.METHODS:
    tm.append(f"| {nr} | [{name}](https://sebastianhanisch-{slug}.streamlit.app/) | {frage} | {regel} |")
st.markdown("\n".join(tm))

st.markdown("---")

# --- Grenzen -------------------------------------------------------------------------------------------------------------------------------------

st.subheader("🚧 Wo die Annahmen enden")
st.markdown(
    """
| Annahme | Was passiert, wenn sie verletzt ist | Wer setzt an |
|---|---|---|
| **Eine Karte aus 40 Buchten je Zelle** | Die Anteile sind grob; ein einzelner Eintrag („36 von 40“) kann um einige Buchten schwanken. „Regel über Optimum“ ist ein Mittel über die gelösten Buchten und in Zellen mit vielen ungelösten Buchten eher zu niedrig. | – |
| **Knotenbudget statt Zeit** | „Die Suche trägt“ heißt: Das Ergebnis kommt innerhalb von 100 000 Knoten. Das ist kein Zeitbudget (Python, Einzelmessungen schwanken); mit mehr Budget trägt die Suche weiter. | – |
| **Volle Buchten, Platz 2, restricted** | Teilgefüllte Buchten, anderer Platz und andere Hubmengen (Stück 3) verschieben die Karte. | – |
| **Nur Regel, Untergrenze und Suche gemessen** | ILP und Spaltenformulierung (Stück 7 und 8), Vorsortieren (Stück 11), Einlagern (Stück 12), unbekannte Reihenfolgen (Stück 13) und gelernte Verzweiger (Stück 14) sind nicht Teil der Karte; ihre Fragen stehen in der Verfahrenskarte mit Link. | Stück 7 bis 14 |
| **Gütebeweis über LB2** | Der Abstand der Regel zu LB2 ist nur bei wenigen Lagen brauchbar; bei vielen liegt LB2 meist weit unter dem Optimum (Stück 9). | Stück 9 |
"""
)

st.markdown("---")

with st.expander("📐 Mathematische Formulierung"):
    st.markdown(
        r"""
**Gegeben:** volle Bucht mit $S$ Stapeln, $h$ Lagen, Höchsthöhe $H = h + p$, Abrufnummern $1, \dots, N$ ($N = S\,h$), restricted Relocation.

**Schranken.** $\text{LB1} \le \text{LB2} \le \text{OPT} \le \text{G}$ mit LB1 = Zahl der Blocker (Stück 2), LB2 = LB1 plus Blocker über dem Ziel ohne sicheren Stapel (Stück 9) und $\text{G}$ = Hubzahl der Regel „engste Passung“ (Stück 1).

**Beweis ohne Suche.** Gilt $\text{G} = \text{LB2}$, dann $\text{OPT} = \text{G}$: Die Regel ist bewiesen optimal.

**Exakte Suche.** IDA\* mit LB2 und Zustandsmerken (Stück 5, 6, 9). Mit dem Knotenbudget $B$: Ergebnis, wenn die Suche höchstens $B$ Knoten besucht, sonst „nicht entschieden“.

**Gütebeweis.** Ohne Ergebnis der Suche gilt immer noch $\text{OPT} \le \text{G} \le (1 + \gamma)\,\text{OPT}$ mit $\gamma = \text{G}/\text{LB2} - 1$: Die Regel liegt höchstens $\gamma$ über dem Optimum. Der Wert $\gamma$ ist die einzige Garantie, wenn die Suche nicht trägt; er ist bei wenigen Lagen klein und bei vielen meist groß, vermutlich weil LB2 dort weit unter dem Optimum liegt.

**Anteil mit Ergebnis.** Je Zelle: $\text{trägt} = (\#\text{bewiesen} + \#\text{gelöst}) / n$; Verdikt: trägt, wenn $\ge 90\,\%$, zum Teil ab $50\,\%$, sonst nicht.
        """
    )

st.markdown("---")
st.caption(
    "Diese Demo ist Teil des Portfolios von [Sebastian Hanisch](https://sebastianhanisch.net) – "
    "Operations Research und Machine Learning ([Über mich](https://sebastianhanisch.net/ueber-mich.html)). "
    "Mehr zu den Demos: [Interaktive Demos](https://sebastianhanisch.net/demos.html)."
)
