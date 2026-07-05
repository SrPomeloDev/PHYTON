import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
from typing import Optional

from config.style import COLORS, PLOTLY_TEMPLATE, CHART_COLORS, FONT_FAMILY
from utils.formatters import format_currency, format_percent


# ── Dark theme base ──────────────────────────────────────────────────────────

def _apply_theme(fig: go.Figure, height: int = 420) -> go.Figure:
    """Apply premium dark theme to any Plotly figure."""
    fig.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font_family=FONT_FAMILY,
        font_color=COLORS["text_secondary"],
        font_size=12,
        title_font_size=15,
        title_font_color=COLORS["text_primary"],
        title_font_family=FONT_FAMILY,
        title_x=0.01,
        title_xanchor="left",
        margin=dict(l=16, r=16, t=52, b=16),
        height=height,
        hovermode="x unified",
        hoverlabel=dict(
            bgcolor="#1E293B",
            font_size=12,
            font_family=FONT_FAMILY,
            font_color=COLORS["text_primary"],
            bordercolor="rgba(99,102,241,0.4)",
        ),
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1,
            font=dict(size=11, color=COLORS["text_muted"]),
            bgcolor="rgba(0,0,0,0)",
        ),
        xaxis=dict(
            showgrid=True,
            gridcolor="rgba(255,255,255,0.05)",
            gridwidth=0.5,
            title_font=dict(size=11, color=COLORS["text_muted"]),
            tickfont=dict(size=10, color=COLORS["text_muted"]),
            zeroline=False,
            showline=True,
            linecolor="rgba(255,255,255,0.08)",
            linewidth=1,
        ),
        yaxis=dict(
            showgrid=True,
            gridcolor="rgba(255,255,255,0.05)",
            gridwidth=0.5,
            title_font=dict(size=11, color=COLORS["text_muted"]),
            tickfont=dict(size=10, color=COLORS["text_muted"]),
            zeroline=False,
            showline=False,
        ),
        # Prevent text labels from being hidden when they don't fit
        uniformtext=dict(minsize=8, mode="hide"),
    )
    return fig


def _clean_legend(fig: go.Figure) -> go.Figure:
    if fig.data and len(fig.data) <= 1:
        fig.update_layout(showlegend=False)
    return fig


def _hex_to_rgb(hex_color: str) -> tuple[int, int, int]:
    """Convert a hex color like '#6366F1' to (r, g, b) tuple."""
    h = hex_color.lstrip("#")
    return int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16)


def _format_text_value(val: float, prefix: str = "Bs") -> str:
    """Format a numeric value for display as bar/treemap text label."""
    if abs(val) >= 1_000_000:
        return f"{prefix}{val / 1_000_000:,.1f}M"
    if abs(val) >= 1_000:
        return f"{prefix}{val / 1_000:,.1f}K"
    return f"{prefix}{val:,.0f}"


# ── Line Chart ───────────────────────────────────────────────────────────────

def line_chart(
    df: pd.DataFrame,
    x: str,
    y: str,
    title: str = "",
    color: Optional[str] = None,
) -> go.Figure:
    fig = px.line(
        df, x=x, y=y, title=title, color=color, markers=True,
        color_discrete_sequence=CHART_COLORS, template=PLOTLY_TEMPLATE,
    )
    fig = _apply_theme(fig)
    fig = _clean_legend(fig)
    for i, trace in enumerate(fig.data):
        trace_color = CHART_COLORS[i % len(CHART_COLORS)]
        r, g, b = _hex_to_rgb(trace_color)
        trace_name = trace.name or y
        trace.update(
            line_width=3,
            line_shape="spline",
            marker_size=9,
            marker_line_width=2.5,
            marker_line_color="#0B0F19",
            hovertemplate=(
                f"<b>{trace_name}</b><br>"
                f"%{{x}}<br>"
                f"Bs%{{y:,.2f}}<extra></extra>"
            ),
            fill="tozeroy" if len(fig.data) == 1 else None,
            fillcolor=f"rgba({r},{g},{b},0.06)" if len(fig.data) == 1 else None,
        )
    return fig


# ── Bar Chart ────────────────────────────────────────────────────────────────

