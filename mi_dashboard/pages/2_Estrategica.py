import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go

from utils.cache import get_cached_dataframe
from utils.formatters import format_currency, format_percent
from utils.helpers import apply_filters, store_drill
from components.sidebar import render_sidebar, render_sidebar_nav
from components.charts import bar_chart, treemap, pareto_chart
from components.layout import (
    page_header,
    section_header,
    section_divider,
    chart_panel,
    empty_state,
)
from config.style import COLORS, apply_theme, CHART_COLORS

apply_theme()

c = COLORS

page_header(
    title="Vista Estratégica",
    subtitle="Rentabilidad por categoría, ranking de productos y análisis de portafolio.",
    icon="📈",
    gradient=f"linear-gradient(135deg, {c['success']}, #34D399)",
)

with st.spinner("Cargando datos estratégicos..."):
    ventas = get_cached_dataframe("ventas")
    productos = get_cached_dataframe("productos")
    sucursales = get_cached_dataframe("sucursales")

if ventas is None or ventas.empty or productos is None or productos.empty:
    empty_state("Datos insuficientes para la vista estratégica.", kind="warning")
    st.stop()

render_sidebar_nav()
filtros = render_sidebar()
ventas = apply_filters(ventas, filtros, productos)
if ventas.empty:
    empty_state("No hay datos que coincidan con los filtros seleccionados.")
    st.stop()


@st.cache_data(ttl=300, show_spinner=False)
def _build_product_data(v, p):
    return v.merge(p, on="Codigo_Producto_Homologado", how="left")


df = _build_product_data(ventas, productos)

section_header("Rentabilidad por Categoría", "💰", accent=c["warning"])

cat_rent = (
    df.groupby("Categoria", as_index=False)
    .agg(Venta_Neta=("Venta_Neta", "sum"), Margen_Bruto=("Margen_Bruto", "sum"))
)
cat_rent["Margen_Pct"] = cat_rent.apply(
    lambda r: r["Margen_Bruto"] / r["Venta_Neta"] if r["Venta_Neta"] > 0 else 0, axis=1
)
cat_rent = cat_rent.sort_values("Margen_Pct", ascending=False)

if cat_rent.empty:
    empty_state("No hay datos de rentabilidad por categoría.")
else:
    fig_cat_rent = bar_chart(
        cat_rent.sort_values("Margen_Bruto", ascending=True),
        x="Margen_Bruto", y="Categoria",
        title="Margen Bruto por Categoría", orientation="h",
    )
    chart_panel(fig_cat_rent, key="estrategica_cat_rent")
    cols_drill_cat = st.columns(min(len(cat_rent), 5))
    for i, (_, row) in enumerate(cat_rent.head(5).iterrows()):
        with cols_drill_cat[i % len(cols_drill_cat)]:
            if st.button(f"🔍 {row['Categoria']}", key=f"est_drill_cat_{row['Categoria']}", help=f"Transacciones de {row['Categoria']}"):
                store_drill(f"Categoría: {row['Categoria']}", "categoria", row["Categoria"])
                st.switch_page("pages/3_Operativa.py")

    cat_cols = st.columns(len(cat_rent) if len(cat_rent) <= 5 else 5)
    for i, (_, row) in enumerate(cat_rent.head(5).iterrows()):
        mpct = row["Margen_Pct"]
        if mpct >= 0.25:
            chip_color = c["success"]
            chip_bg = c["green_light"]
        elif mpct >= 0.15:
            chip_color = c["warning"]
            chip_bg = c["orange_light"]
        else:
            chip_color = c["danger"]
            chip_bg = c["red_light"]

        with cat_cols[i % len(cat_cols)]:
            st.markdown(
                f"""
                <div style="
                    background: rgba(255,255,255,0.03);
                    border: 1px solid {c['border']};
                    border-radius: 14px;
                    padding: 0.8rem;
                    text-align: center;
                    animation: fadeInUp 0.5s ease-out {0.05 * i}s both;
                ">
                    <div style="color: {c['text_muted']}; font-size: 0.65rem; font-weight: 700;
                                text-transform: uppercase; letter-spacing: 0.5px; margin-bottom: 0.3rem;">
                        {row['Categoria']}
                    </div>
                    <div style="color: {c['text_primary']}; font-size: 1rem; font-weight: 800;">
                        {format_currency(row['Margen_Bruto'])}
                    </div>
                    <div style="
                        display: inline-block; margin-top: 0.3rem;
                        background: {chip_bg}; color: {chip_color};
                        padding: 0.1rem 0.5rem; border-radius: 20px;
                        font-size: 0.68rem; font-weight: 700;
                    ">{format_percent(mpct)}</div>
                </div>
                """,
                unsafe_allow_html=True,
            )

