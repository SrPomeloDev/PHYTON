-- ============================================================
-- VIEWS — Dashboard Comercial Andina S.A.
-- Estrategia: Vistas materializadas para agregaciones pesadas
-- que se refrescan diariamente. Vistas regulares para consultas
-- en tiempo real que requieren datos al segundo.
-- ============================================================

-- 1. VISTA RESUMEN MENSUAL (usada en Vista Gerencial)
CREATE MATERIALIZED VIEW IF NOT EXISTS mv_resumen_mensual AS
SELECT
    v.anio,
    v.mes,
    v.periodo,
    v.canal,
    s.regional,
    COUNT(DISTINCT v.id_transaccion) AS total_transacciones,
    COUNT(DISTINCT v.id_cliente) AS clientes_activos,
    SUM(v.cantidad) AS cantidad_vendida,
    SUM(v.venta_neta) AS venta_neta,
    SUM(v.margen_bruto) AS margen_bruto,
    CASE WHEN SUM(v.venta_neta) > 0
        THEN SUM(v.margen_bruto) / SUM(v.venta_neta)
        ELSE 0
    END AS margen_pct,
    SUM(v.venta_neta) / NULLIF(COUNT(DISTINCT v.id_transaccion), 0) AS ticket_promedio
FROM fact_ventas v
LEFT JOIN dim_sucursales s ON v.id_sucursal = s.id_sucursal
WHERE v.estado_venta = 'Confirmada'
GROUP BY v.anio, v.mes, v.periodo, v.canal, s.regional
WITH DATA;

CREATE UNIQUE INDEX IF NOT EXISTS idx_mv_resumen_mensual
ON mv_resumen_mensual (anio, mes, canal, regional);

-- 2. VISTA RENTABILIDAD POR CATEGORÍA (usada en Vista Estratégica)
CREATE MATERIALIZED VIEW IF NOT EXISTS mv_rentabilidad_categoria AS
SELECT
    p.categoria,
    p.subcategoria,
    COUNT(DISTINCT v.id_transaccion) AS transacciones,
    SUM(v.cantidad) AS cantidad_vendida,
    SUM(v.venta_neta) AS venta_neta,
    SUM(v.margen_bruto) AS margen_bruto,
    CASE WHEN SUM(v.venta_neta) > 0
        THEN SUM(v.margen_bruto) / SUM(v.venta_neta)
        ELSE 0
    END AS margen_pct
FROM fact_ventas v
JOIN dim_productos p ON v.codigo_producto_homologado = p.codigo_producto_homologado
WHERE v.estado_venta = 'Confirmada'
GROUP BY p.categoria, p.subcategoria
WITH DATA;

CREATE UNIQUE INDEX IF NOT EXISTS idx_mv_rentabilidad_categoria
ON mv_rentabilidad_categoria (categoria, subcategoria);

-- 3. VISTA RANKING PRODUCTOS (usada en Vista Estratégica)
CREATE MATERIALIZED VIEW IF NOT EXISTS mv_ranking_productos AS
SELECT
    p.codigo_producto_homologado,
    p.producto,
    p.categoria,
    p.subcategoria,
    p.marca,
    COUNT(DISTINCT v.id_transaccion) AS transacciones,
    SUM(v.cantidad) AS cantidad_vendida,
    SUM(v.venta_neta) AS venta_neta,
    SUM(v.margen_bruto) AS margen_bruto,
    CASE WHEN SUM(v.venta_neta) > 0
        THEN SUM(v.margen_bruto) / SUM(v.venta_neta)
        ELSE 0
    END AS margen_pct
FROM fact_ventas v
JOIN dim_productos p ON v.codigo_producto_homologado = p.codigo_producto_homologado
WHERE v.estado_venta = 'Confirmada'
GROUP BY p.codigo_producto_homologado, p.producto, p.categoria, p.subcategoria, p.marca
WITH DATA;

CREATE UNIQUE INDEX IF NOT EXISTS idx_mv_ranking_productos
ON mv_ranking_productos (codigo_producto_homologado);

