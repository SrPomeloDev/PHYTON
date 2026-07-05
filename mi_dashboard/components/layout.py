"""Componentes de layout reutilizables para todas las vistas."""

import streamlit as st
import plotly.graph_objects as go

from config.style import COLORS


def page_header(
    title: str,
    subtitle: str,
    icon: str,
    gradient: str,
) -> None:
    """Encabezado consistente para cada página del dashboard."""
    c = COLORS
    st.markdown(
        f"""
        <div class="page-header">
            <div class="page-header-icon" style="background: {gradient};">{icon}</div>
            <div>
                <div class="page-header-title">{title}</div>
                <div class="page-header-subtitle">{subtitle}</div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def section_header(
    title: str,
    icon: str = "",
    subtitle: str = "",
    accent: str = COLORS["primary"],
) -> None:
    """Título de sección con icono y subtítulo opcional."""
    sub_html = (
        f"<div class='section-subtitle'>{subtitle}</div>"
        if subtitle
        else ""
    )
    st.markdown(
        f"""
        <div class='section-title'>
            <span style="color: {accent};">{icon}</span> {title}
        </div>
        {sub_html}
        """,
        unsafe_allow_html=True,
    )


def section_divider() -> None:
    st.markdown("<div class='section-divider'></div>", unsafe_allow_html=True)


def chart_panel(fig: go.Figure, key: str | None = None) -> None:
    """Renderiza un gráfico Plotly con estilo de panel (CSS en config/style.py)."""
    st.plotly_chart(fig, use_container_width=True, key=key)


def progress_bar_row(
    label: str,
    pct: float,
    detail: str,
    bar_color: str,
) -> None:
    """Barra de progreso horizontal para cumplimiento de metas."""
    c = COLORS
    bar_width = min(pct * 100, 100)
    pct_display = f"{pct * 100:.1f}%"
    st.markdown(
        f"""
        <div class="progress-row">
            <div class="progress-label">{label}</div>
            <div class="progress-track">
                <div class="progress-fill" style="width:{bar_width}%; background:linear-gradient(90deg,{bar_color},{bar_color}AA); box-shadow:0 0 8px {bar_color}40;"></div>
            </div>
            <div class="progress-pct" style="color:{bar_color};">{pct_display}</div>
            <div class="progress-detail">{detail}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def empty_state(message: str, kind: str = "info") -> None:
    """Estado vacío consistente."""
    if kind == "warning":
        st.warning(message)
    elif kind == "success":
        st.success(message)
    else:
        st.info(message)


def mini_kpi_card(label: str, value: str, color: str = COLORS["primary"]) -> None:
    """Render a compact inline KPI card — used for summary rows above tables."""
    # Extract rgba background from hex color
    h = color.lstrip("#")
    r, g, b = int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16)
    bg = f"rgba({r},{g},{b},0.08)"
    border = f"rgba({r},{g},{b},0.15)"
    c = COLORS
    st.markdown(
        f"""
        <div style="
            background: {bg};
            border-radius: 10px;
            padding: 0.4rem 0.8rem;
            text-align: center;
            border: 1px solid {border};
            margin-bottom: 0.5rem;
        ">
            <div style="
                font-size: 0.55rem;
                color: {c['text_muted']};
                font-weight: 700;
                text-transform: uppercase;
                letter-spacing: 0.5px;
            ">{label}</div>
            <div style="
                font-size: 1.1rem;
                font-weight: 800;
                color: {c['text_primary']};
            ">{value}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )
