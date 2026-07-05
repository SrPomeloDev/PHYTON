# Informe Técnico — Dashboard Comercial Andina S.A.

## 1. Stack Tecnológico

| Capa | Tecnología | Versión | Propósito |
|------|-----------|---------|-----------|
| Lenguaje | Python | 3.12.9 | Procesamiento de datos y lógica de negocio |
| Dashboard | Streamlit | 1.58.0 | Frontend interactivo (SPA) |
| Base de datos | Supabase (PostgreSQL 15) | — | Persistencia opcional (pooler: db.xxx.supabase.co) |
| ORM | SQLAlchemy | 2.0.x | Conexión a BD (engine opcional) |
| Manipulación | Pandas | 2.2.x | Transformación, agregación y limpieza de datos |
| Visualización | Plotly | 5.20.x | 8 tipos de gráficos con template plotly_dark |
| Tendencia | statsmodels | 0.14.x | Línea OLS en scatter plots |
| Driver BD | psycopg2-binary | 2.9.x | Conexión PostgreSQL |

## 2. Arquitectura del Proyecto

```
mi_dashboard/
├── app.py                       # Entry point — navegación con tarjetas
├── pages/
│   ├── 1_Gerencial.py           # KPIs, tendencias, cumplimiento, multidim
│   ├── 2_Estrategica.py         # Rentabilidad, matriz 4 cuadrantes, Pareto
│   └── 3_Operativa.py           # Detalle transaccional, top ejec/clientes, descuentos
├── services/                    # Lógica de negocio (reservado)
├── components/
│   ├── cards.py                 # KPI Card con glassmorphism
│   ├── charts.py                # 8 tipos de gráficos Plotly
│   ├── layout.py                # Headers, panels, progress bars, empty states
│   ├── sidebar.py               # Filtros multiselect con cascada
│   └── tables.py                # Tablas con exportación CSV/Excel
├── utils/
│   ├── etl.py                   # Pipeline: Excel → limpieza → homologación → upsert
│   ├── cache.py                 # get_cached_dataframe() con st.cache_data
│   ├── metrics.py               # 9 medidas maestras con validación Confirmada
│   ├── helpers.py               # apply_filters(), get_mom_yoy_change()
│   ├── formatters.py            # format_currency(Bs), format_percent, format_number
│   └── data_loader.py           # load_excel_sheets()
├── config/
│   ├── settings.py              # EXCEL_PATH, RANGO_VENTA_BINS/LABELS
│   ├── database.py              # get_engine(), execute_query()
│   └── style.py                 # COLORS (37 keys), CSS 660+ líneas, CHART_COLORS
├── sql/
│   ├── schema.sql               # 6 tablas (fact_ventas, dim_*, fact_metas, dim_homologacion)
│   ├── queries.sql              # 15 consultas de negocio con CTEs
│   └── views.sql                # 6 vistas materializadas
├── docs/
│   ├── informe_tecnico.md       # Este documento
│   └── informe_etl.md           # Documentación del pipeline ETL
├── data/                        # Temporal (gitignored)
└── assets/                      # Diagramas (opcional)
```

## 3. Modelo de Datos (Estrella)

### Tabla de Hechos

**fact_ventas** (9,804 registros Confirmada de 10,000)
- `ID_Transaccion` (PK)
- `ID_Cliente` (FK → dim_clientes)
- `ID_Sucursal` (FK → dim_sucursales)
- `Codigo_Producto_Homologado` (FK → dim_productos)
- `Fecha`, `Canal`, `Ejecutivo_Venta`
- `Cantidad`, `Precio_Unitario`
- `Descuento_Pct`, `Descuento_Valor`
- `Venta_Bruta`, `Venta_Neta`, `Costo_Total`
- `Margen_Bruto`, `Margen_Pct`
- `Año`, `Mes`, `Periodo`, `Rango_Venta`

### Tablas de Dimensiones

**dim_productos** (120 productos)
- `Codigo_Producto_Homologado` (PK)
- `Producto`, `Categoria`, `Subcategoria`, `Marca`