section_divider()

section_header("Distribución por Región y Ciudad", "🌍", accent=c["primary"])

suc_exists = sucursales is not None and not sucursales.empty
if suc_exists:
    ventas_suc = ventas.merge(sucursales, on="ID_Sucursal", how="left")
    if not ventas_suc.empty and "Regional" in ventas_suc.columns:
        reg_data = ventas_suc.groupby("Regional", as_index=False)["Venta_Neta"].sum().sort_values("Venta_Neta", ascending=False)
        col_reg, col_ciudad = st.columns(2)
        with col_reg:
            fig_reg = bar_chart(reg_data, x="Regional", y="Venta_Neta", title="Venta Neta por Regional")
            chart_panel(fig_reg, key="estrategica_regional")
            for regional in reg_data["Regional"].head(6):
                if st.button(f"🔍 {regional}", key=f"drill_reg_{regional}"):
                    store_drill(f"Regional: {regional}", "regional", regional)
                    st.switch_page("pages/3_Operativa.py")
        with col_ciudad:
            if "Ciudad" in ventas_suc.columns:
                ciudad_data = ventas_suc.groupby("Ciudad", as_index=False)["Venta_Neta"].sum().sort_values("Venta_Neta", ascending=False).head(10)
                fig_ciudad = bar_chart(ciudad_data, x="Venta_Neta", y="Ciudad", title="Top 10 Ciudades por Venta Neta", orientation="h")
                chart_panel(fig_ciudad, key="estrategica_ciudad")
else:
    empty_state("Datos de sucursales no disponibles.")

section_divider()

section_header("Ranking de Productos", "🏆", accent=c["primary"])

prod_agg = df.groupby("Producto", as_index=False)["Venta_Neta"].sum().dropna()

if prod_agg.empty:
    empty_state("No hay datos de productos.")
else:
    top10 = prod_agg.sort_values("Venta_Neta", ascending=False).head(10)
    bottom10 = prod_agg.sort_values("Venta_Neta", ascending=True).head(10)

    col_top, col_bottom = st.columns(2)
    with col_top:
        fig_top = bar_chart(top10, x="Venta_Neta", y="Producto", title="Top 10 — Mayor Venta Neta", orientation="h")
        chart_panel(fig_top, key="estrategica_top10")
    with col_bottom:
        fig_bottom = bar_chart(bottom10, x="Venta_Neta", y="Producto", title="Bottom 10 — Menor Venta Neta", orientation="h")
        chart_panel(fig_bottom, key="estrategica_bottom10")

section_divider()

section_header("Matriz Venta vs Margen", "🎯", "Top 30 productos · cuadrantes de rentabilidad", accent=c["accent"])

disp = (
    df.groupby(["Producto", "Categoria"], as_index=False)
    .agg(Venta_Neta=("Venta_Neta", "sum"), Margen_Bruto=("Margen_Bruto", "sum"), Cantidad=("Cantidad", "sum"))
)
disp["Margen_Pct"] = disp.apply(lambda r: r["Margen_Bruto"] / r["Venta_Neta"] if r["Venta_Neta"] > 0 else 0, axis=1)

if disp.empty:
    empty_state("Sin datos para el gráfico.")
