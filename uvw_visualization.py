"""Plotly-Abbildungen. Alle Achsen sind gesperrt (fixedrange), damit Touch-Geräte beim Scrollen nicht am Diagramm hängen bleiben."""

import plotly.graph_objects as go

import uvw_algorithm as A
import uvw_constants as C


def lock_axes(fig):
    fig.update_xaxes(fixedrange=True)
    fig.update_yaxes(fixedrange=True)
    return fig


def _base(fig, height=340):
    fig.update_layout(height=height, margin=dict(l=10, r=10, t=10, b=10), legend=dict(orientation="h", y=-0.25), plot_bgcolor="rgba(0,0,0,0)")
    return lock_axes(fig)


def blocker_cells(stacks) -> set:
    """Container, die über einem früher abzurufenden im selben Stapel liegen (Position (Stapel, Lage))."""
    out = set()
    for i, s in enumerate(stacks):
        lowest = A.INF
        for j, c in enumerate(s):
            if c > lowest:
                out.add((i, j))
            else:
                lowest = c
    return out


def build_bay(stacks, height, target=None):
    """Die Bucht als Säulen: je Lage ein Balken mit der Abrufnummer. Rot: blockiert einen früher abzurufenden, grün: nächster Abruf
    (`target`, eine Abrufnummer oder None), grau-blau: übrige."""
    blockers = blocker_cells(stacks)
    fig = go.Figure()
    xs = list(range(len(stacks)))
    for j in range(height):
        ys, colors, texts = [], [], []
        for i, s in enumerate(stacks):
            if j < len(s):
                c = s[j]
                ys.append(1)
                texts.append(str(c))
                colors.append(C.COLOR_TARGET if c == target else C.COLOR_BLOCK if (i, j) in blockers else C.COLOR_CELL)
            else:
                ys.append(0)
                texts.append("")
                colors.append(C.COLOR_CELL)
        fig.add_trace(go.Bar(x=xs, y=ys, base=j, marker_color=colors, text=texts, textposition="inside", insidetextanchor="middle",
                             textfont=dict(color="#ffffff", size=16), width=0.78, showlegend=False,
                             hovertemplate="Abruf %{text}<extra></extra>", marker_line=dict(width=0)))
    fig.update_layout(barmode="overlay")
    fig.add_hline(y=height, line_dash="dot", line_color="rgba(128,128,128,0.7)", annotation_text="Höchsthöhe", annotation_position="top left")
    fig.update_xaxes(tickvals=xs, ticktext=[f"Stapel {i + 1}" for i in xs], showgrid=False)
    fig.update_yaxes(range=[0, height + 0.35], showticklabels=False, showgrid=False, zeroline=False)
    return _base(fig, height=48 * height + 90)


def _grid(karte, value):
    """Matrix (Lagen × Stapel) aus `value(stats)` über die Zellen der Karte; fehlende Zellen None."""
    xs = list(C.STACK_OPTIONS)
    ys = list(C.KARTE_LAYERS)
    z = [[value(karte[f"{s},{l}"]) if f"{s},{l}" in karte else None for s in xs] for l in ys]
    return xs, ys, z


def build_carry(karte):
    """Karte „trägt die Suche?“: Anteil der Buchten mit Ergebnis (bewiesen oder gelöst) in Prozent, je Zelle Stapel × Lagen. `karte`: {"s,l": cell_stats}."""
    xs, ys, z = _grid(karte, lambda c: 100.0 * (c["proven"] + c["solved"]) / c["n"])
    text = [[("" if v is None else f"{v:.0f} %") for v in row] for row in z]
    fig = go.Figure(go.Heatmap(x=[str(s) for s in xs], y=[f"{l} Lagen" for l in ys], z=z, text=text, texttemplate="%{text}", colorscale=C.COLOR_SCALE, zmin=0, zmax=100,
                               colorbar=dict(title="Buchten mit Ergebnis (%)"), hovertemplate="%{x} Stapel, %{y}: %{z:.0f} %<extra></extra>"))
    fig.update_xaxes(type="category", title_text="Zahl der Stapel")
    fig.update_yaxes(type="category", autorange="reversed")
    return _base(fig, height=330)


def build_excess(karte):
    """Karte „wie gut ist die Regel?“: Regel über dem Optimum in Prozent (Mittel über die Buchten mit bekanntem Optimum), je Zelle Stapel × Lagen. `karte`: {"s,l": cell_stats}."""
    xs, ys, z = _grid(karte, lambda c: None if c["excess"] is None else 100.0 * c["excess"])
    text = [[("" if v is None else (f"{v:.1f} %" if v < 10 else f"{v:.0f} %")) for v in row] for row in z]
    fig = go.Figure(go.Heatmap(x=[str(s) for s in xs], y=[f"{l} Lagen" for l in ys], z=z, text=text, texttemplate="%{text}", colorscale=C.COLOR_SCALE_REV, zmin=0, zmax=15,
                               colorbar=dict(title="Regel über Optimum (%)"), hovertemplate="%{x} Stapel, %{y}: %{z:.1f} %<extra></extra>"))
    fig.update_xaxes(type="category", title_text="Zahl der Stapel")
    fig.update_yaxes(type="category", autorange="reversed")
    return _base(fig, height=330)
