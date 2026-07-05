import streamlit as st
import pandas as pd

from utils.cache import get_cached_dataframe
from utils.formatters import format_currency, format_percent, format_number
from utils.helpers import apply_filters, clear_drill, get_drill_filter
from components.sidebar import render_sidebar, render_sidebar_nav
from components.cards import kpi_card
from components.charts import bar_chart
from components.tables import export_to_csv
from components.layout import (
    page_header,
    section_header,
    section_divider,
    chart_panel,
    empty_state,
    mini_kpi_card,
)
from config.style import COLORS, apply_theme

apply_theme()

c = COLORS

page_header(
    title="Vista Operativa",
    subtitle="Detalle transaccional, rendimiento de ejecutivos y análisis de clientes.",
    icon="📋",
    gradient=f"linear-gradient(135deg, {c['accent']}, #22D3EE)",
)

with st.spinner("Cargando datos operativos..."):
    ventas = get_cached_dataframe("ventas")
    productos = get_cached_dataframe("productos")
    clientes = get_cached_dataframe("clientes")
    sucursales = get_cached_dataframe("sucursales")

if ventas is None or ventas.empty:
    empty_state("No hay datos disponibles para la vista operativa.", kind="warning")
    st.stop()

render_sidebar_nav()
filtros = render_sidebar()

# Apply drill-down if present (before sidebar filters so user overrides)
drill = get_drill_filter()
if drill:
    filtros[drill["dimension"]] = [drill["value"]]

ventas = apply_filters(ventas, filtros, productos, clientes, sucursales)

if drill:
    st.markdown(
        f"""
        <div class="drill-badge">
            <span>🔍</span>
            <span class="drill-label">{drill['label']}</span>
            <span style="color:rgba(255,255,255,0.2);">|</span>
            <span>usa filtros del sidebar para refinar</span>
            <span class="drill-clear" onclick="(function(){{const p=window.parent.document.querySelector('button[kind=\\'secondaryFormSubmit\\']'); if(p&&p.innerText.includes('Limpiar')) p.click();}})();">✕</span>
        </div>
        """,
        unsafe_allow_html=True,
    )
    col_clear, _ = st.columns([1, 5])
    with col_clear:
        if st.button("✕ Limpiar drill", key="clear_drill_btn", use_container_width=True):
            clear_drill()
            st.rerun()

if ventas.empty:
    empty_state("No hay datos que coincidan con los filtros seleccionados.")
    st.stop()


@st.cache_data(ttl=300, show_spinner=False)
def _build_full_dataset(v, p, cl, s):
    vp = v.merge(p, on="Codigo_Producto_Homologado", how="left") if p is not None else v.copy()
    vc = vp.merge(cl, on="ID_Cliente", how="left") if cl is not None else vp.copy()
    vf = vc.merge(s, on="ID_Sucursal", how="left") if s is not None else vc.copy()
    return vf


ventas_full = _build_full_dataset(ventas, productos, clientes, sucursales)

cols_detalle = [
    "ID_Transaccion", "Fecha", "Canal", "Cliente", "Segmento",
    "Producto", "Ejecutivo_Venta",
    "Cantidad", "Venta_Neta", "Margen_Bruto", "Margen_Pct",
]
available_cols = [col for col in cols_detalle if col in ventas_full.columns]
df_detalle = ventas_full[available_cols].copy()

section_header(
    "Detalle de Transacciones",
    "🔍",
    "Use los filtros de columna en la tabla para buscar por ID, cliente o producto.",
    c["info"],
)

col_canal, col_ejec, col_info = st.columns([2, 2, 3])
with col_canal:
    canales_opts = ["Todos"] + sorted(df_detalle["Canal"].dropna().unique().tolist()) if "Canal" in df_detalle.columns else ["Todos"]
    canal_filter = st.selectbox("Canal", canales_opts, key="op_canal")
with col_ejec:
    ejec_opts = ["Todos"] + sorted(df_detalle["Ejecutivo_Venta"].dropna().unique().tolist()) if "Ejecutivo_Venta" in df_detalle.columns else ["Todos"]
    ejec_filter = st.selectbox("Ejecutivo", ejec_opts, key="op_ejec")