else:
    top = disp.nlargest(30, "Venta_Neta").copy()
    avg_margen = top["Margen_Pct"].mean()
    avg_venta = top["Venta_Neta"].mean()

    cat_palette = {cat: CHART_COLORS[i % len(CHART_COLORS)] for i, cat in enumerate(sorted(top["Categoria"].unique()))}

    fig = go.Figure()

    # Background quadrant rectangles
    x_max = top["Venta_Neta"].max() * 1.15
    y_max = top["Margen_Pct"].max() * 1.2
    fig.add_shape(type="rect", x0=avg_venta, x1=x_max, y0=avg_margen, y1=y_max,
                  fillcolor="rgba(16,185,129,0.04)", line_width=0, layer="below")
    fig.add_shape(type="rect", x0=0, x1=avg_venta, y0=avg_margen, y1=y_max,
                  fillcolor="rgba(6,182,212,0.04)", line_width=0, layer="below")
    fig.add_shape(type="rect", x0=avg_venta, x1=x_max, y0=0, y1=avg_margen,
                  fillcolor="rgba(245,158,11,0.04)", line_width=0, layer="below")
    fig.add_shape(type="rect", x0=0, x1=avg_venta, y0=0, y1=avg_margen,
                  fillcolor="rgba(239,68,68,0.04)", line_width=0, layer="below")

    # Single trace — color by category, symbol by quadrant
    def _quad_symbol(mp, vn):
        if mp >= avg_margen and vn >= avg_venta:
            return "star", "⭐"
        elif mp >= avg_margen and vn < avg_venta:
            return "diamond", "🔍"
        elif mp < avg_margen and vn >= avg_venta:
            return "triangle-up", "⚠️"
        return "x", "❌"

    top["sym"], top["sym_label"] = zip(*top.apply(lambda r: _quad_symbol(r["Margen_Pct"], r["Venta_Neta"]), axis=1))

    for cat in sorted(top["Categoria"].unique()):
        subset = top[top["Categoria"] == cat]
        if subset.empty:
            continue
        fig.add_trace(go.Scatter(
            x=subset["Venta_Neta"],
            y=subset["Margen_Pct"],
            mode="markers+text",
            name=cat,
            legendgroup=cat,
            text=subset["sym_label"],
            textposition="middle center",
            textfont=dict(size=9),
            marker=dict(
                size=np.clip(np.sqrt(subset["Cantidad"] / subset["Cantidad"].max()) * 55 + 14, 14, 65),
                sizemode="area",
                color=cat_palette[cat],
                symbol=subset["sym"],
                line=dict(width=2, color="#0B0F19"),
                opacity=0.88,
            ),
            customdata=subset[["Producto", "Cantidad", "Categoria", "sym_label"]],
            hovertemplate=(
                "<b>%{customdata[0]}</b><br>"
                "Categoría: %{customdata[2]}<br>"
                "Venta Neta: Bs%{x:,.2f}<br>"
                "Margen: %{y:.1%}<br>"
                "Cantidad: %{customdata[1]:,.0f}<br>"
                "Cuadrante: %{customdata[3]}"
                "<extra></extra>"
            ),
        ))

    # Reference lines
    fig.add_hline(y=avg_margen, line_dash="dash", line_color="rgba(255,255,255,0.3)", line_width=1)
    fig.add_vline(x=avg_venta, line_dash="dash", line_color="rgba(255,255,255,0.3)", line_width=1)

    # Quadrant labels
    fig.add_annotation(x=x_max * 0.8, y=y_max * 0.92,
                       text="⬆ Alto margen · Alta venta ⬆",
                       showarrow=False, font=dict(size=9, color=c["success"]), opacity=0.6)
    fig.add_annotation(x=x_max * 0.8, y=avg_margen * 0.65,
                       text="⬇ Bajo margen · Alta venta ⬇",
                       showarrow=False, font=dict(size=9, color=c["warning"]), opacity=0.6)
    fig.add_annotation(x=avg_venta * 0.45, y=y_max * 0.92,
                       text="⬆ Alto margen · Baja venta ⬆",
                       showarrow=False, font=dict(size=9, color=c["accent"]), opacity=0.6)
    fig.add_annotation(x=avg_venta * 0.45, y=avg_margen * 0.65,
                       text="⬇ Bajo margen · Baja venta ⬇",
                       showarrow=False, font=dict(size=9, color=c["danger"]), opacity=0.6)

    fig.update_layout(
        title=f"Venta Neta vs Margen % — Top 30 | prom. margen {avg_margen:.1%} | prom. venta Bs{avg_venta:,.0f}",
        xaxis_title="Venta Neta (Bs)",
        yaxis_title="Margen %",
        yaxis_tickformat=".0%",
        xaxis=dict(tickprefix="Bs", showgrid=True, gridcolor="rgba(255,255,255,0.04)",
                   title_font=dict(size=11, color=c["text_muted"]),
                   tickfont=dict(size=10, color=c["text_muted"]),
                   zeroline=False, showline=True, linecolor="rgba(255,255,255,0.08)"),
        yaxis=dict(showgrid=True, gridcolor="rgba(255,255,255,0.04)",
                   title_font=dict(size=11, color=c["text_muted"]),
                   tickfont=dict(size=10, color=c["text_muted"]),
                   zeroline=False, showline=False),
        hovermode="closest",
        hoverlabel=dict(bgcolor="#1E293B", font_size=12,
                        font_color=c["text_primary"], bordercolor="rgba(99,102,241,0.3)"),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1,
                    font=dict(size=10, color=c["text_muted"]), bgcolor="rgba(0,0,0,0)"),
        margin=dict(l=16, r=16, t=60, b=16),
        height=500,
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
        font_family="Inter, sans-serif",
        font_color=c["text_secondary"],
    )
    chart_panel(fig, key="estrategica_disp")

    # Quadrant summary cards
    qlabels = {"star": ("⭐ Estrella", "Alto margen + alta venta", c["success"]),
               "diamond": ("🔍 Potencial", "Alto margen + baja venta", c["accent"]),
               "triangle-up": ("⚠️ Volumen", "Bajo margen + alta venta", c["warning"]),
               "x": ("❌ Revisar", "Bajo margen + baja venta", c["danger"])}
    qcols = st.columns(4)
    for col_idx, (sym, (name, desc, color)) in enumerate(zip(qlabels, qlabels.values())):
        sym_key = list(qlabels.keys())[col_idx]
        count = (top["sym"] == sym_key).sum()
        vn_sum = top.loc[top["sym"] == sym_key, "Venta_Neta"].sum()
        with qcols[col_idx]:
            st.markdown(
                f"""
                <div style="text-align:center; padding:0.5rem; border:1px solid {c['border']};
                     border-radius:12px; border-top:2px solid {color};
                     background:rgba(255,255,255,0.02);">
                    <div style="font-size:1.2rem; font-weight:800; color:{color};">{count}</div>
                    <div style="font-size:0.65rem; font-weight:700; color:{c['text_muted']};">{name}</div>
                    <div style="font-size:0.55rem; color:{c['text_muted']}; opacity:0.5;">{desc}</div>
                    <div style="font-size:0.6rem; color:{c['text_muted']}; opacity:0.4;">{vn_sum:,.0f} Bs</div>
                </div>
                """,
                unsafe_allow_html=True,
            )

