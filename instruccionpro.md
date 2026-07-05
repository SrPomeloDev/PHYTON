
# PROMPT — Corrección quirúrgica + diseño profesional

## Dashboard Comercial Andina S.A.

Eres un Arquitecto de Datos + Frontend Engineer senior. Vas a trabajar sobre un
proyecto **que ya funciona en gran parte**. Tu misión NO es reescribirlo desde
cero ni "modernizarlo" con otro stack. Tu misión es:

1. Corregir errores puntuales y confirmados.
2. Elevar el diseño visual de las 3 vistas Streamlit a nivel profesional/C-suite.

---

## 🚫 REGLAS DURAS — NO ROMPER LO QUE YA SIRVE

- NO cambies nombres de tablas ni columnas en `schema.sql` (`dim_productos`,
  `dim_clientes`, `dim_sucursales`, `dim_homologacion`, `fact_ventas`,
  `fact_metas`, todo en snake_case). Ya está bien y las queries dependen de eso.
- NO cambies el driver de conexión. El proyecto usa `SQLAlchemy` + `psycopg2`
  directo contra Supabase/Postgres (ver `config/database.py` y `etl.py`).
  No introduzcas el cliente `supabase-py` ni reemplaces `engine.begin()`.
- NO renombres archivos ni carpetas de la estructura ya definida en
  `AGENTS.md` (`pages/`, `services/`, `components/`, `utils/`, `config/`, `sql/`).
- NO toques `queries.sql` salvo el bug puntual indicado abajo (query 7).
- NO agregues RLS, vistas materializadas, `dim_tiempo`, ni funciones PL/pgSQL
  nuevas — no fueron pedidas y agregan complejidad innecesaria para el alcance
  de esta prueba.
- Cualquier cambio de esquema o de contrato de función debe ir acompañado de
  una migración explícita y de actualizar TODOS los lugares que lo consumen
  (queries, etl, metrics, pages) — no dejes referencias rotas.
- Si tienes dudas sobre si algo "ya sirve", ejecútalo primero y compara el
  resultado antes/después. No asumas.

---

## ✅ BUGS CONFIRMADOS A CORREGIR (en este orden)

### 1. `queries.sql` — Query 7 (Regional con mayor cumplimiento de meta)

Bug: el `LEFT JOIN` fila-a-fila contra `fact_metas` genera fan-out y usar
`MAX(m.meta_venta_neta)` descarta metas de otras combinaciones mes/canal
para la misma regional, subestimando el denominador.

Corrige agregando las metas por regional en un CTE separado antes de cruzar
(sin duplicar), por ejemplo:

```sql
WITH metas_reg AS (
  SELECT regional, SUM(meta_venta_neta) AS meta_total
  FROM fact_metas GROUP BY regional
),
ventas_reg AS (
  SELECT s.regional, SUM(v.venta_neta) AS venta_total
  FROM fact_ventas v
  JOIN dim_sucursales s ON v.id_sucursal = s.id_sucursal
  WHERE v.estado_venta = 'Confirmada'
  GROUP BY s.regional
)
SELECT vr.regional, vr.venta_total / NULLIF(mr.meta_total, 0) AS cumplimiento
FROM ventas_reg vr JOIN metas_reg mr ON vr.regional = mr.regional
ORDER BY cumplimiento DESC LIMIT 1;
```

Verifica que el resultado sea coherente con `get_cumplimiento_meta()` en
`metrics.py` para el mismo recorte de datos.

### 2. `etl.py` — `homologar_productos()`, fallback inseguro

```python
ventas["Codigo_Producto_Homologado"] = ventas["Codigo_Producto_Homologado"].fillna(ventas["Codigo_Producto"])
```

Si algún `Codigo_Producto` no homologa, el fallback asigna un código que no
existe como PK en `dim_productos`, y la FK de `fact_ventas` rompe el INSERT
completo del chunk.

Corrige así: loguea con `logger.warning` cada código sin homologar con su
`ID_Transaccion`, y EXCLUYE esas filas de la carga a `fact_ventas` (no las
inventes ni las fuerces). Deja un conteo final en el log de cuántas filas se
excluyeron por esta causa, para que quede visible en el reporte ETL.

