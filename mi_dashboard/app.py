import streamlit as st
import logging

from config.settings import STREAMLIT_CONFIG
from config.style import COLORS, apply_theme
from components.sidebar import render_sidebar_nav
from utils.cache import get_cached_dataframe
from utils.metrics import get_venta_neta, get_margen_bruto, get_clientes_activos
from utils.formatters import format_currency, format_number

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)

st.set_page_config(
    page_title=STREAMLIT_CONFIG["page_title"],
    page_icon=STREAMLIT_CONFIG["page_icon"],
    layout=STREAMLIT_CONFIG["layout"],
    initial_sidebar_state=STREAMLIT_CONFIG["initial_sidebar_state"],
)

apply_theme()

if "filtros" not in st.session_state:
    st.session_state.filtros = {}

render_sidebar_nav()

c = COLORS

st.markdown(
    f"""
    <div style="
        background: linear-gradient(135deg,
            {c['header_gradient_start']} 0%,
            #1E1B4B 30%,
            #312E81 60%,
            {c['header_gradient_end']} 100%);
        border-radius: 20px;
        padding: 1.8rem 2.2rem;
        margin-bottom: 1.5rem;
        position: relative;
        overflow: hidden;
        border: 1px solid rgba(99,102,241,0.15);
        box-shadow: 0 8px 32px rgba(99,102,241,0.1);
    ">
        <div style="
            position: absolute; top: -40%; right: -10%;
            width: 300px; height: 300px;
            background: radial-gradient(circle, rgba(6,182,212,0.15) 0%, transparent 60%);
            border-radius: 50%;
        "></div>
        <div style="
            position: absolute; bottom: -30%; left: 20%;
            width: 200px; height: 200px;
            background: radial-gradient(circle, rgba(168,85,247,0.1) 0%, transparent 60%);
            border-radius: 50%;
        "></div>
        <div style="position: relative; z-index: 1;">
            <div style="display: flex; align-items: center; justify-content: space-between; flex-wrap: wrap; gap: 1rem;">
                <div style="display: flex; align-items: center; gap: 1rem;">
                    <div style="
                        width: 48px; height: 48px;
                        background: linear-gradient(135deg, {c['primary']}, {c['accent']});
                        border-radius: 14px;
                        display: flex; align-items: center; justify-content: center;
                        font-size: 1.5rem; box-shadow: 0 4px 20px rgba(99,102,241,0.4);
                    ">🏢</div>
                    <div>
                        <div style="
                            font-size: 1.6rem; font-weight: 900; color: white;
                            letter-spacing: -0.5px; line-height: 1.2;
                        ">Dashboard Comercial</div>
                        <div style="
                            font-size: 0.82rem; color: rgba(255,255,255,0.55);
                            font-weight: 400; margin-top: 0.15rem;
                        ">Comercial Andina S.A. — Análisis de Ventas, Rentabilidad y Cumplimiento</div>
                    </div>
                </div>
                <div style="display: flex; align-items: center; gap: 0.6rem;">
                    <div style="
                        display: flex; align-items: center; gap: 0.35rem;
                        background: rgba(16,185,129,0.15);
                        border: 1px solid rgba(16,185,129,0.25);
                        padding: 0.3rem 0.7rem; border-radius: 20px;
                    ">
                        <div style="
                            width: 7px; height: 7px;
                            background: {c['success']};
                            border-radius: 50%;
                            box-shadow: 0 0 8px {c['success']};
                            animation: pulse-glow 2s ease-in-out infinite;
                        "></div>
                        <span style="color: {c['success']}; font-size: 0.65rem; font-weight: 600; letter-spacing: 0.5px;">LIVE</span>
                    </div>
                    <span style="color: rgba(255,255,255,0.3); font-size: 0.65rem; letter-spacing: 1px;">v2.0</span>
                </div>
            </div>
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)

with st.spinner("Cargando resumen..."):
    ventas = get_cached_dataframe("ventas")

if ventas is not None and not ventas.empty:
    kpi_cols = st.columns(3)
    summary = [
        ("Venta Neta Total", format_currency(get_venta_neta(ventas)), c["primary"], "💰"),
        ("Margen Bruto Total", format_currency(get_margen_bruto(ventas)), c["success"], "📈"),
        ("Clientes Activos", format_number(float(get_clientes_activos(ventas))), c["accent"], "👥"),
    ]
    for col, (label, value, color, icon) in zip(kpi_cols, summary):
        with col:
            st.markdown(
                f"""
                <div style="
                    background: rgba(255,255,255,0.03);
                    border: 1px solid {c['border']};
                    border-left: 3px solid {color};
                    border-radius: 14px;
                    padding: 0.9rem 1rem;
                    margin-bottom: 0.5rem;
                    animation: fadeInUp 0.4s ease-out both;
                ">
                    <div style="color: {c['text_muted']}; font-size: 0.65rem; font-weight: 700;
                                text-transform: uppercase; letter-spacing: 0.6px;">
                        {icon} {label}
                    </div>
                    <div style="color: {c['text_primary']}; font-size: 1.35rem; font-weight: 800;
                                margin-top: 0.2rem; font-variant-numeric: tabular-nums;">
                        {value}
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )

