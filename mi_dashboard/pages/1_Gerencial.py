import streamlit as st
import pandas as pd

from utils.cache import get_cached_dataframe
from utils.metrics import (
    get_venta_neta,
    get_margen_bruto,
    get_margen_pct,
    get_ticket_promedio,
    get_cantidad_vendida,
    get_clientes_activos,
)
from utils.formatters import format_currency, format_number, format_percent
from utils.helpers import apply_filters, get_mom_yoy_change, store_drill
from components.sidebar import render_sidebar, render_sidebar_nav
from components.cards import kpi_card
from components.charts import line_chart, bar_chart, donut_chart, heatmap
from components.layout import (
    page_header,
    section_header,
    section_divider,
    chart_panel,
    progress_bar_row,
    empty_state,
)
from config.style import COLORS, apply_theme, SEGMENT_COLORS

apply_theme()

c = COLORS

page_header(
    title="Vista Gerencial",
    subtitle="Indicadores clave, evolución mensual y distribución comercial.",
    icon="📊",
    gradient=f"linear-gradient(135deg, {c['primary']}, #818CF8)",
)

with st.spinner("Cargando datos gerenciales..."):
    ventas = get_cached_dataframe("ventas")
    productos = get_cached_dataframe("productos")
    clientes = get_cached_dataframe("clientes")
    sucursales = get_cached_dataframe("sucursales")
    metas = get_cached_dataframe("metas")

if ventas is None or ventas.empty:
    empty_state("No hay datos de ventas disponibles.", kind="warning")
    st.stop()

render_sidebar_nav()
filtros = render_sidebar()

ventas_full = ventas.copy()
ventas = apply_filters(ventas, filtros, productos, clientes)

if ventas.empty:
    empty_state("No hay datos que coincidan con los filtros seleccionados.")
    st.stop()

section_header("Indicadores Clave", "💰", "Métricas consolidadas del período filtrado", c["primary"])

_kpi_defs = [
    ("Venta Neta", get_venta_neta, format_currency, c["primary"], "💰"),
    ("Margen Bruto", get_margen_bruto, format_currency, c["success"], "📈"),
    ("Margen %", get_margen_pct, format_percent, c["warning"], "🎯"),
    ("Ticket Promedio", get_ticket_promedio, format_currency, c["purple"], "🧾"),
    ("Cant. Vendida", get_cantidad_vendida, format_number, c["accent"], "📦"),
    ("Clientes Activos", get_clientes_activos, lambda v: format_number(float(v)), c["danger"], "👥"),
]
_kpi_results = []
for label, metric_fn, fmt_fn, color, icon in _kpi_defs:
    current_val = metric_fn(ventas)
    mom_pct, yoy_pct = get_mom_yoy_change(ventas_full, filtros, metric_fn, productos, clientes)

    delta = ""
    if mom_pct is not None and current_val:
        arrow = "▲" if mom_pct >= 0 else "▼"
        delta = f"{arrow} {abs(mom_pct)*100:.1f}% vs mes ant."

    help_text = ""
    if yoy_pct is not None:
        arrow = "▲" if yoy_pct >= 0 else "▼"
        help_text = f"{arrow} {abs(yoy_pct)*100:.1f}% vs año ant."

    _kpi_results.append((label, fmt_fn(current_val), delta, help_text, color, icon))

for row_start in range(0, 6, 3):
    cols = st.columns(3)
    for i in range(3):
        idx = row_start + i
        r = _kpi_results[idx]
        with cols[i]:
            kpi_card(r[0], r[1], delta=r[2], help_text=r[3], color=r[4], icon=r[5], delay=0.05 * idx)

section_divider()

section_header(
    "Evolución Mensual",
    "📈",
    "Venta Neta y Margen Bruto mes a mes",
    c["primary"],
)

tendencia = ventas.groupby("Periodo", as_index=False)[["Venta_Neta", "Margen_Bruto"]].sum().sort_values("Periodo")
tendencia_melted = tendencia.melt(id_vars="Periodo", var_name="Métrica", value_name="Valor")

if tendencia_melted.empty:
    empty_state("Sin datos de tendencia para los filtros actuales.")
else:
    fig_tendencia = line_chart(
        tendencia_melted, x="Periodo", y="Valor", color="Métrica",
        title="Evolución Mensual — Venta Neta y Margen Bruto",
    )
    chart_panel(fig_tendencia, key="gerencial_tendencia")

section_divider()

section_header("Análisis Multidimensional (Cumplimiento de Matriz)", "🧭", "Objetivos estratégicos según requerimiento: VENTA, MARGEN, META, CLIENTE.", c["primary"])

# --- 2x2 Grid for the 4 requirements ---
col_req1, col_req2 = st.columns(2)

with col_req1:
    st.markdown(f"**1. VENTA** — Crecimiento y concentración (Dim: Canal)")
    ventas_canal = ventas.groupby("Canal", as_index=False)["Venta_Neta"].sum().sort_values("Venta_Neta", ascending=False)
    if not ventas_canal.empty:
        fig_canal = bar_chart(ventas_canal, x="Canal", y="Venta_Neta", title="Venta Neta por Canal")
        chart_panel(fig_canal, key="gerencial_canal")

