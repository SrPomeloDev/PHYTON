# Dashboard Comercial — Andina S.A.

Dashboard analítico para **Comercial Andina S.A.** Empresa de venta de productos de consumo masivo por múltiples canales. Construido con Streamlit, Supabase, Pandas y Plotly. Responde 10 preguntas de negocio clave a través de 3 vistas interactivas con más de 15 visualizaciones.

> 📖 Documentación completa: [`docs/informe_tecnico.md`](docs/informe_tecnico.md) — stack, modelo de datos, ETL, arquitectura, métricas, consultas SQL y respuestas validadas.
>
> 📖 Informe ETL detallado: [`docs/informe_etl.md`](docs/informe_etl.md)
>
> 📖 Respuestas validadas: [`respuestas_validacion.txt`](respuestas_validacion.txt)

## Stack

| Tecnología | Versión | Propósito |
|-----------|---------|-----------|
| Python | 3.12+ | Lenguaje principal |
| Streamlit | 1.58+ | Dashboard interactivo |
| Pandas | 2.2+ | Transformación de datos |
| Plotly | 5.20+ | Visualizaciones (tema dark) |
| SQLAlchemy | 2.0+ | Conexión PostgreSQL |
| Supabase | — | Base de datos (opcional) |
| statsmodels | 0.14+ | Tendencia OLS en scatter |

Ver `requirements.txt` para dependencias completas.

## Quick Start

```powershell
.venv\Scripts\activate
streamlit run app.py        # Iniciar dashboard (modo offline automático)
py -m utils.etl             # (Opcional) Cargar datos a Supabase
```

Sin configuración adicional el dashboard funciona offline cargando datos directamente del archivo `bbdd_prueba.xlsx`.

## Arquitectura

```
mi_dashboard/
├── app.py                  # Entry point
├── pages/                  # 3 vistas: Gerencial, Estratégica, Operativa
├── services/               # Lógica de negocio
├── components/             # UI: cards, charts (8 tipos), sidebar, tables
├── utils/                  # ETL, caché, métricas, formateo, helpers
├── config/                 # Configuración + conexión + CSS (660+ líneas)
├── sql/                    # Schema, 15 queries, vistas materializadas
├── docs/                   # Documentación técnica
└── assets/                 # Diagrama del modelo de datos
```

**Modelo**: Esquema estrella — `fact_ventas` como hecho con 4 dimensiones (`dim_productos`, `dim_clientes`, `dim_sucursales`, `fact_metas` via `KeyMeta`).

## Vistas del Dashboard

| Vista | Propósito | KPIs | Visualizaciones clave |
|-------|-----------|------|----------------------|
| **Gerencial** | Estado general | 6 KPIs con MoM/YoY | Tendencia, canal×regional, heatmap, cumplimiento metas |
| **Estratégica** | Rentabilidad | Matriz 4 cuadrantes | Ranking categorías/productos, scatter, treemap, Pareto, baja rentabilidad |
| **Operativa** | Detalle transaccional | 3 tablas con ProgressColumn | Detalle filtrable, top ejecutivos, top clientes, descuentos >20% |

## 9 Medidas Maestras

Venta Bruta, Venta Neta, Costo Total, Margen Bruto, Margen %, Ticket Promedio, Cantidad Vendida, Cumplimiento Meta, Clientes Activos.

Todas en `utils/metrics.py` con validación `_assert_confirmada()`.

## 10 Preguntas Respondidas (con datos reales)

| # | Pregunta | Respuesta |
|---|----------|-----------|
| 1 | Venta Neta total | Bs 2,722,974.24 |
| 2 | Margen Bruto total | Bs 598,627.79 |
| 3 | Margen % general | 21.98% |
| 4 | Canal con mayor Venta Neta | Distribuidor (Bs 1,225,314) |
| 5 | Categoría con mayor Margen Bruto | Mascotas (Bs 132,635) |
| 6 | Regional con mayor cumplimiento | Oriente (98.94%) |
| 7 | Ejecutivo con mayor Venta Neta | Daniel Quiroga (Bs 221,997) |
| 8 | Producto con menor Margen % | Botiquín NaturaMax 117 (5.02%) |
| 9 | Cliente con mayor compra | Cliente Empresa 0515 (Bs 14,849) |
| 10 | Transacciones desc. >20% | 1,213 |

## Funcionalidades Clave

- **Offline-first**: sin Supabase configurado, carga datos del Excel automáticamente
- **Filtros avanzados**: cascada Categoría→Marca, MTD/QTD/YTD, rango de fechas
- **Time comparison**: MoM y YoY en todos los KPIs gerenciales
- **Drill-down**: navegación contextual entre vistas con badge indicador
- **8 tipos de gráficos**: línea, barra, dona, heatmap, scatter, treemap, Pareto, gauge
- **Diseño premium**: glassmorphism, animaciones, paleta oscura (660+ líneas CSS)
- **Exportación CSV** desde Vista Operativa
