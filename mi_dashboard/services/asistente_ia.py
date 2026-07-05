import logging
from typing import Optional

import pandas as pd
import streamlit as st

from utils.cache import get_cached_dataframe
from utils.helpers import apply_filters
from utils.metrics import (
    get_venta_neta,
    get_margen_bruto,
    get_margen_pct,
    get_ticket_promedio,
    get_cantidad_vendida,
    get_clientes_activos,
    get_cumplimiento_meta,
)
from utils.formatters import format_currency, format_percent, format_number
from config.style import COLORS

logger = logging.getLogger(__name__)

DASHBOARD_CONTEXT = """
INFORMACION COMPLETA DEL DASHBOARD COMERCIAL ANDINA S.A.:

=============================================
ESTRUCTURA DE DATOS (ESQUEMA ESTRELLA):
=============================================

=== TABLA HECHO: VENTAS (9,804 registros confirmados) ===
Columnas:
- ID_Transaccion (str): Identificador unico (T000001...)
- Fecha_Hora_Transaccion (datetime): Fecha y hora de la venta
- Codigo_Producto (str): Codigo original del producto (P001...)
- ID_Cliente (str): ID del cliente (C0001...)
- ID_Sucursal (str): ID sucursal (S001...)
- Canal (str): 4 canales (Distribuidor, Corporativo, Tienda Fisica, E-commerce)
- Cantidad (int): Unidades vendidas (1-200)
- Precio_Unitario (float): Precio por unidad en Bs
- Descuento_Pct (float): Descuento (0-50%)
- Costo_Unitario (float): Costo por unidad en Bs
- Ejecutivo_Venta (str): 15 ejecutivos
- Estado_Venta (str): Confirmada / Anulada

Campos derivados (calculados en ETL):
- Venta_Bruta = Cantidad * Precio_Unitario
- Descuento_Valor = Venta_Bruta * Descuento_Pct
- Venta_Neta = Venta_Bruta - Descuento_Valor
- Costo_Total = Cantidad * Costo_Unitario
- Margen_Bruto = Venta_Neta - Costo_Total
- Margen_Pct = Margen_Bruto / Venta_Neta
- Rango_Venta: Minimo / Bajo / Medio / Alto / Premium
- Periodo: "YYYY-MM"
- Ano, Mes (enteros), Fecha (date)

=== TABLA DIMENSION: PRODUCTOS (120 productos) ===
- Codigo_Producto_Homologado (int): PK 1-120
- Producto (str): Nombre del producto
- Categoria (str): 8 categorias (Bebidas, Lacteos, Panaderia, Limpieza, Cuidado Personal, Mascotas, Abarrotes, Congelados)
- Subcategoria (str): 32 subcategorias
- Marca (str): 10 marcas (NaturaMax, AndinaFresh, CleanHome, PetLove, etc.)
- Estado_Producto (str): Activo, Inactivo, Descontinuado
- Precio_Lista (float): Precio de lista en Bs
- Costo_Base (float): Costo base en Bs

=== TABLA DIMENSION: CLIENTES (600 clientes) ===
- ID_Cliente (str): PK (C0001...)
- Cliente (str): Nombre del cliente
- Segmento (str): 5 segmentos (Retail, Corporativo, PYME, Gobierno, ONG)
- Ciudad (str): 13 ciudades
- Tipo_Cliente (str): Empresa o Persona
- Fecha_Alta (datetime): Fecha de registro
- Estado_Cliente (str): Activo / Inactivo

=== TABLA DIMENSION: SUCURSALES (16 sucursales) ===
- ID_Sucursal (str): PK (S001...)
- Sucursal (str): Nombre comercial
- Ciudad_Sucursal (str): 13 ciudades
- Regional (str): 4 regionales (Oriente, Occidente, Centro, Norte)
- Responsable_Sucursal (str): 8 responsables
- Formato_Sucursal (str): Tradicional, Express, Premium

=== TABLA DIMENSION: METAS (288 registros, 18 meses × 4 canales × 4 regionales) ===
- Ano (int): 2023-2024
- Mes (int): 1-12
- Canal (str): 4 canales
- Regional (str): 4 regionales
- Meta_Venta_Neta (float): Meta mensual de venta en Bs
- Meta_Margen (float): Meta mensual de margen en Bs

=== TABLA HOMOLOGACION (480 registros) ===
- Codigo_Producto_Origen -> Codigo_Producto_Homologado (mapeo Pxxx -> 1-120)
- Tipo_Codigo: 4 tipos de prefijo

=============================================
RELACIONES DEL MODELO:
=============================================
fact_ventas.ID_Cliente -> dim_clientes.ID_Cliente
fact_ventas.ID_Sucursal -> dim_sucursales.ID_Sucursal
fact_ventas.Codigo_Producto -> homologacion.Codigo_Producto_Origen -> dim_productos.Codigo_Producto_Homologado
fact_metas.KeyMeta (Ano, Mes, Canal, Regional) -> fact_ventas (Ano, Mes, Canal, Regional)

=============================================
PAGINAS DEL DASHBOARD:
=============================================
1. INICIO (app.py): Logo, 3 KPIS (Venta Neta Total, Margen Bruto, Clientes Activos), tarjetas a vistas.

2. VISTA GERENCIAL (pagina 1): 6 KPIs con variacion MoM y YoY. Tendencia mensual. Matriz 2x2: venta por canal, margen por categoria, cumplimiento de meta por regional, clientes por segmento. Tabla resumen por regional.

3. VISTA ESTRATEGICA (pagina 2): Rentabilidad por categoria. Distribucion region/ciudad. Top/Bottom 10 productos. Dispersion 4 cuadrantes (venta vs margen%) con tendencia OLS. Treemap jerarquico Categoria-Marca-Producto. Analisis ABC Pareto. Tabla productos con margen <5%.

4. VISTA OPERATIVA (pagina 3): Tabla transacciones filtrable. Top 10 ejecutivos. Top 10 clientes. Descuentos >20%. Exportacion CSV/Excel.

=============================================
FILTROS DISPONIBLES (Sidebar):
=============================================
Tiempo: Ano (2023-2024), Mes, MTD/QTD/YTD, rango de fechas exacto
Comerciales: Canal (4), Sucursal (16), Ejecutivo (15)
Producto: Categoria (8) → Marca (10) en cascada
Cliente: Segmento (5)

=============================================
DATOS GENERALES DEL NEGOCIO:
=============================================
- Empresa: Comercial Andina S.A. (Bolivia, consumo masivo masivo)
- Periodo: Enero 2023 a Junio 2024 (18 meses)
- Transacciones confirmadas: ~9,804
- Venta Neta Total: ~Bs 2,722,974
- Margen Bruto Total: ~Bs 598,628 (22%)
- 120 productos, 600 clientes, 16 sucursales, 15 ejecutivos
- 4 canales, 4 regionales, 8 categorias, 10 marcas, 5 segmentos
- Moneda: Bolivianos (Bs). Ticket promedio: ~Bs 278
"""