st.markdown("<div class='section-divider'></div>", unsafe_allow_html=True)

st.markdown(
    f"""
    <div style="
        font-size: 1.05rem; font-weight: 700; color: {c['text_primary']};
        margin: 1rem 0 0.8rem 0; letter-spacing: -0.3px;
    ">📂 Módulos del Dashboard</div>
    """,
    unsafe_allow_html=True,
)

nav_cards = [
    ("📊", "Vista Gerencial", "KPIs, tendencias, distribución y cumplimiento de metas", "pages/1_Gerencial.py", c["primary"]),
    ("📈", "Vista Estratégica", "Rentabilidad, ranking de productos, Pareto y análisis de portafolio", "pages/2_Estrategica.py", c["success"]),
    ("📋", "Vista Operativa", "Detalle transaccional, ejecutivos, clientes y descuentos", "pages/3_Operativa.py", c["accent"]),
]
nav_cols = st.columns(3)
for col, (icon, title, desc, page, accent) in zip(nav_cols, nav_cards):
    with col:
        st.markdown(
            f"""
            <div style="
                background: rgba(255,255,255,0.025);
                border: 1px solid {c['border']};
                border-top: 3px solid {accent};
                border-radius: 16px;
                padding: 1rem 0.8rem 0.5rem 0.8rem;
                text-align: center;
                transition: all 0.3s ease;
                margin-bottom: 0.3rem;
            ">
                <div style="font-size: 2rem; margin-bottom: 0.3rem;">{icon}</div>
                <div style="color: {c['text_primary']}; font-size: 0.9rem; font-weight: 700; margin-bottom: 0.2rem;">{title}</div>
                <div style="color: {c['text_muted']}; font-size: 0.68rem; line-height: 1.4; margin-bottom: 0.5rem;">{desc}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
        st.page_link(page, label=f"Ir a {title}", use_container_width=True)

st.markdown("<div class='section-divider'></div>", unsafe_allow_html=True)

with st.expander("ℹ️ Acerca del Dashboard", expanded=False):
    st.markdown(
        """
        **Comercial Andina S.A.** — Dashboard de análisis de ventas, rentabilidad, cumplimiento de metas y comportamiento de clientes.

        - **Fuente de datos**: `bbdd_prueba.xlsx` (6 hojas)
        - **Modelo**: Esquema estrella (Ventas como hecho, 4 dimensiones)
        - **Stack**: Python 3.12+, Streamlit, Plotly, Pandas
        - **Base de datos**: Supabase (PostgreSQL)
        """
    )