section_divider()

section_header("Distribución Jerárquica", "🗂️", accent=c["secondary"])

treemap_data = (
    df.groupby(["Categoria", "Subcategoria", "Producto"], as_index=False)["Venta_Neta"]
    .sum().dropna()
)
if treemap_data.empty:
    empty_state("Sin datos para el treemap.")
else:
    fig_tree = treemap(
        treemap_data, path=["Categoria", "Subcategoria", "Producto"],
        values="Venta_Neta",
        title="Distribución por Categoría → Subcategoría → Producto",
        color="Venta_Neta",
    )
    chart_panel(fig_tree, key="estrategica_treemap")

section_divider()

section_header("Análisis ABC / Pareto", "📊", accent=c["danger"])

pareto_data = df.groupby("Producto", as_index=False)["Venta_Neta"].sum().dropna().sort_values("Venta_Neta", ascending=False)
if pareto_data.empty:
    empty_state("Sin datos para el análisis de Pareto.")
else:
    fig_pareto = pareto_chart(
        pareto_data, item_col="Producto", value_col="Venta_Neta",
        title="Concentración de Venta Neta por Producto",
    )
    chart_panel(fig_pareto, key="estrategica_pareto")

section_divider()

section_header("Productos de Baja Rentabilidad", "⚠️", "Margen ponderado < 5%. Se ordenan de menor a mayor margen.", accent=c["danger"])

