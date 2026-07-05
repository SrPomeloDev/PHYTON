"""
ETL Pipeline — Dashboard Comercial Andina S.A.

Flujo:
1. Cargar todas las hojas del Excel
2. Limpiar y transformar cada tabla
3. Homologar productos (Ventas → Homologación → Productos)
4. Derivar campos obligatorios
5. Cargar a Supabase (upsert)

Ejecución: python -m utils.etl
"""
import logging
import sys
from datetime import datetime
from typing import Optional

import pandas as pd
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError

from config.database import get_engine, execute_query
from config.settings import RANGO_VENTA_BINS, RANGO_VENTA_LABELS
from utils.data_loader import load_excel_sheets

logger = logging.getLogger(__name__)


def _normalize_date(val) -> Optional[datetime]:
    if pd.isna(val):
        return None
    if isinstance(val, (datetime, pd.Timestamp)):
        return val if isinstance(val, datetime) else val.to_pydatetime()
    try:
        return datetime(1899, 12, 30) + pd.Timedelta(days=float(val))
    except (TypeError, ValueError):
        return None


def clean_ventas(df: pd.DataFrame) -> pd.DataFrame:
    logger.info("Limpiando VENTAS: %d filas originales", len(df))
    df = df.copy()

    df.columns = df.columns.str.strip()

    df = df[df["Estado_Venta"] == "Confirmada"].copy()
    logger.info("Filtradas Confirmada: %d filas", len(df))

    df["Fecha_Hora_Transaccion"] = df["Fecha_Hora_Transaccion"].apply(_normalize_date)
    df["Fecha"] = df["Fecha_Hora_Transaccion"].dt.date
    df["Año"] = df["Fecha_Hora_Transaccion"].dt.year
    df["Mes"] = df["Fecha_Hora_Transaccion"].dt.month
    df["Periodo"] = df["Año"].astype(str) + "-" + df["Mes"].astype(str).str.zfill(2)

    df[["Cantidad", "Precio_Unitario", "Descuento_Pct", "Costo_Unitario"]] = (
        df[["Cantidad", "Precio_Unitario", "Descuento_Pct", "Costo_Unitario"]]
        .apply(pd.to_numeric, errors="coerce")
        .fillna(0)
    )

    df["Venta_Bruta"] = df["Cantidad"] * df["Precio_Unitario"]
    df["Descuento_Valor"] = df["Venta_Bruta"] * df["Descuento_Pct"]
    df["Venta_Neta"] = df["Venta_Bruta"] - df["Descuento_Valor"]
    df["Costo_Total"] = df["Cantidad"] * df["Costo_Unitario"]
    df["Margen_Bruto"] = df["Venta_Neta"] - df["Costo_Total"]
    df["Margen_Pct"] = df.apply(
        lambda r: r["Margen_Bruto"] / r["Venta_Neta"] if r["Venta_Neta"] > 0 else 0,
        axis=1,
    )
    df["Rango_Venta"] = pd.cut(
        df["Venta_Neta"],
        bins=RANGO_VENTA_BINS,
        labels=RANGO_VENTA_LABELS,
        right=False,
    )

    for col in ["ID_Cliente", "ID_Sucursal", "Codigo_Producto", "Canal", "Ejecutivo_Venta"]:
        df[col] = df[col].astype(str).str.strip()

    logger.info("Ventas limpias: %d filas", len(df))
    return df


def clean_productos(df: pd.DataFrame) -> pd.DataFrame:
    logger.info("Limpiando PRODUCTOS: %d filas", len(df))
    df = df.copy()
    df.columns = df.columns.str.strip()
    for col in ["Codigo_Producto_Homologado", "Producto", "Categoria", "Subcategoria", "Marca"]:
        if col in df.columns:
            df[col] = df[col].astype(str).str.strip()
    for col in ["Precio_Lista", "Costo_Base"]:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0)
    if "Estado_Producto" in df.columns:
        df["Estado_Producto"] = df["Estado_Producto"].fillna("Activo")
    return df


def clean_clientes(df: pd.DataFrame) -> pd.DataFrame:
    logger.info("Limpiando CLIENTES: %d filas", len(df))
    df = df.copy()
    df.columns = df.columns.str.strip()
    for col in ["ID_Cliente", "Cliente", "Segmento", "Ciudad", "Tipo_Cliente"]:
        if col in df.columns:
            df[col] = df[col].astype(str).str.strip()
    if "Fecha_Alta" in df.columns:
        df["Fecha_Alta"] = pd.to_datetime(df["Fecha_Alta"], errors="coerce")
    if "Estado_Cliente" in df.columns:
        df["Estado_Cliente"] = df["Estado_Cliente"].fillna("Activo")
    return df


