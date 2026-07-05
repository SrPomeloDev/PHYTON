import datetime
from typing import Any, Optional

import pandas as pd
import streamlit as st

from config.style import COLORS
from utils.cache import get_cached_dataframe
from services.asistente_ia import render_chat_ia


def _filter_key(name: str) -> str:
    return f"filtro_{name}"


def _toggle(key: str, options: list, select: bool):
    if select:
        st.session_state[key] = list(options)
    else:
        st.session_state[key] = []


def _set_periodo_rapido(max_date: datetime.date, periodo: str):
    """Store pending period; actual state is applied on next run BEFORE widgets."""
    st.session_state._pending_periodo = {"max_date": max_date, "periodo": periodo}
    st.rerun()


def _apply_pending_periodo():
    pending = st.session_state.pop("_pending_periodo", None)
    if not pending:
        return
    max_date = pending["max_date"]
    periodo = pending["periodo"]
    año = max_date.year
    mes = max_date.month
    if periodo == "MTD":
        desde = datetime.date(año, mes, 1)
        hasta = max_date
        meses = [mes]
    elif periodo == "QTD":
        trimestre = (mes - 1) // 3 + 1
        desde = datetime.date(año, 3 * trimestre - 2, 1)
        hasta = max_date
        meses = {1: [1, 2, 3], 2: [4, 5, 6], 3: [7, 8, 9], 4: [10, 11, 12]}[trimestre]
    elif periodo == "YTD":
        desde = datetime.date(año, 1, 1)
        hasta = max_date
        meses = list(range(1, mes + 1))
    else:
        return
    st.session_state.filtro_fecha_desde = desde
    st.session_state.filtro_fecha_hasta = hasta
    st.session_state.filtro_año = [año]
    st.session_state.filtro_mes = meses
    st.session_state._periodo_activo = periodo


def _multiselect_row(
    label: str,
    options: list,
    key: str,
    default: Optional[list] = None,
    format_func=None,
) -> list:
    if default is None:
        default = list(options)
    if f"_{key}_options" not in st.session_state:
        st.session_state[f"_{key}_options"] = list(options)

    st.markdown(f"<div class='filter-label'>{label}</div>", unsafe_allow_html=True)

    kwargs = dict(
        label=label,
        options=options,
        default=default,
        key=key,
        label_visibility="collapsed",
    )
    if format_func is not None:
        kwargs["format_func"] = format_func

    cols = st.columns([7, 1, 1])
    with cols[0]:
        sel = st.multiselect(**kwargs)
    with cols[1]:
        st.button(
            "✓",
            key=f"sel_{key}",
            help="Seleccionar todo",
            on_click=_toggle,
            args=(key, options, True),
        )
    with cols[2]:
        st.button(
            "✕",
            key=f"clr_{key}",
            help="Limpiar selección",
            on_click=_toggle,
            args=(key, options, False),
        )
    return sel if sel else []


def _count_active_filters(filtros: dict[str, Any], ventas: pd.DataFrame) -> int:
    """Cuenta cuántos filtros están activos (selección parcial)."""
    active = 0
    checks = [
        ("año", sorted(ventas["Año"].unique()) if "Año" in ventas.columns else []),
        ("mes", sorted(ventas["Mes"].unique()) if "Mes" in ventas.columns else []),
        ("canal", sorted(ventas["Canal"].unique()) if "Canal" in ventas.columns else []),
        ("sucursal", sorted(ventas["ID_Sucursal"].unique()) if "ID_Sucursal" in ventas.columns else []),
        ("ejecutivo", sorted(ventas["Ejecutivo_Venta"].unique()) if "Ejecutivo_Venta" in ventas.columns else []),
    ]
    for key, full in checks:
        sel = filtros.get(key, [])
        if sel and full and len(sel) < len(full):
            active += 1
    if filtros.get("fecha_desde") or filtros.get("fecha_hasta"):
        if "Fecha" in ventas.columns:
            full_min = ventas["Fecha"].min()
            full_max = ventas["Fecha"].max()
            sel_desde = filtros.get("fecha_desde")
            sel_hasta = filtros.get("fecha_hasta")
            if sel_desde and sel_desde > full_min:
                active += 1
            if sel_hasta and sel_hasta < full_max:
                active += 1
    return active


