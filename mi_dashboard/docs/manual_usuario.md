# Manual de Usuario — Dashboard Comercial Andina S.A.

---

## Índice

1. [Introducción](#1-introducción)
2. [Requisitos del Sistema](#2-requisitos-del-sistema)
3. [Instalación y Ejecución](#3-instalación-y-ejecución)
4. [Estructura del Dashboard](#4-estructura-del-dashboard)
5. [Barra Lateral de Navegación y Filtros](#5-barra-lateral-de-navegación-y-filtros)
6. [Vista Gerencial (Página 1)](#6-vista-gerencial-página-1)
7. [Vista Estratégica (Página 2)](#7-vista-estratégica-página-2)
8. [Vista Operativa (Página 3)](#8-vista-operativa-página-3)
9. [Indicadores Clave (KPIs)](#9-indicadores-clave-kpis)
10. [Interpretación de Tarjetas KPI](#10-interpretación-de-tarjetas-kpi)
11. [Filtros y Segmentación](#11-filtros-y-segmentación)
12. [Exportación de Datos](#12-exportación-de-datos)
13. [Preguntas de Negocio](#13-preguntas-de-negocio)
14. [Solución de Problemas](#14-solución-de-problemas)

---

## 1. Introducción

**Dashboard Comercial Andina S.A.** es una aplicación web interactiva desarrollada en Python con **Streamlit** que permite visualizar, analizar y monitorear los indicadores comerciales clave de la empresa Comercial Andina S.A., una compañía boliviana de consumo masivo con operaciones en múltiples canales de venta.

### Canales de Venta

| Canal | Descripción |
|-------|-------------|
| **Distribuidor** | Ventas a través de distribuidores autorizados |
| **Corporativo** | Ventas a empresas e instituciones |
| **Tienda Física** | Ventas en locales comerciales propios |
| **E-commerce** | Ventas por canales digitales |

### Funcionalidades Principales

- Visualización de KPIs comerciales con variaciones mensuales e interanuales
- Análisis de rentabilidad por categoría, región y producto
- Seguimiento de cumplimiento de metas por regional
- Ranking de productos y clientes
- Detalle transaccional con filtros avanzados
- Exportación de datos a CSV y Excel

---

## 2. Requisitos del Sistema

### Locales

| Requisito | Versión Mínima |
|-----------|----------------|
| Python | 3.12 |
| pip | Última versión estable |
| Navegador | Chrome 90+, Firefox 88+, Edge 90+ |

### Dependencias Principales

| Paquete | Versión Mínima | Propósito |
|---------|----------------|-----------|
| streamlit | 1.35.0 | Framework web interactivo |
| plotly | 5.20.0 | Gráficos interactivos |
| pandas | 2.2.0 | Manipulación de datos |
| numpy | 1.26.0 | Operaciones numéricas |
| openpyxl | 3.1.2 | Lectura de archivos Excel |

---

## 3. Instalación y Ejecución

### 3.1 Entorno Virtual (Recomendado)

```powershell
# Crear entorno virtual
python -m venv .venv

# Activar entorno virtual
.venv\Scripts\activate

# Instalar dependencias
pip install -r requirements.txt
```

### 3.2 Ejecutar el Dashboard

```powershell
.venv\Scripts\activate
streamlit run app.py
```

La aplicación se abrirá automáticamente en `http://localhost:8501`.

### 3.3 Ejecutar con Docker

```powershell
docker-compose up --build
```

### 3.4 Acceso en Línea

El dashboard está disponible en: **https://phyton.streamlit.app**

---

## 4. Estructura del Dashboard

El dashboard está organizado en **tres vistas principales**, cada una enfocada en un nivel distinto de análisis:

### Página Principal (`app.py`)

Al iniciar la aplicación verás:

1. **Encabezado superior** con el logo de la empresa y un indicador "LIVE" en verde
2. **Tres KPIS de resumen**:
   - Venta Neta Total
   - Margen Bruto Total
   - Clientes Activos
3. **Tres tarjetas de navegación** para acceder a cada vista
4. **Sección "Acerca de"** expandible con información del proyecto

### Navegación

Usa la **barra lateral izquierda** o las **tarjetas en la página principal** para cambiar entre vistas.

---

## 5. Barra Lateral de Navegación y Filtros

### Navegación

En la parte superior de la barra lateral encontrarás enlaces directos a cada página:

- **Inicio** — Página principal con resumen
- **Vista Gerencial** — Indicadores de alto nivel
- **Vista Estratégica** — Análisis de rentabilidad y portafolio
- **Vista Operativa** — Detalle transaccional

### Panel de Filtros

Debajo de la navegación se encuentra el **panel de filtros globales** que afectan a todas las vistas:

| Filtro | Descripción |
|--------|-------------|
| **Año** | Selección múltiple de años (2023, 2024) |
| **Mes** | Selección múltiple de meses (Enero a Junio) |
| **Canal** | Selección múltiple de canales de venta |
| **Categoría** | Selección de categorías de producto (afecta las marcas disponibles) |
| **Marca** | Selección de marcas (depende de la categoría seleccionada) |
| **Segmento** | Selección de segmentos de cliente |
| **Sucursal/Regional** | Selección de sucursales o regionales |
| **Ejecutivo** | Selección de ejecutivos de venta |
| **Rango de Fechas** | Selector de fecha de inicio y fecha de fin |

### Botones Rápidos de Periodo

- **MTD** — Mes a la fecha (Month to Date)
- **QTD** — Trimestre a la fecha (Quarter to Date)
- **YTD** — Año a la fecha (Year to Date)
- **Reset** — Restablece todos los filtros a sus valores por defecto

---

## 6. Vista Gerencial (Página 1)

**Propósito:** Monitoreo ejecutivo de alto nivel con indicadores agregados y tendencias.

### Componentes

#### 6.1 Tarjetas KPI (6 indicadores)

Cada tarjeta muestra:

- **Valor actual** del indicador
- **Variación Mes contra Mes (MoM)** expresada como porcentaje y color (verde = mejora, rojo = empeora)
- **Variación Año contra Año (YoY)** expresada como porcentaje y color

Los 6 KPIs son:

1. **Venta Neta** — Ingresos netos totales después de descuentos
2. **Margen Bruto** — Ganancia bruta total
3. **Margen %** — Porcentaje de margen sobre venta neta
4. **Ticket Promedio** — Valor promedio por transacción
5. **Cumplimiento de Meta** — Porcentaje de venta alcanzado vs. meta asignada
6. **Clientes Activos** — Número de clientes que compraron en el periodo

#### 6.2 Tendencia Mensual

Gráfico de **línea** que muestra la evolución mensual de una métrica seleccionable a lo largo del tiempo.

#### 6.3 Matriz 2x2 de Indicadores

Cuatro gráficos organizados en cuadrícula:

| Cuadrante | Contenido |
|-----------|-----------|
| **Venta por Canal** | Gráfico de barras con distribución de ventas por canal |
| **Margen por Categoría** | Gráfico de barras con margen bruto por categoría de producto |
| **Meta por Regional** | Gráfico de barras con cumplimiento de metas por región |
| **Clientes por Segmento** | Gráfico de donut con distribución de clientes por segmento |

#### 6.4 Tabla Resumen Regional

Tabla detallada con métricas (Venta Neta, Margen, % Margen, Cumplimiento) desglosadas por **Regional**.

Al hacer clic en el botón **"📥 Exportar Tabla"** se descarga la tabla en formato CSV.

---

## 7. Vista Estratégica (Página 2)

**Propósito:** Análisis profundo de rentabilidad, portafolio de productos y optimización.

### Componentes

#### 7.1 Rentabilidad por Categoría

Gráfico de **barras** que muestra la **Venta Neta** y **Margen Bruto** por categoría de producto, permitiendo identificar las categorías más rentables.

#### 7.2 Distribución por Región y Ciudad

- **Gráfico de barras** con ventas por región
- **Gráfico de barras** con ventas por ciudad (top 10)

#### 7.3 Ranking de Productos

- **Top 10** productos con mayores ventas netas
- **Bottom 10** productos con menores ventas netas
- Visualización en gráfico de barras horizontal

#### 7.4 Matriz de Dispersión (4 Cuadrantes)

Gráfico de **dispersión** que cruza:

- **Eje X:** Volumen de ventas
- **Eje Y:** Porcentaje de margen
- **Tamaño de burbuja:** Cantidad vendida
- **Color:** Categoría de producto

Incluye una **línea de tendencia OLS** para identificar correlaciones.

Los productos en el **cuadrante superior derecho** son los de mejor rendimiento (altas ventas + alto margen).

#### 7.5 Treemap Jerárquico

Visualización de **áreas proporcionales** que muestra la jerarquía:

`Categoría → Marca → Producto`

El tamaño del rectángulo representa el volumen de venta; el color representa el margen porcentual.

#### 7.6 Análisis ABC (Pareto)

Gráfico de **Pareto** con:

- **Barras:** Ventas por producto ordenadas de mayor a menor
- **Línea roja:** Porcentaje acumulado
- **Línea punteada:** Referencia del 80%

Identifica los productos **A** (80% de la venta acumulada) que son críticos para el negocio.

#### 7.7 Productos con Bajo Margen

Tabla que lista los productos con **margen menor al 5%**, ayudando a identificar artículos con problemas de rentabilidad.

---

## 8. Vista Operativa (Página 3)

**Propósito:** Análisis detallado de transacciones y desempeño operativo.

### Componentes

#### 8.1 Panel de Filtro de Transacciones

Filtros específicos para el detalle transaccional:

| Filtro | Opciones |
|--------|----------|
| **Canal** | Todos / Distribuidor / Corporativo / Tienda Física / E-commerce |
| **Categoría** | Todas las categorías disponibles |
| **Regional** | Todas las regionales disponibles |

#### 8.2 Detalle de Transacciones

Tabla interactiva con las siguientes columnas:

- Fecha
- Canal
- Producto
- Categoría
- Marca
- Cantidad
- Venta Neta
- Descuento %
- Cliente
- Ejecutivo
- Regional

La tabla se actualiza automáticamente al aplicar filtros.

#### 8.3 Top 10 Ejecutivos

Gráfico de **barras** con los 10 ejecutivos de venta con mayor facturación en el periodo seleccionado.

#### 8.4 Top 10 Clientes

Gráfico de **barras horizontales** con los 10 clientes que más han comprado.

#### 8.5 Análisis de Descuentos

Tabla que muestra las transacciones con **descuentos superiores al 20%**, permitiendo identificar:

- Productos con márgenes comprometidos
- Patrones de descuento excesivo
- Oportunidades de optimización de precios

#### 8.6 Exportación de Datos

- **"📥 Exportar Transacciones a CSV"** — Descarga el detalle de transacciones filtrado
- **"📥 Exportar a Excel"** — Descarga en formato Excel con múltiples hojas

---

## 9. Indicadores Clave (KPIs)

El dashboard utiliza **9 medidas maestras** calculadas sobre datos confirmados:

| # | KPI | Fórmula | Unidad |
|---|-----|---------|--------|
| 1 | **Venta Bruta** | Suma de Precio_Unitario * Cantidad | Bolivianos (Bs) |
| 2 | **Venta Neta** | Venta Bruta - Descuento | Bolivianos (Bs) |
| 3 | **Costo Total** | Suma de Costo_Unitario * Cantidad | Bolivianos (Bs) |
| 4 | **Margen Bruto** | Venta Neta - Costo Total | Bolivianos (Bs) |
| 5 | **Margen %** | (Margen Bruto / Venta Neta) * 100 | Porcentaje |
| 6 | **Ticket Promedio** | Venta Neta / Número de Transacciones | Bolivianos (Bs) |
| 7 | **Cantidad Vendida** | Suma de Cantidad de productos | Unidades |
| 8 | **Clientes Activos** | Conteo de clientes distintos con compras | Número |
| 9 | **Cumplimiento de Meta** | (Venta Neta / Meta Asignada) * 100 | Porcentaje |

**Nota importante:** Todos los KPIs se calculan **exclusivamente** sobre transacciones con estado `Confirmada`. Las transacciones anuladas o pendientes no se incluyen en ningún cálculo.

---

## 10. Interpretación de Tarjetas KPI

Cada tarjeta KPI incluye indicadores visuales de tendencia:

### Indicadores de Variación

- **▲ (Triángulo verde hacia arriba):** El indicador mejoró respecto al periodo anterior
- **▼ (Triángulo rojo hacia abajo):** El indicador empeoró respecto al periodo anterior

### Variaciones Mostradas

| Indicador | Significado |
|-----------|-------------|
| **MoM** (Mes vs Mes anterior) | `(Valor Mes Actual - Valor Mes Anterior) / Valor Mes Anterior * 100` |
| **YoY** (Año vs Año anterior) | `(Valor Mes Actual - Valor Mismo Mes Año Anterior) / Valor Mismo Mes Año Anterior * 100` |

### Colores de Fondo

- **Verde:** El valor de la variación es positivo (mejora)
- **Rojo:** El valor de la variación es negativo (empeora)
- **Gris:** No hay datos del periodo anterior para comparar

---

## 11. Filtros y Segmentación

### Filtros en Cascada

Los filtros de **Categoría** y **Marca** están relacionados en cascada:

1. Al seleccionar una o más categorías, el filtro de marcas se actualiza para mostrar solo las marcas pertenecientes a esas categorías
2. Si no se selecciona ninguna categoría, se muestran todas las marcas disponibles

### Persistencia de Filtros

Los filtros se mantienen al navegar entre páginas gracias al almacenamiento en `st.session_state`. Puedes cambiar de vista sin perder las selecciones actuales.

### Restablecer Filtros

Usa el botón **"🔄 Reset"** en la barra lateral para limpiar todos los filtros y volver al estado inicial.

---

## 12. Exportación de Datos

### Formatos Disponibles

| Formato | Cómo Exportar |
|---------|---------------|
| **CSV** | Botón "📥 Exportar Tabla" o "📥 Exportar Transacciones a CSV" |
| **Excel** | Botón "📥 Exportar a Excel" (Vista Operativa) |

### Datos Exportables

- Tablas de resumen regional (Vista Gerencial)
- Detalle de transacciones filtrado (Vista Operativa)
- La exportación incluye **solo los datos visibles** según los filtros aplicados

---

## 13. Preguntas de Negocio

El dashboard está diseñado para responder **10 preguntas clave de negocio**:

| # | Pregunta | Dónde Encontrarla |
|---|----------|-------------------|
| 1 | ¿Cuál es la venta total del período? | Página Principal + Vista Gerencial |
| 2 | ¿Cuál es el margen bruto y porcentaje de margen? | Vista Gerencial (tarjetas KPI) |
| 3 | ¿Cómo varían las ventas por canal? | Vista Gerencial (matriz 2x2) |
| 4 | ¿Cuál es la rentabilidad por categoría de producto? | Vista Estratégica (rentabilidad por categoría) |
| 5 | ¿Cuáles son los productos más y menos vendidos? | Vista Estratégica (ranking top/bottom 10) |
| 6 | ¿Cómo es el cumplimiento de metas por regional? | Vista Gerencial (matriz 2x2 + tabla regional) |
| 7 | ¿Cuáles son los clientes con mayores compras? | Vista Operativa (top 10 clientes) |
| 8 | ¿Cuáles son los ejecutivos con mejor desempeño? | Vista Operativa (top 10 ejecutivos) |
| 9 | ¿Cuál es la distribución geográfica de ventas? | Vista Estratégica (distribución región/ciudad) |
| 10| ¿Qué productos tienen bajo margen y requieren atención? | Vista Estratégica (productos margen < 5%) |

---

## 14. Solución de Problemas

### La aplicación no carga

1. Verifica que el entorno virtual esté activado
2. Confirma que todas las dependencias estén instaladas:
   ```powershell
   pip install -r requirements.txt
   ```
3. Revisa que el archivo `bbdd_prueba.xlsx` exista en la raíz del proyecto

### Los filtros no funcionan correctamente

- Usa el botón **"🔄 Reset"** en la barra lateral para restablecer todos los filtros
- Recarga la página en el navegador

### Los gráficos no se muestran

- Verifica que el navegador esté actualizado
- Prueba en modo incógnito para descartar problemas de caché
- Revisa la consola de desarrollador del navegador (F12) para errores

### La aplicación está lenta

- Reduce el rango de fechas seleccionado
- Selecciona menos categorías o canales simultáneamente
- Cierra otras aplicaciones que consuman memoria

### Error de conexión a base de datos (Supabase)

El dashboard **funciona completamente offline** usando el archivo Excel. Si ves errores de conexión a Supabase, ignóralos — la aplicación seguirá funcionando sin problemas.

### El archivo Excel no se encuentra

Asegúrate de que `bbdd_prueba.xlsx` esté en la carpeta raíz (`C:\Users\lenov\Desktop\PHYTON TRABAJO\`). El dashboard espera encontrar este archivo para cargar los datos.

---

## Contacto y Soporte

Para reportar problemas o solicitar mejoras, contacta al equipo de desarrollo a través del repositorio del proyecto.

---

*Documento generado el Julio 2026 — Versión 1.0*