def clean_sucursales(df: pd.DataFrame) -> pd.DataFrame:
    logger.info("Limpiando SUCURSAL: %d filas", len(df))
    df = df.copy()
    df.columns = df.columns.str.strip()
    for col in ["ID_Sucursal", "Sucursal", "Ciudad_Sucursal", "Regional"]:
        if col in df.columns:
            df[col] = df[col].astype(str).str.strip()
    return df


def clean_metas(df: pd.DataFrame) -> pd.DataFrame:
    logger.info("Limpiando METAS: %d filas", len(df))
    df = df.copy()
    df.columns = df.columns.str.strip()
    if "Regional" in df.columns:
        df["Regional"] = df["Regional"].astype(str).str.strip()
    if "Canal" in df.columns:
        df["Canal"] = df["Canal"].astype(str).str.strip()
    if "Año" in df.columns:
        df["Año"] = pd.to_numeric(df["Año"], errors="coerce").fillna(0).astype(int)
    if "Mes" in df.columns:
        df["Mes"] = pd.to_numeric(df["Mes"], errors="coerce").fillna(0).astype(int)
    for col in ["Meta_Venta_Neta", "Meta_Margen"]:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0)
    df["KeyMeta"] = (
        df["Año"].astype(str)
        + "|"
        + df["Mes"].astype(str)
        + "|"
        + df["Canal"].astype(str)
        + "|"
        + df["Regional"].astype(str)
    )
    return df


def clean_homologacion(df: pd.DataFrame) -> pd.DataFrame:
    logger.info("Limpiando HOMOLOGACIÓN: %d filas", len(df))
    df = df.copy()
    df.columns = df.columns.str.strip()
    for col in ["Codigo_Producto_Origen", "Codigo_Producto_Homologado", "Tipo_Codigo"]:
        if col in df.columns:
            df[col] = df[col].astype(str).str.strip()
    return df


def homologar_productos(ventas: pd.DataFrame, homologacion: pd.DataFrame) -> pd.DataFrame:
    logger.info("Homologando productos en ventas...")
    hom_map = homologacion.set_index("Codigo_Producto_Origen")[
        "Codigo_Producto_Homologado"
    ].to_dict()
    ventas["Codigo_Producto_Homologado"] = ventas["Codigo_Producto"].map(hom_map)
    sin_homologar = ventas["Codigo_Producto_Homologado"].isna()
    total_sin = sin_homologar.sum()
    if total_sin > 0:
        excluidas = ventas.loc[sin_homologar, ["ID_Transaccion", "Codigo_Producto"]]
        for _, row in excluidas.iterrows():
            logger.warning(
                "Producto sin homologación — excluido: ID_Transaccion=%s, Codigo_Producto=%s",
                row["ID_Transaccion"],
                row["Codigo_Producto"],
            )
        ventas = ventas[~sin_homologar].copy()
        logger.info(
            "%d transacciones excluidas por producto sin homologación.",
            total_sin,
        )
    return ventas


def upsert_table(df: pd.DataFrame, table_name: str, pk_columns: list[str]) -> int:
    engine = get_engine()
    if engine is None:
        logger.warning("Sin conexión a base de datos. No se puede insertar %s.", table_name)
        return 0

    if df.empty:
        logger.warning("DataFrame vacío para %s. Saltando.", table_name)
        return 0

    inserted = 0
    try:
        with engine.begin() as conn:
            rows = df.to_dict("records")
            if not rows:
                return 0

            pk_list = ", ".join(pk_columns)
            all_cols = list(rows[0].keys())
            cols = ", ".join(all_cols)

            # Batch in chunks of 500 for pooler performance
            chunk_size = 500
            for i in range(0, len(rows), chunk_size):
                chunk = rows[i : i + chunk_size]

                placeholders = ", ".join(
                    [
                        "(" + ", ".join([f":{k}_{j}" for k in all_cols]) + ")"
                        for j in range(len(chunk))
                    ]
                )

                params = {}
                for j, row in enumerate(chunk):
                    for k, v in row.items():
                        params[f"{k}_{j}"] = v if pd.notna(v) else None

                update_cols = ", ".join(
                    [f"{k} = EXCLUDED.{k}" for k in all_cols if k not in pk_columns]
                )

                sql = f"""
                    INSERT INTO {table_name} ({cols})
                    VALUES {placeholders}
                    ON CONFLICT ({pk_list})
                    DO UPDATE SET {update_cols}
                """
                conn.execute(text(sql), params)
                inserted += len(chunk)

            logger.info("Upsert %s: %d filas procesadas", table_name, inserted)
    except SQLAlchemyError as e:
        logger.error("Error en upsert %s: %s", table_name, e)
        raise
    return inserted