def render_sidebar_nav() -> None:
    """Renderiza marca y navegacion en el sidebar (visible en todas las paginas)."""
    c = COLORS
    with st.sidebar:
        st.markdown(
            f"""
            <div class="sidebar-brand">
                <div class="sidebar-brand-logo">🏢</div>
                <div class="sidebar-brand-name">Comercial Andina</div>
                <div class="sidebar-brand-tag">Dashboard Comercial v2.0</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
        st.markdown(
            "<div class='nav-section'>Navegación</div>",
            unsafe_allow_html=True,
        )
        for page, icon, label in [
            ("app.py", "🏠", "Inicio"),
            ("pages/1_Gerencial.py", "📊", "Vista Gerencial"),
            ("pages/2_Estrategica.py", "📈", "Vista Estratégica"),
            ("pages/3_Operativa.py", "📋", "Vista Operativa"),
        ]:
            st.page_link(page, label=f"{icon}  {label}", width="stretch")
        st.markdown(
            "<div style='height:1px; background: linear-gradient(90deg, transparent, rgba(99,102,241,0.3), transparent); margin: 0.5rem 0 0.8rem 0;'></div>",
            unsafe_allow_html=True,
        )

        render_chat_ia()


def render_sidebar() -> dict[str, Any]:
    _apply_pending_periodo()

    if "filtros" not in st.session_state:
        st.session_state.filtros = {}

    ventas = get_cached_dataframe("ventas")
    productos = get_cached_dataframe("productos")
    filtros: dict[str, Any] = {}

    with st.sidebar:
        c = COLORS

    if ventas is None or ventas.empty:
        with st.sidebar:
            st.info("No hay datos disponibles")
        return {}

    with st.sidebar:
        with st.expander("📅 Filtros de Tiempo", expanded=True):
            años = sorted(ventas["Año"].unique())
            meses = sorted(ventas["Mes"].unique())
            filtros["año"] = _multiselect_row("Año", años, _filter_key("año"))
            filtros["mes"] = _multiselect_row(
                "Mes",
                meses,
                _filter_key("mes"),
                format_func=lambda x: [
                    "Ene", "Feb", "Mar", "Abr", "May", "Jun",
                    "Jul", "Ago", "Sep", "Oct", "Nov", "Dic",
                ][x - 1],
            )
            
            st.markdown("<div style='margin-top: 0.8rem; margin-bottom: 0.2rem; font-size: 0.8rem; color: #94A3B8;'>⏱️ Selección Rápida</div>", unsafe_allow_html=True)
            max_date = ventas["Fecha"].max()
            min_date = ventas["Fecha"].min()
            qt_cols = st.columns(3)
            with qt_cols[0]:
                if st.button("MTD", use_container_width=True, help="Mes a la fecha"):
                    _set_periodo_rapido(max_date, "MTD")
            with qt_cols[1]:
                if st.button("QTD", use_container_width=True, help="Trimestre a la fecha"):
                    _set_periodo_rapido(max_date, "QTD")
            with qt_cols[2]:
                if st.button("YTD", use_container_width=True, help="Año a la fecha"):
                    _set_periodo_rapido(max_date, "YTD")

            periodo_activo = st.session_state.pop("_periodo_activo", None)
            if periodo_activo:
                st.caption(f"✅ {periodo_activo} activo — edita Año/Mes para borrar")

            st.markdown("<div style='margin-top: 0.8rem; margin-bottom: 0.2rem; font-size: 0.8rem; color: #94A3B8;'>Rango Exacto (Opcional)</div>", unsafe_allow_html=True)
            fecha_default = (
                st.session_state.get("filtro_fecha_desde", min_date),
                st.session_state.get("filtro_fecha_hasta", max_date),
            )
            date_val = st.date_input(
                "Rango de fechas",
                value=fecha_default,
                min_value=min_date,
                max_value=max_date,
                label_visibility="collapsed",
            )
            if isinstance(date_val, tuple) and len(date_val) == 2:
                filtros["fecha_desde"] = date_val[0]
                filtros["fecha_hasta"] = date_val[1]
            elif isinstance(date_val, datetime.date):
                filtros["fecha_desde"] = date_val
                filtros["fecha_hasta"] = date_val

        with st.expander("🏢 Filtros Comerciales", expanded=False):
            canales = sorted(ventas["Canal"].unique())
            ejecutivos = sorted(ventas["Ejecutivo_Venta"].unique())
            sucursales_list = sorted(ventas["ID_Sucursal"].unique())
            filtros["canal"] = _multiselect_row("Canal", canales, _filter_key("canal"))
            filtros["sucursal"] = _multiselect_row(
                "Sucursal",
                sucursales_list,
                _filter_key("sucursal"),
                format_func=lambda x: f"ID {x}",
            )
            filtros["ejecutivo"] = _multiselect_row(
                "Ejecutivo", ejecutivos, _filter_key("ejecutivo")
            )

        with st.expander("🏷️ Producto & Cliente", expanded=False):
            if productos is not None and not productos.empty:
                categorias = sorted(productos["Categoria"].dropna().unique())
                filtros["categoria"] = _multiselect_row(
                    "Categoría", categorias, _filter_key("categoria")
                )
                mask = (
                    productos["Categoria"].isin(filtros["categoria"])
                    if filtros.get("categoria")
                    else pd.Series(True, index=productos.index)
                )
                marcas_disp = sorted(productos.loc[mask, "Marca"].dropna().unique())
                filtros["marca"] = _multiselect_row(
                    "Marca", marcas_disp, _filter_key("marca")
                )
            else:
                filtros["categoria"] = []
                filtros["marca"] = []

            clientes = get_cached_dataframe("clientes")
            if clientes is not None and not clientes.empty and "Segmento" in clientes.columns:
                segmentos = sorted(clientes["Segmento"].dropna().unique())
                filtros["segmento"] = _multiselect_row(
                    "Segmento", segmentos, _filter_key("segmento")
                )
            else:
                filtros["segmento"] = []

        active_count = _count_active_filters(filtros, ventas)
        if active_count > 0:
            st.markdown(
                f"<div style='text-align:center; margin: 0.5rem 0;'>"
                f"<span class='filter-badge'>{active_count} filtro{'s' if active_count > 1 else ''} activo{'s' if active_count > 1 else ''}</span>"
                f"</div>",
                unsafe_allow_html=True,
            )

        st.markdown(
            "<div style='height:1px; background: linear-gradient(90deg, transparent, rgba(99,102,241,0.2), transparent); margin: 0.8rem 0;'></div>",
            unsafe_allow_html=True,
        )

        if st.button("🔄 Restablecer filtros", use_container_width=True):
            for key in list(st.session_state.keys()):
                if key.startswith("filtro_") or key == "_periodo_activo":
                    del st.session_state[key]
            st.rerun()

        st.markdown(
            "<div style='color: rgba(255,255,255,0.15); font-size: 0.58rem; text-align: center; padding: 0.5rem 0 0.2rem 0; letter-spacing: 0.5px;'>Comercial Andina S.A. © 2025</div>",
            unsafe_allow_html=True,
        )

        return filtros