def generar_resumen_datos(
    df_ventas: pd.DataFrame,
    df_metas: Optional[pd.DataFrame] = None,
    df_productos: Optional[pd.DataFrame] = None,
    df_clientes: Optional[pd.DataFrame] = None,
    df_sucursales: Optional[pd.DataFrame] = None,
) -> str:
    if df_ventas.empty:
        return "No hay datos disponibles para el filtro actual."

    total_vn = get_venta_neta(df_ventas)
    total_mb = get_margen_bruto(df_ventas)
    margen_pct = get_margen_pct(df_ventas)
    ticket_prom = get_ticket_promedio(df_ventas)
    cantidad = get_cantidad_vendida(df_ventas)
    clientes_act = get_clientes_activos(df_ventas)
    transacciones = df_ventas["ID_Transaccion"].nunique() if "ID_Transaccion" in df_ventas.columns else len(df_ventas)

    periodo_min = df_ventas["Periodo"].min() if "Periodo" in df_ventas.columns else "N/A"
    periodo_max = df_ventas["Periodo"].max() if "Periodo" in df_ventas.columns else "N/A"

    resumen = f"""DATOS ACTUALES DEL DASHBOARD (periodo: {periodo_min} a {periodo_max}):

METRICAS GENERALES:
- Venta Neta Total: {format_currency(total_vn)}
- Margen Bruto Total: {format_currency(total_mb)}
- Margen Porcentual: {format_percent(margen_pct)}
- Ticket Promedio: {format_currency(ticket_prom)}
- Cantidad Vendida: {format_number(cantidad)} unidades
- Clientes Activos: {format_number(float(clientes_act))}
- Transacciones: {format_number(float(transacciones))}"""

    if "Canal" in df_ventas.columns:
        top_canales = df_ventas.groupby("Canal")["Venta_Neta"].sum().nlargest(5)
        resumen += "\n\nVENTAS POR CANAL:\n"
        for canal, val in top_canales.items():
            resumen += f"- {canal}: {format_currency(val)}\n"

    if "Ejecutivo_Venta" in df_ventas.columns:
        top_ejec = df_ventas.groupby("Ejecutivo_Venta")["Venta_Neta"].sum().nlargest(5)
        resumen += "\nTOP 5 EJECUTIVOS:\n"
        for ejec, val in top_ejec.items():
            resumen += f"- {ejec}: {format_currency(val)}\n"

    if df_productos is not None and not df_productos.empty and "Codigo_Producto_Homologado" in df_ventas.columns:
        merged = df_ventas.merge(
            df_productos[["Codigo_Producto_Homologado", "Producto", "Categoria", "Marca"]],
            on="Codigo_Producto_Homologado", how="left"
        )
        if "Producto" in merged.columns:
            top_prod = merged.groupby("Producto")["Venta_Neta"].sum().nlargest(5)
            resumen += "\nTOP 5 PRODUCTOS:\n"
            for prod, val in top_prod.items():
                resumen += f"- {prod}: {format_currency(val)}\n"
        if "Categoria" in merged.columns:
            cat_margen = merged.groupby("Categoria")["Margen_Bruto"].sum()
            resumen += "\nMARGEN BRUTO POR CATEGORIA:\n"
            for cat, val in cat_margen.items():
                resumen += f"- {cat}: {format_currency(val)}\n"

    if df_sucursales is not None and not df_sucursales.empty and "ID_Sucursal" in df_ventas.columns:
        merged_suc = df_ventas.merge(
            df_sucursales[["ID_Sucursal", "Regional", "Ciudad_Sucursal"]],
            on="ID_Sucursal", how="left"
        )
        if "Regional" in merged_suc.columns:
            top_reg = merged_suc.groupby("Regional")["Venta_Neta"].sum().nlargest(5)
            resumen += "\nVENTAS POR REGIONAL:\n"
            for reg, val in top_reg.items():
                resumen += f"- {reg}: {format_currency(val)}\n"

    if df_metas is not None and not df_metas.empty:
        cumplimiento = get_cumplimiento_meta(df_ventas, df_metas)
        resumen += f"\nCUMPLIMIENTO DE META GLOBAL: {format_percent(cumplimiento)}"

    if df_clientes is not None and not df_clientes.empty and "Segmento" in df_clientes.columns:
        clientes_ids = df_ventas["ID_Cliente"].unique()
        seg_counts = df_clientes[df_clientes["ID_Cliente"].isin(clientes_ids)]["Segmento"].value_counts()
        resumen += "\n\nCLIENTES POR SEGMENTO:\n"
        for seg, cnt in seg_counts.items():
            resumen += f"- {seg}: {format_number(float(cnt))} clientes\n"

    return resumen