### 3. `metrics.py` — filtro de `Estado_Venta` no garantizado

Ninguna función valida que el DataFrame recibido ya esté filtrado por
`Estado_Venta == 'Confirmada'`. Agrega una validación defensiva ligera (no
un re-filtro silencioso que oculte errores de quien llama):

```python
def _assert_confirmada(df: pd.DataFrame) -> None:
    if "Estado_Venta" in df.columns and (df["Estado_Venta"] != "Confirmada").any():
        raise ValueError(
            "El DataFrame contiene ventas no confirmadas; "
            "filtra por Estado_Venta == 'Confirmada' antes de calcular métricas."
        )
```

Llama a `_assert_confirmada(df)` al inicio de cada función que reciba un
DataFrame de ventas. Si `Estado_Venta` no está en las columnas (porque el
caller ya lo descartó tras filtrar), no falles — solo valida cuando la
columna esté presente.

### 4. `AGENTS.md` — conteos de filas incorrectos

Corrige la tabla de "Tablas (bbdd_prueba.xlsx)":

- `PRODUCTOS` → son 120 filas, no 600.
- `CLIENTES` → son 600 filas, no 480.
  (SUCURSAL=16, HOMOLOGACIÓN=480, METAS=288, VENTAS=10.000 ya están correctos,
  no los toques.)

---

## 🎨 MEJORA DE DISEÑO — PÁGINAS STREAMLIT (Gerencial, Estratégica, Operativa)

Objetivo: que se vea diseñado por un experto en UI para dashboards ejecutivos,
sin cambiar la lógica de negocio ni las fuentes de datos.

Antes de tocar cualquier componente visual, **lee y aplica**
`/mnt/skills/public/frontend-design/SKILL.md` — contiene los tokens de diseño,
tipografía y restricciones del entorno. No inventes estilos por tu cuenta.

Lineamientos específicos:

- Jerarquía visual clara: KPIs principales arriba en tarjetas, luego
  tendencias, luego detalle tabular — en ese orden en las 3 vistas.
- Una sola paleta de color coherente en toda la app (defínela una vez en
  `config/style.py` o `assets/style.css`, no la repitas hardcodeada en cada
  página).
- Tipografía consistente, buen contraste, espaciado generoso — nada apretado
  ni con `st.write` plano para números importantes.
- Gráficos Plotly con `template="plotly_white"`, sin leyendas redundantes,
  con hover claro y ejes con formato de moneda/porcentaje ya aplicado
  (usa `utils/formatting.py`, no formatees inline en cada gráfico).
- Filtros de la barra lateral agrupados lógicamente (periodo, canal,
  regional, categoría) y con estado persistente entre vistas si el usuario
  navega de una página a otra.
- Estados vacíos y de carga (`st.spinner`, mensajes cuando un filtro no
  devuelve datos) — nada de pantallas en blanco o tracebacks visibles.
- Responsive: que no se rompa el layout en pantallas angostas.

No agregues librerías nuevas fuera de las ya listadas en `AGENTS.md`
(Streamlit, Plotly, Pandas, SQLAlchemy). Si crees que falta algo, dime cuál y
por qué antes de instalarlo.

---

## 🔍 PROCESO DE TRABAJO OBLIGATORIO

1. Antes de tocar código, corre lo que ya existe y confirma qué funciona hoy
   (ETL, queries, la app si ya levanta).
2. Aplica los 4 bugs de arriba, uno por uno, con commits/diffs separados.
3. Vuelve a correr las 10 preguntas de validación práctica (sección 7 de
   `Instrucciones_Pasantías.docx`) y compara resultados antes/después de tus
   cambios — deben seguir siendo consistentes salvo donde el bug los estaba
   distorsionando (query 7).
4. Recién después de validar que nada se rompió, entra al Módulo de diseño.
5. Al final, entrega un resumen corto: qué corregiste, qué cambió en los
   resultados de las preguntas de validación (si algo cambió), y qué mejoras
   de diseño aplicaste.

No hagas cambios "de paso" que no estén en esta lista. Si ves algo más que
valdría la pena corregir, anótalo aparte y pregúntame antes de tocarlo.