**dim_clientes** (600 clientes)
- `ID_Cliente` (PK)
- `Cliente`, `Segmento`, `Ciudad`, `Tipo_Cliente`
- `Fecha_Alta`, `Estado_Cliente`

**dim_sucursales** (~30 sucursales)
- `ID_Sucursal` (PK)
- `Sucursal`, `Ciudad_Sucursal`, `Regional`

**fact_metas** (~120 registros)
- `KeyMeta` (PK = `Año|Mes|Canal|Regional`)
- `Meta_Venta_Neta`

**dim_homologacion** (~120 registros)
- `Codigo_Producto_Origen` → `Codigo_Producto_Homologado`

### Reglas Críticas del Modelo

1. **Confirmada**: Solo `Estado_Venta = 'Confirmada'`. El ETL filtra en `clean_ventas()`. Todas las métricas validan con `_assert_confirmada()`.

2. **Homologación**: `Codigo_Producto` (Ventas) → `Codigo_Producto_Origen` (Homologación) → `Codigo_Producto_Homologado` (Productos). Filas sin homologación son **excluidas** (no hay fallback).

3. **KeyMeta**: Pipe-concatenado `Año|Mes|Canal|Regional` para cruce con metas.

4. **Año (ñ)**: La columna Excel `Año` se renombra a `anio` antes del upsert para evitar errores de encoding SQL.

5. **Moneda**: Bolivianos (Bs). Formateador por defecto `format_currency(value, symbol="Bs")`.

## 4. Pipeline ETL

### Flujo

```
Excel (bbdd_prueba.xlsx)
  → load_excel_sheets() — carga 6 hojas
  → clean_ventas() — filtra Confirmada, calcula Venta_Bruta, Descuento_Valor, Venta_Neta,
     Costo_Total, Margen_Bruto, Margen_Pct, Rango_Venta, Fecha, Año, Mes, Periodo
  → clean_productos() — estandariza tipos, homologación
  → clean_clientes() — estandariza tipos
  → clean_sucursales() — estandariza tipos
  → clean_metas() — valida KeyMeta
  → homologar_productos() — cruza Ventas → Homologación → Productos, excluye no mapeados
  → rename a snake_case
  → upsert_table() — ON CONFLICT DO UPDATE, chunks de 500 filas
  → devuelve dict con 6 DataFrames limpios
```

### Caché offline

`get_cached_dataframe(key)` en `utils/cache.py`:
1. Llama a `_run_etl()` que lee Excel directamente
2. Almacena en `_data_cache` (diccionario global)
3. Envuelto en `st.cache_data(ttl=3600)` para persistencia entre reruns

Sin Supabase, el dashboard funciona **offline-first**.

### Limpieza de Ventas

Campos derivados en `clean_ventas()`:
- `Venta_Bruta` = `Cantidad * Precio_Unitario`
- `Descuento_Valor` = `Venta_Bruta * Descuento_Pct`
- `Venta_Neta` = `Venta_Bruta - Descuento_Valor`
- `Costo_Total` = `Cantidad * Costo_Unitario`
- `Margen_Bruto` = `Venta_Neta - Costo_Total`
- `Margen_Pct` = `Margen_Bruto / Venta_Neta`
- `Rango_Venta` = bandas personalizadas (`RANGO_VENTA_BINS/LABELS`)
- `Fecha` = `pd.to_datetime()`
- `Año` / `Mes` / `Periodo`

## 5. Dashboard — 3 Vistas

### 5.1 Vista Gerencial (`1_Gerencial.py`)

**Propósito**: Estado general del negocio con indicadores clave.

| Elemento | Descripción |
|----------|-------------|
| 6 KPIs | Venta Neta, Margen Bruto, Margen %, Ticket Promedio, Cant. Vendida, Clientes Activos |
| MoM/YoY | Cada KPI muestra variación vs mes anterior y vs año anterior |
| Tendencia mensual | Línea: Venta Neta + Margen Bruto por Periodo |
| Matriz 4 req. | VENTA (canal), MARGEN (categoría), META (regional), CLIENTE (segmento) |
| Tabla x Regional | Venta Neta, Margen Bruto, Transacciones por Regional |