def consultar_groq(pregunta: str, contexto: str) -> str:
    api_key = st.secrets.get("GROQ_API_KEY", "")
    if not api_key:
        return "Error: No se ha configurado la API key de Groq. Agrega GROQ_API_KEY en los secrets."

    try:
        from groq import Groq
        client = Groq(api_key=api_key)
        prompt = f"""Eres un analista de inteligencia de negocios senior para Comercial Andina S.A.

{DASHBOARD_CONTEXT}

DATOS DEL FILTRO ACTUAL:
{contexto}

INSTRUCCIONES ESTRICTAS:
1. Responde SOLO con informacion de los datos y contexto proporcionados arriba.
2. Si te preguntan sobre el dashboard (paginas, KPIs, estructura), explica usando la informacion de arriba.
3. Si te preguntan por datos (ventas, margenes, productos), usa los DATOS DEL FILTRO ACTUAL.
4. NO inventes cifras. Si no tienes suficiente informacion, indicalo.
5. Se conciso, profesional y directo. Usa viñetas para claridad.
6. Menciona valores numericos con formato: Bs X,XXX cuando sea relevante.

Pregunta del usuario: {pregunta}"""
        chat_completion = client.chat.completions.create(
            messages=[{"role": "user", "content": prompt}],
            model="llama-3.3-70b-versatile",
            temperature=0.2,
            max_tokens=800,
        )
        return chat_completion.choices[0].message.content
    except Exception as e:
        logger.error(f"Error al consultar Groq: {e}")
        return f"Error: {str(e)}"


