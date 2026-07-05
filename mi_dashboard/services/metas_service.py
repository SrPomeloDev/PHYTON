import logging
from typing import Optional

import pandas as pd

from utils.cache import get_cached_dataframe

logger = logging.getLogger(__name__)


def get_metas() -> pd.DataFrame:
    df = get_cached_dataframe("metas")
    if df is None or df.empty:
        logger.warning("Datos de metas no disponibles")
        return pd.DataFrame()
    return df


def get_cumplimiento_por_regional() -> pd.DataFrame:
    ventas = get_cached_dataframe("ventas")
    metas = get_metas()
    sucursales = get_cached_dataframe("sucursales")

    if ventas is None or metas is None or sucursales is None:
        return pd.DataFrame()

    ventas_con_regional = ventas.merge(
        sucursales[["ID_Sucursal", "Regional"]], on="ID_Sucursal", how="left"
    )
    ventas_con_regional["KeyMeta"] = (
        ventas_con_regional["Año"].astype(str)
        + "|"
        + ventas_con_regional["Mes"].astype(str)
        + "|"
        + ventas_con_regional["Canal"].astype(str)
        + "|"
        + ventas_con_regional["Regional"].astype(str)
    )

    merged = ventas_con_regional.merge(
        metas[["KeyMeta", "Meta_Venta_Neta", "Meta_Margen"]],
        on="KeyMeta",
        how="left",
    )

    cumplimiento = (
        merged.groupby("Regional")
        .agg(
            venta_neta=("Venta_Neta", "sum"),
            meta_venta=("Meta_Venta_Neta", "sum"),
            margen_bruto=("Margen_Bruto", "sum"),
            meta_margen=("Meta_Margen", "sum"),
        )
        .reset_index()
    )
    cumplimiento["cumplimiento_pct"] = cumplimiento.apply(
        lambda r: r["venta_neta"] / r["meta_venta"] if r["meta_venta"] > 0 else 0,
        axis=1,
    )
    return cumplimiento.sort_values("cumplimiento_pct", ascending=False)