### 5.2 Vista Estratégica (`2_Estrategica.py`)

**Propósito**: Rentabilidad y análisis de portafolio.

| Elemento | Descripción |
|----------|-------------|
| Rentabilidad x Categoría | Barras horizontales + chips con margen % |
| Distribución x Región | Barras por Regional y Top 10 Ciudades |
| Ranking productos | Top 10 / Bottom 10 por Venta Neta |
| Matriz 4 cuadrantes | Scatter: Margen % vs Venta Neta (Top 30). Cuadrantes: Estrella ⭐, Potencial 🔍, Volumen ⚠️, Revisar ❌ |
| Treemap jerárquico | Categoría → Subcategoría → Producto |
| Pareto ABC | Concentración de venta por producto |
| Baja rentabilidad | Productos con margen ponderado < 5%. Tabla + gráfico. Incluye impacto y contexto. |

### 5.3 Vista Operativa (`3_Operativa.py`)

**Propósito**: Detalle transaccional y análisis de desempeño.

| Elemento | Descripción |
|----------|-------------|
| Detalle transacciones | 11 columnas con filtros Canal/Ejecutivo. ProgressColumn para Margen %. 3 metric cards. |
| Top 10 Ejecutivos | Ranking por Venta Neta con transacciones y clientes únicos |
| Top 10 Clientes | Ranking por compra con Margen %, Ticket Promedio. Barra de concentración. |
| Descuentos >20% | 1,213 transacciones identificadas. 3 metric cards + tabla con ProgressColumn. |
| Exportación CSV | Botón al final de la página |

## 6. Medidas Maestras (`utils/metrics.py`)

Todas reciben `df` (DataFrame filtrado de ventas) y validan `_assert_confirmada()`.

| # | Medida | Fórmula |
|---|--------|---------|
| 1 | Venta Bruta | `sum(Venta_Bruta)` |
| 2 | Venta Neta | `sum(Venta_Neta)` |
| 3 | Costo Total | `sum(Costo_Total)` |
| 4 | Margen Bruto | `sum(Margen_Bruto)` |
| 5 | Margen % | `sum(Margen_Bruto) / sum(Venta_Neta)` |
| 6 | Ticket Promedio | `sum(Venta_Neta) / ID_Transaccion.nunique()` |
| 7 | Cantidad Vendida | `sum(Cantidad)` |
| 8 | Cumplimiento Meta | Agregación por KeyMeta vs Meta_Venta_Neta |
| 9 | Clientes Activos | `ID_Cliente.nunique()` |

## 7. Consultas SQL (`sql/queries.sql`)

15 consultas de negocio usando CTEs para agregaciones complejas:

| # | Propósito |
|---|-----------|
| Q1 | Venta Neta total (Confirmada) |
| Q2 | Margen Bruto total |
| Q3 | Margen % general |
| Q4 | Canal con mayor Venta Neta |
| Q5 | Categoría con mayor Margen Bruto |
| Q6 | Regional con mayor cumplimiento de meta |
| Q7 | Cumplimiento de meta por regional (CTE) |
| Q8 | Ejecutivo con mayor Venta Neta |
| Q9 | Top 5 ejecutivos |
| Q10 | Producto con menor Margen % |
| Q11 | Top 5 productos más rentables |
| Q12 | Cliente con mayor compra individual |
| Q13 | Top 5 clientes por Venta Neta |
| Q14 | Transacciones con descuento > 20% |
| Q15 | Resumen mensual (Venta Neta, Margen Bruto, Margen %) |

## 8. Filtros Interactivos

`render_sidebar()` en `components/sidebar.py` devuelve `dict` de selecciones.