prod_margen = (
    df.groupby(["Producto", "Categoria", "Subcategoria", "Marca"], as_index=False)
    .agg(Venta_Neta=("Venta_Neta", "sum"), Margen_Bruto=("Margen_Bruto", "sum"), Cantidad=("Cantidad", "sum"))
)
prod_margen["Margen_Pct"] = prod_margen.apply(
    lambda r: r["Margen_Bruto"] / r["Venta_Neta"] if r["Venta_Neta"] > 0 else 0, axis=1
)
baja_rent = prod_margen[prod_margen["Margen_Pct"] < 0.05].sort_values("Margen_Pct", ascending=True)

if baja_rent.empty:
    st.success("✅ No se encontraron productos con margen ponderado inferior al 5%.")
else:
    show = baja_rent.head(50).copy()
    show["Impacto"] = show["Venta_Neta"] / baja_rent["Venta_Neta"].sum()
    total_afectado = baja_rent["Venta_Neta"].sum()
    st.markdown(f'<div style="font-size:0.75rem;color:{c["text_muted"]};margin-bottom:0.5rem;">{len(baja_rent)} productos con margen &lt; 5% · Ventas afectadas: <strong style="color:{c["danger"]};">Bs{total_afectado:,.2f}</strong> · <strong style="color:{c["warning"]};">{total_afectado / disp["Venta_Neta"].sum() * 100:.1f}%</strong> del total</div>', unsafe_allow_html=True)
    fig_br, tbl_col = st.columns([1, 1])
    with fig_br:
        fig_br_chart = bar_chart(
            show.nlargest(15, "Margen_Bruto"),
            x="Producto", y="Margen_Bruto",
            title="Top 15 Pérdida de Margen (Bs)",
        )
        chart_panel(fig_br_chart, key="estrategica_baja_rent")
    with tbl_col:
        vn_max = show["Venta_Neta"].max()
        mb_min = show["Margen_Bruto"].min()
        mb_max = show["Margen_Bruto"].max()
        st.dataframe(
            show,
            use_container_width=True, hide_index=True,
            column_config={
                "Producto": st.column_config.TextColumn("Producto", width="large"),
                "Categoria": st.column_config.TextColumn("Cat.", width="small"),
                "Subcategoria": st.column_config.TextColumn("Subcat.", width="small"),
                "Marca": st.column_config.TextColumn("Marca", width="small"),
                "Venta_Neta": st.column_config.NumberColumn("Venta Neta", format="Bs%.2f", width="medium"),
                "Margen_Bruto": st.column_config.NumberColumn("Margen Bruto", format="Bs%.2f", width="medium"),
                "Margen_Pct": st.column_config.ProgressColumn("Margen %", min_value=0, max_value=0.05, format="%.2%%", width="small"),
                "Cantidad": st.column_config.NumberColumn("Cant.", format="%d", width="small"),
                "Impacto": st.column_config.ProgressColumn("Impacto", format="%.1%%", min_value=0, max_value=1, width="small"),
            },
        )
    if len(baja_rent) > 50:
        st.caption(f"Mostrando los 50 productos con margen más crítico de {len(baja_rent)} en total.")
