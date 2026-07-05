-- ============================================================
-- QUERIES — Dashboard Comercial Andina S.A.
-- Estrategia: CTEs para consultas complejas, JOINs explícitos,
-- filtros tempranos para reducir el set de datos antes de agregar.
-- ============================================================

-- 1. KPI: Venta Neta Total (filtrada por Confirmada)
SELECT COALESCE(SUM(venta_neta), 0) AS venta_neta_total
FROM fact_ventas
WHERE estado_venta = 'Confirmada';

-- 2. KPI: Margen Bruto Total
SELECT COALESCE(SUM(margen_bruto), 0) AS margen_bruto_total
FROM fact_ventas
WHERE estado_venta = 'Confirmada';

-- 3. KPI: Margen % General
SELECT
    CASE WHEN SUM(venta_neta) > 0
        THEN SUM(margen_bruto) / SUM(venta_neta)
        ELSE 0
    END AS margen_pct_general
FROM fact_ventas
WHERE estado_venta = 'Confirmada';

-- 4. KPI: Ticket Promedio
SELECT
    SUM(venta_neta) / NULLIF(COUNT(DISTINCT id_transaccion), 0) AS ticket_promedio
FROM fact_ventas
WHERE estado_venta = 'Confirmada';

-- 5. Canal con mayor Venta Neta
SELECT
    canal,
    SUM(venta_neta) AS total_venta_neta
FROM fact_ventas
WHERE estado_venta = 'Confirmada'
GROUP BY canal
ORDER BY total_venta_neta DESC
LIMIT 1;

-- 6. Categoría con mayor Margen Bruto
SELECT
    p.categoria,
    SUM(v.margen_bruto) AS total_margen_bruto
FROM fact_ventas v
JOIN dim_productos p ON v.codigo_producto_homologado = p.codigo_producto_homologado
WHERE v.estado_venta = 'Confirmada'
GROUP BY p.categoria
ORDER BY total_margen_bruto DESC
LIMIT 1;

-- 7. Regional con mayor cumplimiento de meta
WITH metas_reg AS (
    SELECT regional, SUM(meta_venta_neta) AS meta_total
    FROM fact_metas
    GROUP BY regional
),
ventas_reg AS (
    SELECT s.regional, SUM(v.venta_neta) AS venta_total
    FROM fact_ventas v
    JOIN dim_sucursales s ON v.id_sucursal = s.id_sucursal
    WHERE v.estado_venta = 'Confirmada'
    GROUP BY s.regional
)
SELECT vr.regional, vr.venta_total / NULLIF(mr.meta_total, 0) AS cumplimiento
FROM ventas_reg vr
JOIN metas_reg mr ON vr.regional = mr.regional
ORDER BY cumplimiento DESC
LIMIT 1;

-- 8. Ejecutivo con mayor Venta Neta
SELECT
    ejecutivo_venta,
    SUM(venta_neta) AS total_venta_neta
FROM fact_ventas
WHERE estado_venta = 'Confirmada'
GROUP BY ejecutivo_venta
ORDER BY total_venta_neta DESC
LIMIT 1;

-- 9. Producto con menor Margen %
WITH producto_margen AS (
    SELECT
        p.producto,
        SUM(v.venta_neta) AS venta_neta,
        SUM(v.margen_bruto) AS margen_bruto
    FROM fact_ventas v
    JOIN dim_productos p ON v.codigo_producto_homologado = p.codigo_producto_homologado
    WHERE v.estado_venta = 'Confirmada'
    GROUP BY p.producto
    HAVING SUM(v.venta_neta) > 0
)
SELECT
    producto,
    margen_bruto / venta_neta AS margen_pct
FROM producto_margen
ORDER BY margen_pct ASC
LIMIT 1;

-- 10. Cliente con mayor compra acumulada
SELECT
    c.id_cliente,
    c.cliente,
    SUM(v.venta_neta) AS compra_acumulada
FROM fact_ventas v
JOIN dim_clientes c ON v.id_cliente = c.id_cliente
WHERE v.estado_venta = 'Confirmada'
GROUP BY c.id_cliente, c.cliente
ORDER BY compra_acumulada DESC
LIMIT 1;

-- 11. Transacciones con descuento mayor al 20%
SELECT COUNT(DISTINCT id_transaccion) AS transacciones_alto_descuento
FROM fact_ventas
WHERE estado_venta = 'Confirmada'
  AND descuento_pct > 0.20;

-- 12. Tendencia mensual de Venta Neta (Vista Gerencial)
SELECT
    periodo,
    anio,
    mes,
    SUM(venta_neta) AS venta_neta,
    SUM(margen_bruto) AS margen_bruto,
    COUNT(DISTINCT id_transaccion) AS transacciones,
    COUNT(DISTINCT id_cliente) AS clientes_activos
FROM fact_ventas
WHERE estado_venta = 'Confirmada'
GROUP BY periodo, anio, mes
ORDER BY anio, mes;

-- 13. Ventas por Canal y Regional (tabla dinámica, Vista Gerencial)
SELECT
    s.regional,
    v.canal,
    SUM(v.venta_neta) AS venta_neta,
    SUM(v.margen_bruto) AS margen_bruto,
    SUM(v.cantidad) AS cantidad_vendida,
    COUNT(DISTINCT v.id_transaccion) AS transacciones
FROM fact_ventas v
JOIN dim_sucursales s ON v.id_sucursal = s.id_sucursal
WHERE v.estado_venta = 'Confirmada'
GROUP BY s.regional, v.canal
ORDER BY s.regional, v.canal;

-- 14. Ranking de productos por Venta Neta (Vista Estratégica)
SELECT
    p.producto,
    p.categoria,
    SUM(v.venta_neta) AS venta_neta,
    SUM(v.margen_bruto) AS margen_bruto,
    SUM(v.cantidad) AS cantidad_vendida,
    COUNT(DISTINCT v.id_transaccion) AS transacciones
FROM fact_ventas v
JOIN dim_productos p ON v.codigo_producto_homologado = p.codigo_producto_homologado
WHERE v.estado_venta = 'Confirmada'
GROUP BY p.producto, p.categoria
ORDER BY venta_neta DESC;

-- 15. Detalle transaccional (Vista Operativa)
SELECT
    v.id_transaccion,
    v.fecha,
    v.canal,
    c.cliente,
    c.segmento,
    p.producto,
    p.categoria,
    s.sucursal,
    s.regional,
    v.ejecutivo_venta,
    v.cantidad,
    v.precio_unitario,
    v.descuento_pct,
    v.venta_bruta,
    v.descuento_valor,
    v.venta_neta,
    v.costo_total,
    v.margen_bruto,
    v.margen_pct
FROM fact_ventas v
JOIN dim_clientes c ON v.id_cliente = c.id_cliente
JOIN dim_productos p ON v.codigo_producto_homologado = p.codigo_producto_homologado
JOIN dim_sucursales s ON v.id_sucursal = s.id_sucursal
WHERE v.estado_venta = 'Confirmada'
ORDER BY v.fecha DESC;
