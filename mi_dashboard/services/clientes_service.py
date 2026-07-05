import logging
from typing import Optional

import pandas as pd

from utils.cache import get_cached_dataframe

logger = logging.getLogger(__name__)


def get_clientes() -> pd.DataFrame:
    df = get_cached_dataframe("clientes")
    if df is None or df.empty:
        logger.warning("Datos de clientes no disponibles")
        return pd.DataFrame()
    return df


def get_segmentos() -> list[str]:
    df = get_clientes()
    if df.empty or "Segmento" not in df.columns:
        return []
    return sorted(df["Segmento"].dropna().unique().tolist())


def get_top_clientes(top_n: int = 10) -> pd.DataFrame:
    ventas = get_cached_dataframe("ventas")
    clientes = get_clientes()
    if ventas is None or clientes is None:
        return pd.DataFrame()

    merged = ventas.merge(clientes, on="ID_Cliente", how="left")
    top = (
        merged.groupby(["ID_Cliente", "Cliente", "Segmento"])
        .agg(
            compra_acumulada=("Venta_Neta", "sum"),
            transacciones=("ID_Transaccion", "nunique"),
        )
        .reset_index()
        .sort_values("compra_acumulada", ascending=False)
    )
    return top.head(top_n)