def bar_chart(
    df: pd.DataFrame,
    x: str,
    y: str,
    title: str = "",
    color: Optional[str] = None,
    orientation: str = "v",
    value_prefix: str = "Bs",
) -> go.Figure:
    fig = px.bar(
        df, x=x, y=y, title=title, color=color, orientation=orientation,
        color_discrete_sequence=CHART_COLORS,
        template=PLOTLY_TEMPLATE,
    )
    fig = _apply_theme(fig)
    fig = _clean_legend(fig)

    # Determine the value column for formatting
    val_col = y if orientation == "v" else x

    # Build readable text labels instead of scientific notation
    for trace in fig.data:
        vals = trace.y if orientation == "v" else trace.x
        if vals is not None:
            trace.text = [_format_text_value(v, value_prefix) for v in vals]

    # Hover template with field name and formatted value
    if orientation == "v":
        hover = (
            f"<b>%{{x}}</b><br>"
            f"{val_col}: {value_prefix}%{{y:,.2f}}<extra></extra>"
        )
    else:
        hover = (
            f"<b>%{{y}}</b><br>"
            f"{val_col}: {value_prefix}%{{x:,.2f}}<extra></extra>"
        )

    fig.update_traces(
        marker_line_width=0,
        marker_cornerradius=6,
        textposition="outside",
        textfont=dict(size=10, color=COLORS["text_muted"]),
        hovertemplate=hover,
        opacity=0.9,
        cliponaxis=False,
    )
    # Add subtle gradient effect via color opacity
    if not color:
        for i, trace in enumerate(fig.data):
            c = CHART_COLORS[i % len(CHART_COLORS)]
            r, g, b = _hex_to_rgb(c)
            trace.update(
                marker_color=f"rgba({r},{g},{b},0.85)",
            )

    # Extra margin for horizontal bars with long labels
    if orientation == "h":
        fig.update_layout(margin=dict(l=120, r=40, t=52, b=16))

    return fig


# ── Donut Chart ──────────────────────────────────────────────────────────────

def donut_chart(
    df: pd.DataFrame,
    names: str,
    values: str,
    title: str = "",
    color_map: dict | None = None,
) -> go.Figure:
    fig = px.pie(
        df, names=names, values=values, title=title, hole=0.65,
        color=names if color_map else None,
        color_discrete_map=color_map if color_map else None,
        color_discrete_sequence=CHART_COLORS if not color_map else None,
        template=PLOTLY_TEMPLATE,
    )
    fig = _apply_theme(fig)
    fig.update_layout(
        showlegend=True,
        legend=dict(
            orientation="h", yanchor="bottom", y=-0.2,
            xanchor="center", x=0.5,
            font=dict(size=11, color=COLORS["text_muted"]),
        ),
        margin=dict(l=16, r=16, t=52, b=60),
    )
    fig.update_traces(
        textposition="outside",
        textinfo="percent+label",
        textfont=dict(size=11, color=COLORS["text_secondary"]),
        marker=dict(
            line=dict(color="#0B0F19", width=3),
        ),
        pull=[0.02] * len(df),
        hovertemplate=(
            "<b>%{label}</b><br>"
            f"{values}: Bs%{{value:,.2f}}<br>"
            "Participación: %{percent}<extra></extra>"
        ),
    )
    return fig


# ── Heatmap ──────────────────────────────────────────────────────────────────

def heatmap(
    df: pd.DataFrame,
    x: str,
    y: str,
    z: str,
    title: str = "",
) -> go.Figure:
    pivot = df.pivot_table(index=y, columns=x, values=z, aggfunc="sum")
    # Custom dark colorscale with improved contrast
    colorscale = [
        [0.0, "#0B0F19"],
        [0.15, "#1E1B4B"],
        [0.35, "#312E81"],
        [0.55, "#4F46E5"],
        [0.75, "#06B6D4"],
        [1.0, "#22D3EE"],
    ]

    # Build readable text annotations instead of ".2s"
    text_vals = []
    for row in pivot.values:
        text_row = []
        for val in row:
            if pd.isna(val) or val == 0:
                text_row.append("")
            else:
                text_row.append(_format_text_value(val, "Bs"))
        text_vals.append(text_row)

    fig = go.Figure(data=go.Heatmap(
        z=pivot.values,
        x=pivot.columns.tolist(),
        y=pivot.index.tolist(),
        colorscale=colorscale,
        text=text_vals,
        texttemplate="%{text}",
        textfont=dict(color=COLORS["text_primary"], size=11),
        hovertemplate=(
            f"<b>%{{x}}</b> × <b>%{{y}}</b><br>"
            f"{z}: Bs%{{z:,.2f}}<extra></extra>"
        ),
        colorbar=dict(
            title="",
            tickfont=dict(color=COLORS["text_muted"], size=10),
            outlinewidth=0,
            borderwidth=0,
            bgcolor="rgba(0,0,0,0)",
        ),
    ))
    fig.update_layout(title=title)
    fig = _apply_theme(fig)
    fig.update_layout(
        xaxis=dict(side="bottom"),
    )
    return fig