-- 4. VISTA CUMPLIMIENTO METAS (usada en Vista Gerencial)
CREATE MATERIALIZED VIEW IF NOT EXISTS mv_cumplimiento_metas AS
SELECT
    v.anio,
    v.mes,
    v.canal,
    s.regional,
    SUM(v.venta_neta) AS venta_neta_real,
    SUM(v.margen_bruto) AS margen_real,
    MAX(m.meta_venta_neta) AS meta_venta_neta,
    MAX(m.meta_margen) AS meta_margen,
    CASE WHEN MAX(m.meta_venta_neta) > 0
        THEN SUM(v.venta_neta) / MAX(m.meta_venta_neta)
        ELSE NULL
    END AS cumplimiento_venta,
    CASE WHEN MAX(m.meta_margen) > 0
        THEN SUM(v.margen_bruto) / MAX(m.meta_margen)
        ELSE NULL
    END AS cumplimiento_margen
FROM fact_ventas v
LEFT JOIN dim_sucursales s ON v.id_sucursal = s.id_sucursal
LEFT JOIN fact_metas m ON m.key_meta = v.anio || '|' || v.mes || '|' || v.canal || '|' || s.regional
WHERE v.estado_venta = 'Confirmada'
GROUP BY v.anio, v.mes, v.canal, s.regional
WITH DATA;

CREATE UNIQUE INDEX IF NOT EXISTS idx_mv_cumplimiento_metas
ON mv_cumplimiento_metas (anio, mes, canal, regional);

-- 5. VISTA TOP CLIENTES (usada en Vista Operativa)
CREATE MATERIALIZED VIEW IF NOT EXISTS mv_top_clientes AS
SELECT
    c.id_cliente,
    c.cliente,
    c.segmento,
    c.ciudad,
    COUNT(DISTINCT v.id_transaccion) AS transacciones,
    SUM(v.venta_neta) AS compra_acumulada,
    SUM(v.margen_bruto) AS margen_generado,
    COUNT(DISTINCT v.codigo_producto_homologado) AS productos_distintos
FROM fact_ventas v
JOIN dim_clientes c ON v.id_cliente = c.id_cliente
WHERE v.estado_venta = 'Confirmada'
GROUP BY c.id_cliente, c.cliente, c.segmento, c.ciudad
WITH DATA;

CREATE UNIQUE INDEX IF NOT EXISTS idx_mv_top_clientes
ON mv_top_clientes (id_cliente);

-- 6. VISTA RENDIMIENTO EJECUTIVOS
CREATE MATERIALIZED VIEW IF NOT EXISTS mv_rendimiento_ejecutivos AS
SELECT
    v.ejecutivo_venta,
    COUNT(DISTINCT v.id_transaccion) AS transacciones,
    COUNT(DISTINCT v.id_cliente) AS clientes_atendidos,
    SUM(v.cantidad) AS cantidad_vendida,
    SUM(v.venta_neta) AS venta_neta,
    SUM(v.margen_bruto) AS margen_bruto,
    CASE WHEN SUM(v.venta_neta) > 0
        THEN SUM(v.margen_bruto) / SUM(v.venta_neta)
        ELSE 0
    END AS margen_pct
FROM fact_ventas v
WHERE v.estado_venta = 'Confirmada'
GROUP BY v.ejecutivo_venta
WITH DATA;

CREATE UNIQUE INDEX IF NOT EXISTS idx_mv_rendimiento_ejecutivos
ON mv_rendimiento_ejecutivos (ejecutivo_venta);

-- Función para refrescar todas las vistas materializadas
CREATE OR REPLACE FUNCTION refresh_materialized_views()
RETURNS void AS $$
BEGIN
    REFRESH MATERIALIZED VIEW CONCURRENTLY mv_resumen_mensual;
    REFRESH MATERIALIZED VIEW CONCURRENTLY mv_rentabilidad_categoria;
    REFRESH MATERIALIZED VIEW CONCURRENTLY mv_ranking_productos;
    REFRESH MATERIALIZED VIEW CONCURRENTLY mv_cumplimiento_metas;
    REFRESH MATERIALIZED VIEW CONCURRENTLY mv_top_clientes;
    REFRESH MATERIALIZED VIEW CONCURRENTLY mv_rendimiento_ejecutivos;
END;
$$ LANGUAGE plpgsql;
