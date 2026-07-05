import logging
from typing import Optional

import pandas as pd

from utils.cache import get_cached_dataframe

logger = logging.getLogger(__name__)


def get_productos() -> pd.DataFrame:
    df = get_cached_dataframe("productos")
    if df is None or df.empty:
        logger.warning("Datos de productos no disponibles")
        return pd.DataFrame()
    return df


def get_categorias() -> list[str]:
    df = get_productos()
    if df.empty or "Categoria" not in df.columns:
        return []
    return sorted(df["Categoria"].dropna().unique().tolist())


def get_subcategorias(categoria: Optional[str] = None) -> list[str]:
    df = get_productos()
    if df.empty or "Subcategoria" not in df.columns:
        return []
    if categoria:
        df = df[df["Categoria"] == categoria]
    return sorted(df["Subcategoria"].dropna().unique().tolist())


def get_marcas() -> list[str]:
    df = get_productos()
    if df.empty or "Marca" not in df.columns:
        return []
    return sorted(df["Marca"].dropna().unique().tolist())


def get_ranking_productos(top_n: int = 10) -> pd.DataFrame:
    ventas = get_cached_dataframe("ventas")
    productos = get_productos()
    if ventas is None or productos is None:
        return pd.DataFrame()

    merged = ventas.merge(
        productos,
        on="Codigo_Producto_Homologado",
        how="left",
    )
    ranking = (
        merged.groupby(["Codigo_Producto_Homologado", "Producto", "Categoria"])
        .agg(
            venta_neta=("Venta_Neta", "sum"),
            margen_bruto=("Margen_Bruto", "sum"),
            cantidad=("Cantidad", "sum"),
            transacciones=("ID_Transaccion", "nunique"),
        )
        .reset_index()
        .sort_values("venta_neta", ascending=False)
    )
    return ranking.head(top_n)
