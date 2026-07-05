import logging
from typing import Optional
from sqlalchemy import create_engine, text
from sqlalchemy.engine import Engine
from sqlalchemy.exc import SQLAlchemyError
import streamlit as st

from config.settings import SUPABASE_DB_URL

logger = logging.getLogger(__name__)


@st.cache_resource
def get_engine() -> Optional[Engine]:
    if not SUPABASE_DB_URL:
        logger.warning("SUPABASE_DB_URL no configurada. Usando modo offline.")
        return None
    try:
        engine = create_engine(
            SUPABASE_DB_URL,
            pool_size=5,
            max_overflow=10,
            pool_pre_ping=True,
            connect_args={"connect_timeout": 10},
        )
        return engine
    except Exception as e:
        logger.error("Error al crear engine de base de datos: %s", e)
        return None


def execute_query(query: str, params: Optional[dict] = None) -> list[dict]:
    engine = get_engine()
    if engine is None:
        logger.warning("Base de datos no disponible. Query omitida.")
        return []
    try:
        with engine.connect() as conn:
            result = conn.execute(text(query), params or {})
            rows = result.fetchall()
            return [dict(row._mapping) for row in rows]
    except SQLAlchemyError as e:
        logger.error("Error ejecutando query: %s | Query: %s", e, query[:100])
        return []


def test_connection() -> bool:
    engine = get_engine()
    if engine is None:
        return False
    try:
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        return True
    except SQLAlchemyError:
        return False
