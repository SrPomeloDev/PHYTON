from typing import Optional

import pandas as pd


def _assert_confirmada(df: pd.DataFrame) -> None:
    if "Estado_Venta" in df.columns and (df["Estado_Venta"] != "Confirmada").any():
        raise ValueError(
            "El DataFrame contiene ventas no confirmadas; "
            "filtra por Estado_Venta == 'Confirmada' antes de calcular métricas."
        )


def get_venta_bruta(df: Optional[pd.DataFrame] = None) -> float:
    if df is not None:
        _assert_confirmada(df)
        return float(df["Venta_Bruta"].sum())
    return 0.0


def get_venta_neta(df: Optional[pd.DataFrame] = None) -> float:
    if df is not None:
        _assert_confirmada(df)
        return float(df["Venta_Neta"].sum())
    return 0.0


def get_costo_total(df: Optional[pd.DataFrame] = None) -> float:
    if df is not None:
        _assert_confirmada(df)
        return float(df["Costo_Total"].sum())
    return 0.0


def get_margen_bruto(df: Optional[pd.DataFrame] = None) -> float:
    if df is not None:
        _assert_confirmada(df)
        return float(df["Margen_Bruto"].sum())
    return 0.0


def get_margen_pct(df: Optional[pd.DataFrame] = None) -> float:
    if df is not None:
        _assert_confirmada(df)
        venta_neta = df["Venta_Neta"].sum()
        if venta_neta > 0:
            return float(df["Margen_Bruto"].sum() / venta_neta)
    return 0.0


def get_ticket_promedio(df: Optional[pd.DataFrame] = None) -> float:
    if df is not None:
        _assert_confirmada(df)
        transacciones = df["ID_Transaccion"].nunique()
        if transacciones > 0:
            return float(df["Venta_Neta"].sum() / transacciones)
    return 0.0


def get_cantidad_vendida(df: Optional[pd.DataFrame] = None) -> float:
    if df is not None:
        _assert_confirmada(df)
        return float(df["Cantidad"].sum())
    return 0.0


def get_clientes_activos(df: Optional[pd.DataFrame] = None) -> int:
    if df is not None:
        _assert_confirmada(df)
        return int(df["ID_Cliente"].nunique())
    return 0


def get_cumplimiento_meta(
    df_ventas: Optional[pd.DataFrame] = None,
    df_metas: Optional[pd.DataFrame] = None,
) -> float:
    if df_ventas is not None and df_metas is not None:
        _assert_confirmada(df_ventas)
        venta_neta = df_ventas["Venta_Neta"].sum()
        meta_venta = df_metas["Meta_Venta_Neta"].sum()
        if meta_venta > 0:
            return float(venta_neta / meta_venta)
    return 0.0


def get_rango_venta_distribution(df: pd.DataFrame) -> pd.Series:
    if "Rango_Venta" in df.columns:
        return df["Rango_Venta"].value_counts().sort_index()
    return pd.Series(dtype=int)
