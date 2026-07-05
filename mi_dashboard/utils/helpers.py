from typing import Any, Callable, Optional

import pandas as pd
import streamlit as st


def safe_divide(numerator: float, denominator: float, default: float = 0.0) -> float:
    if denominator == 0:
        return default
    return numerator / denominator


def clamp(value: float, min_val: float, max_val: float) -> float:
    return max(min_val, min(max_val, value))


def semaphore_color(value: float, thresholds: list[float]) -> str:
    if value >= thresholds[0]:
        return "green"
    if value >= thresholds[1]:
        return "yellow"
    return "red"


def get_month_name(month: int) -> str:
    months = [
        "Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio",
        "Julio", "Agosto", "Septiembre", "Octubre", "Noviembre", "Diciembre",
    ]
    return months[month - 1] if 1 <= month <= 12 else str(month)


# ── Time Comparison ──────────────────────────────────────────────────────────

def _get_prev_periodo(periodo: str, months_back: int = 1) -> str:
    """Return the period N months before a YYYY-MM string."""
    year = int(periodo[:4])
    month = int(periodo[5:7])
    total = year * 12 + (month - 1) - months_back
    py = total // 12
    pm = total % 12 + 1
    return f"{py}-{pm:02d}"


def get_mom_yoy_change(
    ventas_full: pd.DataFrame,
    filtros: dict[str, Any],
    metric_func: Callable[[pd.DataFrame], float],
    productos: Optional[pd.DataFrame] = None,
    clientes: Optional[pd.DataFrame] = None,
) -> tuple[float | None, float | None]:
    """Compute (mom_pct, yoy_pct) for a metric given current filters.

    Both values are decimals (e.g. 0.15 = +15%). Returns (None, None) if
    insufficient history exists.
    """
    time_keys = {"año", "mes", "fecha_desde", "fecha_hasta"}
    nontime = {k: v for k, v in filtros.items() if k not in time_keys}
    ventas_base = apply_filters(ventas_full, nontime, productos, clientes)

    all_set = set(ventas_base["Periodo"].unique())
    años = filtros.get("año", [])
    meses = filtros.get("mes", [])
    if años and meses:
        selected = sorted(
            p for p in all_set if int(p[:4]) in años and int(p[5:7]) in meses
        )
    else:
        selected = sorted(all_set)

    if not selected:
        return None, None

    current = ventas_base[ventas_base["Periodo"].isin(selected)]
    current_val = metric_func(current)
    if current_val is None or current_val == 0:
        return None, None

    # MoM — shift each period by 1 month
    mom_periodos = [p for p in (_get_prev_periodo(p, 1) for p in selected) if p in all_set]
    mom_val = metric_func(ventas_base[ventas_base["Periodo"].isin(mom_periodos)]) if mom_periodos else None
    mom_pct = (current_val - mom_val) / mom_val if (mom_val and mom_val != 0) else None

    # YoY — shift each period by 12 months
    yoy_periodos = [p for p in (_get_prev_periodo(p, 12) for p in selected) if p in all_set]
    yoy_val = metric_func(ventas_base[ventas_base["Periodo"].isin(yoy_periodos)]) if yoy_periodos else None
    yoy_pct = (current_val - yoy_val) / yoy_val if (yoy_val and yoy_val != 0) else None

    return mom_pct, yoy_pct


# ── Drill-down ───────────────────────────────────────────────────────────────

def store_drill(label: str, dimension: str, value: Any) -> None:
    """Store a drill-down filter and navigate to Operativa page."""
    st.session_state.drill_filter = {
        "label": label,
        "dimension": dimension,
        "value": value,
    }


def clear_drill() -> None:
    st.session_state.pop("drill_filter", None)


def get_drill_filter() -> dict | None:
    """Get and clear the active drill filter (consumed once)."""
    return st.session_state.pop("drill_filter", None)


def apply_filters(
    ventas: pd.DataFrame,
    filtros: dict[str, Any],
    productos: Optional[pd.DataFrame] = None,
    clientes: Optional[pd.DataFrame] = None,
    sucursales: Optional[pd.DataFrame] = None,
) -> pd.DataFrame:
    df = ventas.copy()

    if filtros.get("año") and "Año" in df.columns:
        df = df[df["Año"].isin(filtros["año"])]
    if filtros.get("mes") and "Mes" in df.columns:
        df = df[df["Mes"].isin(filtros["mes"])]
    if filtros.get("canal") and "Canal" in df.columns:
        df = df[df["Canal"].isin(filtros["canal"])]
    if filtros.get("sucursal") and "ID_Sucursal" in df.columns:
        df = df[df["ID_Sucursal"].isin(filtros["sucursal"])]
    if filtros.get("ejecutivo") and "Ejecutivo_Venta" in df.columns:
        df = df[df["Ejecutivo_Venta"].isin(filtros["ejecutivo"])]
    if filtros.get("categoria") and productos is not None and not productos.empty:
        prods = productos[productos["Categoria"].isin(filtros["categoria"])]["Codigo_Producto_Homologado"]
        df = df[df["Codigo_Producto_Homologado"].isin(prods)]
    if filtros.get("marca") and productos is not None and not productos.empty:
        prods = productos[productos["Marca"].isin(filtros["marca"])]["Codigo_Producto_Homologado"]
        df = df[df["Codigo_Producto_Homologado"].isin(prods)]
    if filtros.get("segmento") and clientes is not None and not clientes.empty:
        ids = clientes[clientes["Segmento"].isin(filtros["segmento"])]["ID_Cliente"]
        df = df[df["ID_Cliente"].isin(ids)]
    if filtros.get("regional") and sucursales is not None and not sucursales.empty:
        suc_ids = sucursales[sucursales["Regional"].isin(filtros["regional"])]["ID_Sucursal"]
        df = df[df["ID_Sucursal"].isin(suc_ids)]

    if "Fecha" in df.columns:
        desde = filtros.get("fecha_desde")
        hasta = filtros.get("fecha_hasta")
        if desde or hasta:
            fecha_col = pd.to_datetime(df["Fecha"])
            if desde:
                df = df[fecha_col >= pd.Timestamp(desde)]
            if hasta:
                df = df[fecha_col <= pd.Timestamp(hasta)]

    return df
