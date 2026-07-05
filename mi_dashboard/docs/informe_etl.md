# Informe ETL — Dashboard Comercial Andina S.A.

## Pipeline

```
bbdd_prueba.xlsx (6 hojas)
  → load_excel_sheets()
  → clean_*() por hoja
  → homologar_productos()
  → rename a snake_case
  → upsert_table() a Supabase
  → _data_cache para Streamlit
```

## Hojas del Excel

| Hoja | Tabla destino | Registros | Propósito |
|------|---------------|-----------|-----------|
| VENTAS | fact_ventas | 10,000 → 9,804 (filtro Confirmada) | Transacciones de venta |
| PRODUCTOS | dim_productos | 120 | Catálogo de productos homologados |
| CLIENTES | dim_clientes | 600 | Datos de clientes |
| SUCURSAL | dim_sucursales | ~30 | Sucursales y regionales |
| METAS | fact_metas | ~120 | Metas de venta por KeyMeta |
| HOMOLOGACION | dim_homologacion | ~120 | Mapeo código origen → homologado |

## clean_ventas()

1. Filtra `Estado_Venta == 'Confirmada'`
2. Convierte columnas numéricas con `pd.to_numeric(, errors='coerce')`
3. Calcula:
   - `Venta_Bruta = Cantidad * Precio_Unitario`
   - `Descuento_Valor = Venta_Bruta * Descuento_Pct`
   - `Venta_Neta = Venta_Bruta - Descuento_Valor`
   - `Costo_Total = Cantidad * Costo_Unitario`
   - `Margen_Bruto = Venta_Neta - Costo_Total`
   - `Margen_Pct = Margen_Bruto / Venta_Neta`
   - `Fecha = pd.to_datetime()`
   - `Año = Fecha.dt.year`
   - `Mes = Fecha.dt.month`
   - `Periodo = Fecha.dt.strftime('%Y-%m')`
4. Clasifica `Rango_Venta` según bandas configurables

## homologar_productos()

1. Merge `Ventas → Homologacion` on `Codigo_Producto = Codigo_Producto_Origen`
2. Loggea cada `ID_Transaccion` que queda sin homologación
3. Excluye filas sin `Codigo_Producto_Homologado` (no hay fallback)

## upsert_table()

- `ON CONFLICT (pk_columns) DO UPDATE SET ...`
- Chunks de 500 filas para evitar timeout del pooler de Supabase
- Convierte `NaN` → `None` para compatibilidad PostgreSQL
- Renombra columnas a snake_case antes del upsert

## Cache offline

`_run_etl()` en `utils/cache.py`:
- Ejecuta todo el pipeline en memoria
- Almacena resultado en `_data_cache` (dict global)
- `get_cached_dataframe(key)` lo envuelve con `@st.cache_data(ttl=3600)`

## Columnas en fact_ventas (snake_case)

| Columna | Tipo | Origen |
|---------|------|--------|
| id_transaccion | integer | Excel |
| id_cliente | integer | Excel |
| id_sucursal | integer | Excel |
| codigo_producto_homologado | integer | Homologación |
| fecha | date | Parseada |
| canal | text | Excel |
| ejecutivo_venta | text | Excel |
| cantidad | numeric | Excel |
| precio_unitario | numeric | Excel |
| descuento_pct | numeric | Excel → calculado |
| descuento_valor | numeric | Calculado |
| venta_bruta | numeric | Calculado |
| venta_neta | numeric | Calculado |
| costo_unitario | numeric | Excel |
| costo_total | numeric | Calculado |
| margen_bruto | numeric | Calculado |
| margen_pct | numeric | Calculado |
| anio | integer | Fecha |
| mes | integer | Fecha |
| periodo | text | Fecha |
| rango_venta | text | Clasificado |