def _obtener_datos_filtrados():
    ventas = st.session_state.get("df_ventas_filtrado")
    if ventas is None:
        ventas = get_cached_dataframe("ventas")
        filtros = st.session_state.get("filtros", {})
        if filtros and ventas is not None:
            ventas = apply_filters(
                ventas, filtros,
                get_cached_dataframe("productos"),
                get_cached_dataframe("clientes"),
                get_cached_dataframe("sucursales"),
            )
    return ventas


def _procesar_pregunta(pregunta: str):
    st.session_state.mensajes_chat.append({"role": "user", "content": pregunta})
    with st.spinner("Analizando datos..."):
        ventas = _obtener_datos_filtrados()
        if ventas is None or ventas.empty:
            respuesta = "No hay datos disponibles para el filtro actual."
        else:
            contexto = generar_resumen_datos(
                ventas,
                get_cached_dataframe("metas"),
                get_cached_dataframe("productos"),
                get_cached_dataframe("clientes"),
                get_cached_dataframe("sucursales"),
            )
            respuesta = consultar_groq(pregunta, contexto)
        st.session_state.mensajes_chat.append({"role": "assistant", "content": respuesta})
    st.rerun()


def render_chat_ia():
    c = COLORS

    if "mensajes_chat" not in st.session_state:
        st.session_state.mensajes_chat = []

    if st.session_state.get("ia_pending"):
        pregunta = st.session_state.pop("ia_pending")
        _procesar_pregunta(pregunta)

    st.markdown(f"""
    <style>
    div[data-testid="stExpander"] details {{
        background: rgba(15, 15, 35, 0.25) !important;
        border: 1px solid {c['border_accent']} !important;
        border-radius: 12px !important;
    }}
    div[data-testid="stChatMessage"] {{
        background: rgba(255,255,255,0.03) !important;
        border: 1px solid rgba(255,255,255,0.06) !important;
        border-radius: 10px !important;
        padding: 6px 10px !important;
        margin: 4px 0 !important;
        font-size: 12.5px !important;
    }}
    div[data-testid="stChatMessage"][data-testid*="user"] {{
        border-color: rgba(99,102,241,0.2) !important;
    }}
    div[data-testid="stChatInput"] textarea {{
        background: rgba(255,255,255,0.04) !important;
        border: 1px solid {c['border']} !important;
        border-radius: 8px !important;
        color: {c['text_primary']} !important;
        font-size: 12px !important;
    }}
    </style>
    """, unsafe_allow_html=True)

    expandido = len(st.session_state.mensajes_chat) > 0
    with st.expander("🤖 IA Comercial", expanded=expandido):
        for msg in st.session_state.mensajes_chat[-6:]:
            with st.chat_message(msg["role"]):
                st.markdown(msg["content"])

        if not st.session_state.mensajes_chat:
            st.caption("Sugerencias: producto mas vendido, canal con mayor margen, mejor ejecutivo, cumplimiento de metas")

        pregunta = st.chat_input("Escribe tu consulta...", key="ia_input")
        if pregunta:
            st.session_state.ia_pending = pregunta
            st.rerun()
