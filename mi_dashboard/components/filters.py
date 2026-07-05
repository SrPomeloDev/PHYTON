import streamlit as st
from typing import Any

from services.productos_service import get_categorias
from services.clientes_service import get_segmentos
from services.ventas_service import get_ventas


def render_global_filters() -> dict[str, Any]:
    ventas = get_ventas()
    filtros = {}

    if ventas.empty:
        return filtros

    with st.container():
        cols = st.columns(4)
        with cols[0]:
            años = sorted(ventas["Año"].unique())
            filtros["año"] = st.multiselect("Año", años, default=años)
        with cols[1]:
            meses = sorted(ventas["Mes"].unique())
            filtros["mes"] = st.multiselect(
                "Mes", meses, default=meses,
                format_func=lambda x: ["Ene","Feb","Mar","Abr","May","Jun",
                                       "Jul","Ago","Sep","Oct","Nov","Dic"][x-1],
            )
        with cols[2]:
            canales = sorted(ventas["Canal"].unique())
            filtros["canal"] = st.multiselect("Canal", canales, default=canales)
        with cols[3]:
            ejecutivos = sorted(ventas["Ejecutivo_Venta"].unique())
            filtros["ejecutivo"] = st.multiselect("Ejecutivo", ejecutivos, default=ejecutivos)

    return filtros
