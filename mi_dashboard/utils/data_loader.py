import pandas as pd
import logging
from pathlib import Path
from typing import Optional

from config.settings import EXCEL_PATH

logger = logging.getLogger(__name__)


def load_excel_sheets(path: Optional[Path] = None) -> dict[str, pd.DataFrame]:
    path = path or EXCEL_PATH
    if not path.exists():
        logger.error("Archivo Excel no encontrado: %s", path)
        raise FileNotFoundError(f"Archivo Excel no encontrado: {path}")

    logger.info("Cargando Excel desde: %s", path)
    sheets = {
        "VENTAS": None,
        "PRODUCTOS": None,
        "CLIENTES": None,
        "SUCURSAL": None,
        "METAS": None,
        "HOMOLOGACIÓN": None,
    }

    for sheet_name in sheets:
        try:
            df = pd.read_excel(path, sheet_name=sheet_name)
            sheets[sheet_name] = df
            logger.info("Cargada hoja '%s': %d filas x %d cols", sheet_name, *df.shape)
        except Exception as e:
            logger.error("Error cargando hoja '%s': %s", sheet_name, e)
            sheets[sheet_name] = pd.DataFrame()

    return sheets


def load_sheet(sheet_name: str, path: Optional[Path] = None) -> pd.DataFrame:
    path = path or EXCEL_PATH
    if not path.exists():
        raise FileNotFoundError(f"Archivo Excel no encontrado: {path}")
    return pd.read_excel(path, sheet_name=sheet_name)