with col_info:
    total_rows = len(df_detalle)
    st.markdown(
        f"""
        <div style='display: flex; align-items: center; height: 100%;'>
            <div class="stat-chip">
                <span style="font-size: 1rem;">📦</span>
                <span class="stat-chip-value">
                    {total_rows:,}
                    <span class="stat-chip-label">transacciones</span>
                </span>
                <span style="color: {c['border']};">|</span>
                <span class="stat-chip-value">
                    {df_detalle['ID_Transaccion'].nunique():,}
                    <span class="stat-chip-label">únicas</span>
                </span>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

mask = pd.Series(True, index=df_detalle.index)
if canal_filter != "Todos" and "Canal" in df_detalle.columns:
    mask &= df_detalle["Canal"] == canal_filter
if ejec_filter != "Todos" and "Ejecutivo_Venta" in df_detalle.columns:
    mask &= df_detalle["Ejecutivo_Venta"] == ejec_filter

df_filtrado = df_detalle[mask]

if df_filtrado.empty:
    empty_state("No se encontraron transacciones que coincidan con los filtros.")
else:
    total_vn = df_filtrado["Venta_Neta"].sum()
    avg_mp = df_filtrado["Margen_Bruto"].sum() / total_vn if total_vn > 0 else 0
    total_rows = len(df_filtrado)
    m1, m2, m3 = st.columns(3)
    with m1:
        mini_kpi_card("Registros", f"{total_rows:,}", c["primary"])
    with m2:
        mini_kpi_card("Venta Neta Total", f"Bs{total_vn:,.2f}", c["success"])
    with m3:
        mini_kpi_card("Margen Promedio", f"{avg_mp:.1%}", c["warning"])

    vn_max = df_filtrado["Venta_Neta"].max()
    mb_max = df_filtrado["Margen_Bruto"].max()
    margen_pct_max = max(df_filtrado["Margen_Pct"].max(), 0.01) if "Margen_Pct" in df_filtrado.columns else 0.5
    st.dataframe(
        df_filtrado.head(2000),
        use_container_width=True,
        height=420,
        hide_index=True,
        column_config={
            "ID_Transaccion": st.column_config.NumberColumn("ID", format="%d", width="small"),
            "Fecha": st.column_config.DateColumn("Fecha", width="small"),
            "Canal": st.column_config.TextColumn("Canal", width="small"),
            "Cliente": st.column_config.TextColumn("Cliente", width="large"),
            "Segmento": st.column_config.TextColumn("Segm.", width="small"),
            "Producto": st.column_config.TextColumn("Producto", width="large"),
            "Ejecutivo_Venta": st.column_config.TextColumn("Ejecutivo", width="medium"),
            "Cantidad": st.column_config.NumberColumn("Cant.", format="%d", width="small"),
            "Venta_Neta": st.column_config.NumberColumn("Vta Neta", format="Bs%.2f", width="medium"),
            "Margen_Bruto": st.column_config.NumberColumn("Margen Bruto", format="Bs%.2f", width="medium"),
            "Margen_Pct": st.column_config.ProgressColumn("Margen %", min_value=0, max_value=margen_pct_max, format="%.1f%%", width="small"),
        },
    )
    if len(df_filtrado) > 2000:
        st.caption(f"Mostrando las primeras 2,000 de {len(df_filtrado):,} filas. Use filtros para acotar.")

section_divider()

section_header("Top 10 Ejecutivos por Venta Neta", "🏅", accent=c["warning"])

if "Ejecutivo_Venta" in ventas_full.columns:
    ranking_ejec = (
        ventas_full.groupby("Ejecutivo_Venta")
        .agg(
            Venta_Neta=("Venta_Neta", "sum"),
            Transacciones=("ID_Transaccion", "nunique"),
            Clientes_Unicos=("ID_Cliente", "nunique"),
        )
        .reset_index()
        .sort_values("Venta_Neta", ascending=False)
        .head(10)
    )
    if ranking_ejec.empty:
        empty_state("Sin datos de ejecutivos.")
    else:
        fig_ejec = bar_chart(
            ranking_ejec, x="Ejecutivo_Venta", y="Venta_Neta",
            title="Top 10 Ejecutivos por Venta Neta",
        )
        chart_panel(fig_ejec, key="operativa_ejec")
else:
    empty_state("Columna Ejecutivo_Venta no disponible.")

section_divider()

section_header("Top 10 Clientes por Compra", "👥", accent=c["primary"])

if "Cliente" in ventas_full.columns:
    total_venta = ventas_full["Venta_Neta"].sum()
    top_clientes = (
        ventas_full.groupby(["ID_Cliente", "Cliente", "Segmento"])
        .agg(Venta_Neta=("Venta_Neta", "sum"), Margen_Bruto=("Margen_Bruto", "sum"), Transacciones=("ID_Transaccion", "nunique"))
        .reset_index()
    )
    top_clientes["Margen_Pct"] = top_clientes.apply(
        lambda r: r["Margen_Bruto"] / r["Venta_Neta"] if r["Venta_Neta"] > 0 else 0, axis=1
    )
    top_clientes["Ticket_Promedio"] = top_clientes.apply(
        lambda r: r["Venta_Neta"] / r["Transacciones"] if r["Transacciones"] > 0 else 0, axis=1
    )
    top_clientes = top_clientes.sort_values("Venta_Neta", ascending=False).head(10).reset_index(drop=True)
    top_clientes.index += 1
    top_clientes = top_clientes.reset_index().rename(columns={"index": "#"})
    if top_clientes.empty:
        empty_state("Sin datos de clientes.")
    else:
        pct = top_clientes["Venta_Neta"].sum() / total_venta * 100 if total_venta > 0 else 0
        st.markdown(f'<div style="font-size:0.75rem;color:{c["text_muted"]};margin-bottom:0.5rem;">Top 10 concentran <strong style="color:{c["text_primary"]};">Bs{top_clientes["Venta_Neta"].sum():,.2f}</strong> = <strong style="color:{c["warning"]};">{pct:.1f}%</strong> de la venta total</div>', unsafe_allow_html=True)
        margen_pct_max_cli = max(top_clientes["Margen_Pct"].max(), 0.01)
        st.dataframe(
            top_clientes, use_container_width=True, hide_index=True,
            column_config={
                "#": st.column_config.NumberColumn("#", format="%d", width="small"),
                "Cliente": st.column_config.TextColumn("Cliente", width="large"),
                "Segmento": st.column_config.TextColumn("Segmento", width="small"),
                "Venta_Neta": st.column_config.NumberColumn("Venta Neta", format="Bs%.2f", width="medium"),
                "Margen_Bruto": st.column_config.NumberColumn("Margen Bruto", format="Bs%.2f", width="medium"),
                "Margen_Pct": st.column_config.ProgressColumn("Margen %", min_value=0, max_value=margen_pct_max_cli, format="%.1f%%", width="small"),
                "Ticket_Promedio": st.column_config.NumberColumn("Ticket Prom.", format="Bs%.2f", width="small"),
                "Transacciones": st.column_config.NumberColumn("Trans.", format="%d", width="small"),
            },
        )
else:
    empty_state("Datos de clientes no disponibles.")

section_divider()

section_header("Transacciones con Descuento > 20%", "⚠️", accent=c["danger"])

df_descuento = ventas_full[ventas_full["Descuento_Pct"] > 0.20].copy() if "Descuento_Pct" in ventas_full.columns else pd.DataFrame()
total_desc = len(df_descuento)

col_kpi, _ = st.columns([1, 3])
with col_kpi:
    kpi_card("Trans. Desc. >20%", format_number(float(total_desc)), color=c["danger"], icon="⚠️")

if total_desc > 0:
    cols_descuento = [
        "ID_Transaccion", "Fecha", "Canal", "Cliente", "Segmento",
        "Ejecutivo_Venta", "Producto", "Cantidad",
        "Venta_Bruta", "Descuento_Pct", "Descuento_Valor", "Venta_Neta", "Margen_Bruto",
    ]
    avail_desc = [col for col in cols_descuento if col in df_descuento.columns]
    total_desc_bs = df_descuento["Descuento_Valor"].sum()
    avg_desc_pct = df_descuento["Descuento_Pct"].mean()
    m1, m2, m3 = st.columns(3)
    with m1:
        mini_kpi_card("Trans. Afectadas", f"{total_desc:,}", c["danger"])
    with m2:
        mini_kpi_card("Total Descuento", f"Bs{total_desc_bs:,.2f}", c["warning"])
    with m3:
        mini_kpi_card("Desc. Promedio", f"{avg_desc_pct:.1%}", c["primary"])
    dv_max = df_descuento["Descuento_Valor"].max()
    vn_max = df_descuento["Venta_Neta"].max()
    st.dataframe(
        df_descuento[avail_desc].head(2000), use_container_width=True, hide_index=True,
        column_config={
            "ID_Transaccion": st.column_config.NumberColumn("ID", format="%d", width="small"),
            "Fecha": st.column_config.DateColumn("Fecha", width="small"),
            "Canal": st.column_config.TextColumn("Canal", width="small"),
            "Cliente": st.column_config.TextColumn("Cliente", width="large"),
            "Segmento": st.column_config.TextColumn("Segm.", width="small"),
            "Ejecutivo_Venta": st.column_config.TextColumn("Ejecutivo", width="medium"),
            "Producto": st.column_config.TextColumn("Producto", width="large"),
            "Cantidad": st.column_config.NumberColumn("Cant.", format="%d", width="small"),
            "Venta_Bruta": st.column_config.NumberColumn("Vta Bruta", format="Bs%.2f", width="medium"),
            "Descuento_Pct": st.column_config.ProgressColumn("Desc. %", min_value=0, max_value=1, format="%.1f%%", width="small"),
            "Descuento_Valor": st.column_config.NumberColumn("Desc. Bs", format="Bs%.2f", width="medium"),
            "Venta_Neta": st.column_config.NumberColumn("Vta Neta", format="Bs%.2f", width="medium"),
            "Margen_Bruto": st.column_config.NumberColumn("Margen Bruto", format="Bs%.2f", width="medium"),
        },
    )
    if len(df_descuento) > 2000:
        st.caption(f"Mostrando las primeras 2,000 de {len(df_descuento):,} filas. Use filtros para acotar.")
else:
    st.success("No hay transacciones con descuento superior al 20%.")

section_divider()

if not df_filtrado.empty:
    export_to_csv(df_filtrado, filename="detalle_transacciones.csv")