# ── Scatter Chart ────────────────────────────────────────────────────────────

def scatter_chart(
    df: pd.DataFrame,
    x: str,
    y: str,
    title: str = "",
    color: Optional[str] = None,
    size: Optional[str] = None,
    text: Optional[str] = None,
    x_prefix: str = "Bs",
    y_format: str = "percent",
) -> go.Figure:
    fig = px.scatter(
        df, x=x, y=y, title=title, color=color, size=size, text=text,
        color_discrete_sequence=CHART_COLORS,
        template=PLOTLY_TEMPLATE,
    )
    fig = _apply_theme(fig)
    fig = _clean_legend(fig)

    # Build contextual hover template
    if y_format == "percent":
        y_fmt = "%{y:.1%}"
    else:
        y_fmt = f"{x_prefix}%{{y:,.2f}}"

    hover = (
        f"<b>%{{text}}</b><br>" if text else ""
    ) + (
        f"{x}: {x_prefix}%{{x:,.2f}}<br>"
        f"{y}: {y_fmt}<extra></extra>"
    )

    # Style scatter markers
    for trace in fig.data:
        if trace.mode and "markers" in trace.mode:
            trace.update(
                marker=dict(
                    size=11,
                    line=dict(width=2.5, color="#0B0F19"),
                    opacity=0.9,
                ),
                hovertemplate=hover,
            )
        # Style trendlines
        if hasattr(trace, 'line') and trace.mode == "lines":
            trace.update(
                line=dict(width=2, dash="dot"),
                opacity=0.5,
            )
    return fig


# ── Treemap ──────────────────────────────────────────────────────────────────

def treemap(
    df: pd.DataFrame,
    path: list[str],
    values: str,
    title: str = "",
    color: Optional[str] = None,
) -> go.Figure:
    fig = px.treemap(
        df, path=path, values=values, title=title, color=color,
        color_continuous_scale=[
            [0.0, "#1E1B4B"],
            [0.3, "#4F46E5"],
            [0.5, "#6366F1"],
            [0.7, "#06B6D4"],
            [1.0, "#22D3EE"],
        ],
        template=PLOTLY_TEMPLATE,
    )
    fig = _apply_theme(fig, height=500)
    fig.update_traces(
        textinfo="label+value",
        texttemplate="<b>%{label}</b><br>Bs%{value:,.0f}",
        textfont=dict(color="white", size=12),
        hovertemplate=(
            "<b>%{label}</b><br>"
            f"{values}: Bs%{{value:,.2f}}<br>"
            "Participación: %{percentRoot:.1%}"
            "<extra></extra>"
        ),
        marker=dict(
            line=dict(width=2, color="#0B0F19"),
            cornerradius=4,
        ),
    )
    fig.update_layout(
        margin=dict(l=0, r=0, t=44, b=0),
        coloraxis_showscale=False,
    )
    return fig


# ── Pareto Chart ─────────────────────────────────────────────────────────────

