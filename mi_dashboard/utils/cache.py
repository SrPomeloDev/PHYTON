import logging
from typing import Optional

import pandas as pd

from utils.data_loader import load_excel_sheets
from utils.etl import (
    clean_ventas,
    clean_productos,
    clean_clientes,
    clean_sucursales,
    clean_metas,
    clean_homologacion,
    homologar_productos,
)

logger = logging.getLogger(__name__)

_data_cache: Optional[dict[str, pd.DataFrame]] = None


def _run_etl() -> dict[str, pd.DataFrame]:
    global _data_cache
    if _data_cache is not None:
        return _data_cache
    logger.info("Cache miss: cargando y transformando datos desde Excel")
    sheets = load_excel_sheets()

    ventas = clean_ventas(sheets["VENTAS"])
    productos = clean_productos(sheets["PRODUCTOS"])
    clientes = clean_clientes(sheets["CLIENTES"])
    sucursales = clean_sucursales(sheets["SUCURSAL"])
    metas = clean_metas(sheets["METAS"])
    homologacion = clean_homologacion(sheets["HOMOLOGACIÓN"])

    ventas = homologar_productos(ventas, homologacion)
    _data_cache = {
        "ventas": ventas,
        "productos": productos,
        "clientes": clientes,
        "sucursales": sucursales,
        "metas": metas,
        "homologacion": homologacion,
    }
    return _data_cache


try:
    import streamlit as st

    @st.cache_data(ttl=3600, show_spinner="Cargando datos del Excel...")
    def load_and_transform_data() -> dict[str, pd.DataFrame]:
        return _run_etl()

    @st.cache_resource(ttl=3600)
    def get_cached_dataframe(key: str) -> Optional[pd.DataFrame]:
        data = load_and_transform_data()
        return data.get(key)

except ImportError:

    def load_and_transform_data() -> dict[str, pd.DataFrame]:
        return _run_etl()

    def get_cached_dataframe(key: str) -> Optional[pd.DataFrame]:
        data = _run_etl()
        return data.get(key)
