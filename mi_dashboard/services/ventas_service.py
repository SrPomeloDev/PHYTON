import logging
from typing import Optional

import pandas as pd

from utils.cache import get_cached_dataframe

logger = logging.getLogger(__name__)


def get_ventas() -> pd.DataFrame:
    df = get_cached_dataframe("ventas")
    if df is None or df.empty:
        logger.warning("Datos de ventas no disponibles")
        return pd.DataFrame()
    return df


def get_ventas_filtradas(
    anio: Optional[list[int]] = None,
    mes: Optional[list[int]] = None,
    canal: Optional[list[str]] = None,
    regional: Optional[list[str]] = None,
    sucursal: Optional[list[str]] = None,
    categoria: Optional[list[str]] = None,
    ejecutivo: Optional[list[str]] = None,
) -> pd.DataFrame:
    df = get_ventas()
    if df.empty:
        return df

    productos = get_cached_dataframe("productos")
    sucursales = get_cached_dataframe("sucursales")

    if anio and "Año" in df.columns:
        df = df[df["Año"].isin(anio)]
    if mes and "Mes" in df.columns:
        df = df[df["Mes"].isin(mes)]
    if canal and "Canal" in df.columns:
        df = df[df["Canal"].isin(canal)]
    if ejecutivo and "Ejecutivo_Venta" in df.columns:
        df = df[df["Ejecutivo_Venta"].isin(ejecutivo)]

    if sucursal and "ID_Sucursal" in df.columns:
        df = df[df["ID_Sucursal"].isin(sucursal)]

    if regional and sucursales is not None and not sucursales.empty:
        suc_reg = sucursales[sucursales["Regional"].isin(regional)]["ID_Sucursal"]
        df = df[df["ID_Sucursal"].isin(suc_reg)]

    if categoria and productos is not None and not productos.empty:
        prod_cat = productos[productos["Categoria"].isin(categoria)][
            "Codigo_Producto_Homologado"
        ]
        df = df[df["Codigo_Producto_Homologado"].isin(prod_cat)]

    return df