def pareto_chart(
    df: pd.DataFrame,
    item_col: str,
    value_col: str,
    title: str = "",
) -> go.Figure:
    df_sorted = df.sort_values(value_col, ascending=False).reset_index(drop=True)
    df_sorted["cumsum"] = df_sorted[value_col].cumsum()
    df_sorted["cumsum_pct"] = df_sorted["cumsum"] / df_sorted[value_col].sum() * 100

    fig = go.Figure()

    # Bars with gradient
    fig.add_trace(
        go.Bar(
            x=df_sorted[item_col],
            y=df_sorted[value_col],
            name=value_col,
            marker=dict(
                color=df_sorted[value_col],
                colorscale=[
                    [0, CHART_COLORS[1]],   # Cyan
                    [1, CHART_COLORS[0]],   # Indigo
                ],
                cornerradius=6,
                line=dict(width=0),
            ),
            opacity=0.85,
            text=df_sorted[value_col].apply(lambda v: _format_text_value(v, "Bs")),
            textposition="outside",
            textfont=dict(size=9, color=COLORS["text_muted"]),
            hovertemplate=(
                "<b>%{x}</b><br>"
                f"{value_col}: Bs%{{y:,.2f}}"
                "<extra></extra>"
            ),
        )
    )

    # Cumulative line with glow
    fig.add_trace(
        go.Scatter(
            x=df_sorted[item_col],
            y=df_sorted["cumsum_pct"],
            name="% Acumulado",
            yaxis="y2",
            line=dict(color=COLORS["warning"], width=3, shape="spline"),
            mode="lines+markers",
            marker=dict(size=9, line=dict(width=2.5, color="#0B0F19")),
            hovertemplate=(
                "<b>%{x}</b><br>"
                "Acumulado: %{y:.1f}%"
                "<extra></extra>"
            ),
        )
    )

    # 80% reference line
    fig.add_hline(
        y=80, yref="y2",
        line_dash="dash", line_color="rgba(239,68,68,0.4)", line_width=1,
        annotation_text="80%",
        annotation_font=dict(color=COLORS["danger"], size=10),
        annotation_position="right",
    )

    # FIX: Apply base theme FIRST, then overlay custom yaxis2 settings
    fig = _apply_theme(fig, height=460)

    # Now set title and yaxis2 AFTER theme so they aren't overwritten
    fig.update_layout(
        title=title,
        yaxis=dict(
            title=value_col,
            gridcolor="rgba(255,255,255,0.05)",
            title_font=dict(size=11, color=COLORS["text_muted"]),
        ),
        yaxis2=dict(
            title="% Acumulado",
            overlaying="y",
            side="right",
            range=[0, 105],
            gridcolor="rgba(255,255,255,0.03)",
            title_font=dict(size=11, color=COLORS["text_muted"]),
            tickfont=dict(color=COLORS["text_muted"]),
            ticksuffix="%",
        ),
        barmode="group",
    )
    return fig


# ── Gauge Chart ──────────────────────────────────────────────────────────────

def gauge_chart(
    value: float,
    title: str = "",
    max_val: float = 1.0,
    suffix: str = "%",
) -> go.Figure:
    """Render a semicircular gauge chart for goal completion."""
    display_val = value * 100 if max_val <= 1.0 else value
    display_max = max_val * 100 if max_val <= 1.0 else max_val

    # Color based on performance
    if display_val >= 90:
        bar_color = COLORS["success"]
    elif display_val >= 70:
        bar_color = COLORS["warning"]
    else:
        bar_color = COLORS["danger"]

    fig = go.Figure(
        go.Indicator(
            mode="gauge+number",
            value=display_val,
            number=dict(
                suffix=suffix,
                font=dict(size=36, color=COLORS["text_primary"], family=FONT_FAMILY),
            ),
            title=dict(
                text=title,
                font=dict(size=13, color=COLORS["text_muted"], family=FONT_FAMILY),
            ),
            gauge=dict(
                axis=dict(
                    range=[0, display_max],
                    tickfont=dict(size=10, color=COLORS["text_muted"]),
                    tickcolor=COLORS["text_muted"],
                ),
                bar=dict(color=bar_color, thickness=0.75),
                bgcolor="rgba(255,255,255,0.04)",
                borderwidth=0,
                steps=[
                    {"range": [0, display_max * 0.7], "color": "rgba(239,68,68,0.15)"},
                    {"range": [display_max * 0.7, display_max * 0.9], "color": "rgba(245,158,11,0.15)"},
                    {"range": [display_max * 0.9, display_max], "color": "rgba(16,185,129,0.12)"},
                ],
                threshold=dict(
                    line=dict(color=COLORS["text_primary"], width=2),
                    thickness=0.8,
                    value=display_val,
                ),
            ),
        )
    )
    fig.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font_family=FONT_FAMILY,
        height=260,
        margin=dict(l=30, r=30, t=60, b=10),
    )
    return fig
