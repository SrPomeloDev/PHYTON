import streamlit as st
import pandas as pd
from typing import Optional

from config.style import COLORS, FONT_FAMILY


def styled_section(title: str, icon: str = "", subtitle: str = "") -> None:
    """Render a premium section header with icon and optional subtitle."""
    st.markdown(
        f"""
        <div style="
            display: flex; align-items: center; gap: 0.5rem;
            margin-top: 1.2rem; margin-bottom: 0.3rem;
        ">
            <span style="font-size: 1.1rem;">{icon}</span>
            <span style="
                font-size: 1.05rem; font-weight: 700;
                color: {COLORS['text_primary']};
                letter-spacing: -0.3px;
            ">{title}</span>
        </div>
        {"<div style='color: " + COLORS['text_muted'] + "; font-size: 0.78rem; margin-bottom: 0.6rem;'>" + subtitle + "</div>" if subtitle else ""}
        """,
        unsafe_allow_html=True,
    )


def render_data_table(df: pd.DataFrame, title: str = "", height: int = 400) -> None:
    if df.empty:
        st.info("No hay datos para mostrar")
        return

    if title:
        st.markdown(f"### {title}")

    st.dataframe(
        df,
        use_container_width=True,
        height=height,
        column_config={
            col: st.column_config.Column(col, width="medium")
            for col in df.columns
        },
        hide_index=True,
    )


def render_metric_table(
    df: pd.DataFrame,
    title: str = "",
    value_col: str = "Valor",
    label_col: str = "Indicador",
) -> None:
    if df.empty:
        return
    if title:
        st.markdown(f"### {title}")

    for _, row in df.iterrows():
        col1, col2 = st.columns([3, 1])
        col1.markdown(f"**{row[label_col]}**")
        col2.markdown(f"**{row[value_col]}**")


def export_to_csv(df: pd.DataFrame, filename: str = "datos_exportados.csv") -> None:
    csv = df.to_csv(index=False).encode("utf-8-sig")
    st.download_button(
        label="📥 Exportar CSV",
        data=csv,
        file_name=filename,
        mime="text/csv",
        use_container_width=True,
    )


def export_to_excel(df: pd.DataFrame, filename: str = "datos_exportados.xlsx") -> None:
    output = pd.ExcelWriter(filename, engine="openpyxl")
    df.to_excel(output, index=False, sheet_name="Datos")
    output.close()
    with open(filename, "rb") as f:
        st.download_button(
            label="📥 Exportar Excel",
            data=f,
            file_name=filename,
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            use_container_width=True,
        )