def run_etl() -> dict[str, int]:
    logger.info("=== INICIO ETL ===")

    sheets = load_excel_sheets()

    resultados = {}

    # 1. Limpiar dimensiones
    productos = clean_productos(sheets["PRODUCTOS"])
    productos = productos.rename(columns={
        "Codigo_Producto_Homologado": "codigo_producto_homologado",
        "Producto": "producto",
        "Categoria": "categoria",
        "Subcategoria": "subcategoria",
        "Marca": "marca",
        "Estado_Producto": "estado_producto",
        "Precio_Lista": "precio_lista",
        "Costo_Base": "costo_base",
    })
    resultados["productos"] = upsert_table(
        productos, "dim_productos", ["codigo_producto_homologado"]
    )

    clientes = clean_clientes(sheets["CLIENTES"])
    clientes = clientes.rename(columns={
        "ID_Cliente": "id_cliente",
        "Cliente": "cliente",
        "Segmento": "segmento",
        "Ciudad": "ciudad",
        "Tipo_Cliente": "tipo_cliente",
        "Fecha_Alta": "fecha_alta",
        "Estado_Cliente": "estado_cliente",
    })
    resultados["clientes"] = upsert_table(clientes, "dim_clientes", ["id_cliente"])

    sucursales = clean_sucursales(sheets["SUCURSAL"])
    sucursales = sucursales.rename(columns={
        "ID_Sucursal": "id_sucursal",
        "Sucursal": "sucursal",
        "Ciudad_Sucursal": "ciudad_sucursal",
        "Regional": "regional",
        "Responsable_Sucursal": "responsable_sucursal",
        "Formato_Sucursal": "formato_sucursal",
    })
    resultados["sucursales"] = upsert_table(
        sucursales, "dim_sucursales", ["id_sucursal"]
    )

    homologacion_raw = clean_homologacion(sheets["HOMOLOGACIÓN"])
    # Rename for upsert (keep original for homologar_productos below)
    homologacion_db = homologacion_raw.rename(columns={
        "Codigo_Producto_Origen": "codigo_producto_origen",
        "Codigo_Producto_Homologado": "codigo_producto_homologado",
        "Tipo_Codigo": "tipo_codigo",
    })
    resultados["homologacion"] = upsert_table(
        homologacion_db, "dim_homologacion", ["codigo_producto_origen", "codigo_producto_homologado"]
    )

    metas = clean_metas(sheets["METAS"])
    metas = metas.rename(columns={
        "A\u00f1o": "anio",
        "Mes": "mes",
        "Canal": "canal",
        "Regional": "regional",
        "Meta_Venta_Neta": "meta_venta_neta",
        "Meta_Margen": "meta_margen",
        "KeyMeta": "key_meta",
    })
    resultados["metas"] = upsert_table(metas, "fact_metas", ["key_meta"])

    # 2. Limpiar y homologar ventas
    ventas = clean_ventas(sheets["VENTAS"])
    ventas = homologar_productos(ventas, homologacion_raw)

    ventas_cols = [
        "id_transaccion", "fecha_hora_transaccion", "fecha", "anio", "mes", "periodo",
        "codigo_producto_origen", "codigo_producto_homologado", "id_cliente", "id_sucursal",
        "canal", "cantidad", "precio_unitario", "descuento_pct", "costo_unitario",
        "ejecutivo_venta", "estado_venta",
        "venta_bruta", "descuento_valor", "venta_neta", "costo_total", "margen_bruto", "margen_pct",
    ]
    ventas_clean = ventas.rename(columns={
        "ID_Transaccion": "id_transaccion",
        "Fecha_Hora_Transaccion": "fecha_hora_transaccion",
        "Fecha": "fecha",
        "Año": "anio",
        "Mes": "mes",
        "Periodo": "periodo",
        "Codigo_Producto": "codigo_producto_origen",
        "Codigo_Producto_Homologado": "codigo_producto_homologado",
        "ID_Cliente": "id_cliente",
        "ID_Sucursal": "id_sucursal",
        "Canal": "canal",
        "Cantidad": "cantidad",
        "Precio_Unitario": "precio_unitario",
        "Descuento_Pct": "descuento_pct",
        "Costo_Unitario": "costo_unitario",
        "Ejecutivo_Venta": "ejecutivo_venta",
        "Estado_Venta": "estado_venta",
        "Venta_Bruta": "venta_bruta",
        "Descuento_Valor": "descuento_valor",
        "Venta_Neta": "venta_neta",
        "Costo_Total": "costo_total",
        "Margen_Bruto": "margen_bruto",
        "Margen_Pct": "margen_pct",
    })[ventas_cols].copy()

    resultados["ventas"] = upsert_table(
        ventas_clean, "fact_ventas", ["id_transaccion"]
    )

    logger.info("=== FIN ETL ===")
    logger.info("Resultados: %s", resultados)
    return resultados


if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    )
    try:
        res = run_etl()
        print("ETL completado exitosamente.")
        for k, v in res.items():
            print(f"  {k}: {v} filas")
    except Exception as e:
        logger.error("ETL falló: %s", e)
        sys.exit(1)