- **Multiselect**: Categoría, Marca, Canal, Regional, Segmento, Ejecutivo
- **Cascada**: Marca se actualiza según Categoría seleccionada
- **Período**: MTD, QTD, YTD, Rango personalizado
- **Reset**: Botón que limpia `session_state.filtro_*` y recarga
- **Persistencia**: Widget key = `filtro_*`, estado guardado en `session_state`
- **Drill-down**: Navegación contextual entre vistas con badge indicador

## 9. Sistema de Diseño (`config/style.py`)

### Paleta COLORS (37 claves)

- **Fondo**: `#0B0F19` (bg_page), `#111827` (bg_card), `#1F2937` (bg_elevated)
- **Texto**: `#F8FAFC` (text_primary), `#94A3B8` (text_secondary), `#64748B` (text_muted)
- **Acento**: `#6366F1` (primary/accent), `#10B981` (success), `#F59E0B` (warning), `#EF4444` (danger)
- **Secundarios**: `#8B5CF6` (purple), `#06B6D4` (info/cyan), `#F97316` (orange)
- **Variantes**: * _light para tintes de fondo (blue_light, green_light, red_light, orange_light, purple_light, cyan_light)
- **Bordes**: `border`, `border_light`

### CSS (660+ líneas)

Inyectado via `inject_css()` → `apply_theme()` al inicio de cada página.

- **KPI Premium**: Glassmorphism, hover lift, glow effect, trend badges
- **Progress bars**: Animación slide-left, gradientes
- **Drill badge**: Badge flotante con botón de limpiar
- **Stat chip**: Badge informativo compacto
- **Animaciones**: fadeInUp, slideInLeft, pulse
- **Scrollbar personalizada**: Tema oscuro
- **Selectbox/ Multiselect**: Personalizados vía clase `.stSelectbox`/`.stMultiSelect`

### Chart Colors (CHART_COLORS)

10 colores para gráficos Plotly: indigo, emerald, amber, rose, cyan, violet, orange, pink, lime, teal.

## 10. Verificación de Datos

### Totales Globales (9,804 filas Confirmada)

| Medida | Valor |
|--------|-------|
| Venta Neta total | Bs 2,722,974.24 |
| Margen Bruto total | Bs 598,627.79 |
| Margen % general | 21.98% |
| Venta Bruta total | Bs 3,192,582.67 |
| Costo Total | Bs 2,124,346.45 |
| Ticket Promedio | Bs 277.83 |
| Cantidad Vendida | 51,453 unidades |
| Clientes Activos | 600 |
| Períodos | 18 meses (Ene 2023 — Jun 2024) |
| Productos únicos | 120 |

### Respuestas a 10 Preguntas de Negocio

| # | Pregunta | Respuesta |
|---|----------|-----------|
| 1 | Venta Neta total | Bs 2,722,974.24 |
| 2 | Margen Bruto total | Bs 598,627.79 |
| 3 | Margen % general | 21.98% |
| 4 | Canal con mayor Venta Neta | Distribuidor (Bs 1,225,313.76) |
| 5 | Categoría con mayor Margen Bruto | Mascotas (Bs 132,635.08) |
| 6 | Regional con mayor cumplimiento de meta | Oriente (98.94%) |
| 7 | Ejecutivo con mayor Venta Neta | Daniel Quiroga (Bs 221,997.04) |
| 8 | Producto con menor Margen % | Botiquín NaturaMax 117 (5.02%) |
| 9 | Cliente con mayor compra individual | Cliente Empresa 0515 (Bs 14,849.49) |
| 10 | Transacciones con desc. > 20% | 1,213 transacciones |

## 11. Despliegue

### Local

```powershell
.venv\Scripts\activate
streamlit run app.py
```

Sin `.env` con `SUPABASE_DB_URL`, funciona offline cargando `bbdd_prueba.xlsx`.

### Supabase

```powershell
py -m utils.etl
```

Requiere `.env` con `SUPABASE_DB_URL` apuntando al pooler de Supabase (puerto 6543, no el 5432 directo). Chunks de 500 filas para evitar timeout del pooler.
