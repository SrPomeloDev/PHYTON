-- ============================================================
-- INDEXES — Dashboard Comercial Andina S.A.
-- Estrategia: Índices compuestos para cubrir los filtros y
-- agregaciones más frecuentes del dashboard.
-- ============================================================

-- Ventas: filtro por estado + agrupaciones temporales
CREATE INDEX IF NOT EXISTS idx_ventas_estado_fecha ON fact_ventas (estado_venta, fecha);
CREATE INDEX IF NOT EXISTS idx_ventas_anio_mes ON fact_ventas (anio, mes);
CREATE INDEX IF NOT EXISTS idx_ventas_canal ON fact_ventas (canal);
CREATE INDEX IF NOT EXISTS idx_ventas_regional ON fact_ventas (id_sucursal);
CREATE INDEX IF NOT EXISTS idx_ventas_ejecutivo ON fact_ventas (ejecutivo_venta);

-- Ventas: búsqueda por cliente y producto
CREATE INDEX IF NOT EXISTS idx_ventas_id_cliente ON fact_ventas (id_cliente);
CREATE INDEX IF NOT EXISTS idx_ventas_codigo_producto ON fact_ventas (codigo_producto_homologado);

-- Ventas: cubrir consultas comunes (evita seq scan en tablas grandes)
CREATE INDEX IF NOT EXISTS idx_ventas_confirmadas ON fact_ventas (estado_venta, anio, mes, canal)
    WHERE estado_venta = 'Confirmada';

-- Metas: búsqueda por key_meta
CREATE INDEX IF NOT EXISTS idx_metas_key_meta ON fact_metas (key_meta);
CREATE INDEX IF NOT EXISTS idx_metas_canal_regional ON fact_metas (canal, regional);

-- Productos: filtros de categoría
CREATE INDEX IF NOT EXISTS idx_productos_categoria ON dim_productos (categoria);
CREATE INDEX IF NOT EXISTS idx_productos_subcategoria ON dim_productos (subcategoria);
CREATE INDEX IF NOT EXISTS idx_productos_marca ON dim_productos (marca);

-- Clientes: búsqueda por segmento y ciudad
CREATE INDEX IF NOT EXISTS idx_clientes_segmento ON dim_clientes (segmento);
CREATE INDEX IF NOT EXISTS idx_clientes_ciudad ON dim_clientes (ciudad);
CREATE INDEX IF NOT EXISTS idx_clientes_estado ON dim_clientes (estado_cliente);

-- Sucursales: búsqueda por regional
CREATE INDEX IF NOT EXISTS idx_sucursales_regional ON dim_sucursales (regional);
CREATE INDEX IF NOT EXISTS idx_sucursales_ciudad ON dim_sucursales (ciudad_sucursal);

-- Homologación: búsqueda inversa
CREATE INDEX IF NOT EXISTS idx_homologacion_origen ON dim_homologacion (codigo_producto_origen);
CREATE INDEX IF NOT EXISTS idx_homologacion_homologado ON dim_homologacion (codigo_producto_homologado);