with col_req2:
    st.markdown(f"**2. MARGEN** — Rentabilidad del negocio (Dim: Categoría)")
    if productos is not None and not productos.empty:
        df_cat = ventas.merge(productos[["Codigo_Producto_Homologado", "Categoria"]], on="Codigo_Producto_Homologado", how="left")
        mgen_cat = df_cat.groupby("Categoria", as_index=False)["Margen_Bruto"].sum().sort_values("Margen_Bruto", ascending=False)
        if not mgen_cat.empty:
            fig_cat = bar_chart(mgen_cat, x="Categoria", y="Margen_Bruto", title="Margen Bruto por Categoría")
            chart_panel(fig_cat, key="gerencial_cat_margen")
    else:
        empty_state("Datos de productos no disponibles.", kind="warning")

st.markdown("<div style='height:0.75rem'/>", unsafe_allow_html=True)

col_req3, col_req4 = st.columns(2)

with col_req3:
    st.markdown(f"**3. META** — Cumplimiento comercial (Dim: Regional)")
    suc_exists = sucursales is not None and not sucursales.empty
    ventas_suc = ventas.merge(sucursales, on="ID_Sucursal", how="left") if suc_exists else ventas.copy()
    if "Regional" in ventas_suc.columns and metas is not None and not metas.empty:
        ventas_suc["KeyMeta"] = (
            ventas_suc["Año"].astype(str) + "|" + ventas_suc["Mes"].astype(str) + "|"
            + ventas_suc["Canal"] + "|" + ventas_suc["Regional"]
        )
        cumplimiento = (
            ventas_suc.groupby("KeyMeta", as_index=False)
            .agg(Venta_Neta_Real=("Venta_Neta", "sum"))
            .merge(metas, on="KeyMeta", how="left")
        )
        cumplimiento_regional = (
            cumplimiento.groupby("Regional", as_index=False)
            .agg(Venta_Neta_Real=("Venta_Neta_Real", "sum"), Meta_Venta_Neta=("Meta_Venta_Neta", "sum"))
        )
        cumplimiento_regional["Cumplimiento"] = cumplimiento_regional.apply(
            lambda r: r["Venta_Neta_Real"] / r["Meta_Venta_Neta"] if r["Meta_Venta_Neta"] > 0 else 0,
            axis=1,
        ).fillna(0)
        cumplimiento_regional = cumplimiento_regional.sort_values("Cumplimiento", ascending=False)
        for _, row in cumplimiento_regional.iterrows():
            pct = row["Cumplimiento"]
            bar_color = c["success"] if pct >= 0.9 else c["warning"] if pct >= 0.7 else c["danger"]
            progress_bar_row(
                label=row["Regional"],
                pct=pct,
                detail=f"{format_currency(row['Venta_Neta_Real'])} / {format_currency(row['Meta_Venta_Neta'])}",
                bar_color=bar_color,
            )
    else:
        empty_state("Datos de metas o regionales no disponibles.", kind="warning")

with col_req4:
    st.markdown(f"**4. CLIENTE** — Comportamiento de clientes (Dim: Segmento)")
    if clientes is not None and not clientes.empty:
        clientes_activos = ventas["ID_Cliente"].unique()
        seg_counts = clientes[clientes["ID_Cliente"].isin(clientes_activos)]["Segmento"].value_counts().reset_index()
        seg_counts.columns = ["Segmento", "Clientes"]
        if not seg_counts.empty:
            fig_seg = donut_chart(seg_counts, names="Segmento", values="Clientes", title="Clientes Activos por Segmento", color_map=SEGMENT_COLORS)
            chart_panel(fig_seg, key="gerencial_segmento")
    else:
        empty_state("Datos de clientes no disponibles.", kind="warning")

section_divider()

section_header("Tabla Resumen por Regional", "📑", "Tabla obligatoria según requerimiento", accent=c["accent"])
if "Regional" in ventas_suc.columns:
    tabla_reg = ventas_suc.groupby("Regional", as_index=False).agg(
        Venta_Neta=("Venta_Neta", "sum"),
        Margen_Bruto=("Margen_Bruto", "sum"),
        Transacciones=("ID_Transaccion", "nunique")
    ).sort_values("Venta_Neta", ascending=False)
    
    st.dataframe(
        tabla_reg, 
        use_container_width=True, 
        hide_index=True,
        column_config={
            "Regional": st.column_config.TextColumn("Regional", width="medium"),
            "Venta_Neta": st.column_config.NumberColumn("Venta Neta", format="Bs%.2f", width="medium"),
            "Margen_Bruto": st.column_config.NumberColumn("Margen Bruto", format="Bs%.2f", width="medium"),
            "Transacciones": st.column_config.NumberColumn("Transacciones", format="%d", width="small")
        }
    )

