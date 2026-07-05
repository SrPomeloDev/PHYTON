# AGENTS.md — Dashboard Comercial Andina S.A.

## Stack

Python 3.12+, Streamlit, Supabase (PostgreSQL), Pandas, Plotly (`template="plotly_dark"`), statsmodels (trendline="ols"), SQLAlchemy + psycopg2-binary

## Commands

```powershell
.venv\Scripts\activate
streamlit run app.py            # Dashboard
py -m utils.etl                 # ETL: Excel → Supabase (upsert)
```

## Architecture

```
mi_dashboard/
├── app.py                      # Entry point — home page with nav cards
├── pages/                      # 3 views: 1_Gerencial, 2_Estrategica, 3_Operativa
├── services/                   # Business logic (ventas, clientes, productos, metas)
├── components/                 # UI: cards, charts (8 types), sidebar, tables
├── utils/                      # etl, cache, metrics, formatters, data_loader, helpers
├── config/                     # settings (ENV paths), database (engine), style (CSS palette)
├── sql/                        # schema, views, indexes, 15 queries
├── data/                       # Temp (gitignored)
└── assets/
```

**Offline-first**: `get_cached_dataframe(key)` in `utils/cache.py` loads Excel directly via `_run_etl()`. Supabase is optional — `get_engine()` returns `None` without `SUPABASE_DB_URL` in `.env`.

**EXCEL_PATH** = `mi_dashboard/../bbdd_prueba.xlsx` (one dir above mi_dashboard/)

## Critical model rules

| Rule | Detail |
|------|--------|
| **Confirmada** | Only `Estado_Venta = 'Confirmada'`. ETL filters in `clean_ventas()`; metrics validate via `_assert_confirmada()` |
| **Homologation** | `Codigo_Producto` (Ventas) → `Codigo_Producto_Origen` (Homologación) → `Codigo_Producto_Homologado` (Productos). **Excludes** unmapped rows (no fallback) |
| **KeyMeta** | `Año|Mes|Canal|Regional` pipe-concatenated |
| **Año (ñ)** | Excel column `Año` with ñ. ETL renames to `anio` before upsert to avoid SQL encoding errors |
| **Currency** | Bolivianos (Bs). Formatter default `format_currency(value, symbol="Bs")` |

## Data flow (offline)

```
Excel → load_excel_sheets() → clean_*() per sheet → homologar_productos() → _data_cache dict
  → get_cached_dataframe(key) (st.cache_data, ttl=3600)
  → pages consume via get_cached_dataframe()
```

Each page calls `get_cached_dataframe("ventas")`, `get_cached_dataframe("productos")`, etc. to get clean DataFrames with derived fields (Venta_Neta, Margen_Bruto, etc.) already computed.

## Sidebar filters (wired)

`render_sidebar()` in `components/sidebar.py` returns a `dict` of filter selections. Every page calls it and passes the result + DataFrames to `apply_filters(ventas, filtros, productos, clientes)` from `utils/helpers.py`.

- Filters are `st.multiselect` widgets with ✓/✕ toggle buttons
- Categoria → Marca cascading: Marca options narrow based on selected Categoria
- State persists via `st.session_state.filtro_*` keys
- Reset button clears all `filtro_*` keys and calls `st.rerun()`

## Performance gotchas

- **`st.text_input`** on Operativa: each keystroke re-runs the whole script. **DO NOT USE**. Use native DataFrame search or `st.selectbox`.
- **Merge 10k rows**: wrap with `@st.cache_data(ttl=300)` inside the page to avoid re-merge per re-render.
- **Large DataFrames**: `.head(2000)` before `st.dataframe` to avoid serialization overload.
- **Supabase pooler**: `chunk_size=500` in upserts. Direct host (db.xxx.supabase.co) is IPv6-only, use pooler.

## ETL pipeline (`utils/etl.py`)

```
run_etl():
  load_excel_sheets() → clean_*() per sheet → homologar_productos(ventas, homologacion)
  → rename columns to snake_case → upsert_table(df, table_name, pk_columns)
```

- `homologar_productos()` excludes (no fallback) products without homologation, logs each `ID_Transaccion` excluded
- `upsert_table()` uses `ON CONFLICT DO UPDATE` with chunks of 500 rows
- `clean_ventas()` computes all derived fields (Venta_Bruta, Descuento_Valor, Venta_Neta, Costo_Total, Margen_Bruto, Margen_Pct, Rango_Venta, Fecha, Año, Mes, Periodo)

## Key metrics (`utils/metrics.py`)

All 7 functions (`get_venta_neta`, `get_margen_bruto`, `get_margen_pct`, `get_ticket_promedio`, `get_cantidad_vendida`, `get_cumplimiento_meta`, `get_clientes_activos`) call `_assert_confirmada(df)` — raises `ValueError` if any row is not Confirmada.

## Design conventions (`config/style.py`)

- **COLORS dict** — never hardcode colors in pages/components
- **CSS injected** via `inject_css()` called from `apply_theme()` in `app.py`
- **Palette**: dark theme (`#0B0F19` background), indigo primary (`#6366F1`), emerald success (`#10B981`)
- **Charts**: Plotly with `template="plotly_dark"`, hover format $/%, `_clean_legend()` helper, `CHART_COLORS` list (10 colors)
- **Currency formatter**: `utils/formatters.py` — `format_currency` (Bs), `format_percent`, `format_number`, `format_date_short`

## SQL (`sql/`)

- `schema.sql` — 6 tables (fact_ventas, fact_metas, dim_productos, dim_clientes, dim_sucursales, dim_homologacion) with FKs, indexes
- `queries.sql` — 15 business queries using CTEs for complex aggregations (e.g., Query 7 uses CTEs for regional meta cumplimiento)
- `views.sql` — 6 materialized views

## Key files

| File | Purpose |
|------|---------|
| `config/settings.py` | `EXCEL_PATH`, `DB_CONFIG`, `RANGO_VENTA_BINS/LABELS` |
| `config/database.py` | `get_engine()` (returns `None` offline), `execute_query()` |
| `utils/cache.py` | `get_cached_dataframe(key)` — ETL + cache layer |
| `utils/helpers.py` | `apply_filters()`, `safe_divide()`, `semaphore_color()` |
| `utils/formatters.py` | `format_currency()` with Bs default |
| `components/sidebar.py` | `render_sidebar()` — returns filter dict, called by all pages |
| `sql/queries.sql` | 15 business queries |
