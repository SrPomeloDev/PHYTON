-- ============================================================
-- SCHEMA: Dashboard Comercial Andina S.A.
-- Motor: Supabase (PostgreSQL 15+)
-- Modelo: Estrella — Ventas (hecho) + Dimensiones
-- ============================================================

-- 1. TABLAS DIMENSIÓN
-- ============================================================

CREATE TABLE IF NOT EXISTS dim_productos (
    codigo_producto_homologado VARCHAR(50) PRIMARY KEY,
    producto VARCHAR(200) NOT NULL,
    categoria VARCHAR(100),
    subcategoria VARCHAR(100),
    marca VARCHAR(100),
    estado_producto VARCHAR(50) DEFAULT 'Activo',
    precio_lista NUMERIC(12,2),
    costo_base NUMERIC(12,2),
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS dim_clientes (
    id_cliente VARCHAR(50) PRIMARY KEY,
    cliente VARCHAR(200) NOT NULL,
    segmento VARCHAR(100),
    ciudad VARCHAR(100),
    tipo_cliente VARCHAR(100),
    fecha_alta DATE,
    estado_cliente VARCHAR(50) DEFAULT 'Activo',
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS dim_sucursales (
    id_sucursal VARCHAR(50) PRIMARY KEY,
    sucursal VARCHAR(200) NOT NULL,
    ciudad_sucursal VARCHAR(100),
    regional VARCHAR(100),
    responsable_sucursal VARCHAR(200),
    formato_sucursal VARCHAR(100),
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS dim_homologacion (
    codigo_producto_origen VARCHAR(50) NOT NULL,
    codigo_producto_homologado VARCHAR(50) NOT NULL,
    tipo_codigo VARCHAR(50),
    PRIMARY KEY (codigo_producto_origen, codigo_producto_homologado),
    FOREIGN KEY (codigo_producto_homologado) REFERENCES dim_productos(codigo_producto_homologado)
);

-- 2. TABLA DE HECHOS: VENTAS
-- ============================================================

CREATE TABLE IF NOT EXISTS fact_ventas (
    id_transaccion VARCHAR(50) PRIMARY KEY,
    fecha_hora_transaccion TIMESTAMPTZ NOT NULL,
    fecha DATE NOT NULL,
    anio INTEGER NOT NULL,
    mes INTEGER NOT NULL,
    periodo VARCHAR(7) NOT NULL,
    codigo_producto_origen VARCHAR(50),
    codigo_producto_homologado VARCHAR(50),
    id_cliente VARCHAR(50),
    id_sucursal VARCHAR(50),
    canal VARCHAR(100),
    cantidad NUMERIC(12,4) NOT NULL DEFAULT 0,
    precio_unitario NUMERIC(12,2) NOT NULL DEFAULT 0,
    descuento_pct NUMERIC(5,4) DEFAULT 0,
    costo_unitario NUMERIC(12,2) DEFAULT 0,
    ejecutivo_venta VARCHAR(200),
    estado_venta VARCHAR(50) NOT NULL,
    venta_bruta NUMERIC(14,2) NOT NULL DEFAULT 0,
    descuento_valor NUMERIC(14,2) NOT NULL DEFAULT 0,
    venta_neta NUMERIC(14,2) NOT NULL DEFAULT 0,
    costo_total NUMERIC(14,2) NOT NULL DEFAULT 0,
    margen_bruto NUMERIC(14,2) NOT NULL DEFAULT 0,
    margen_pct NUMERIC(6,4) NOT NULL DEFAULT 0,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    FOREIGN KEY (codigo_producto_homologado) REFERENCES dim_productos(codigo_producto_homologado),
    FOREIGN KEY (id_cliente) REFERENCES dim_clientes(id_cliente),
    FOREIGN KEY (id_sucursal) REFERENCES dim_sucursales(id_sucursal)
);

CREATE INDEX IF NOT EXISTS idx_ventas_estado ON fact_ventas (estado_venta);
CREATE INDEX IF NOT EXISTS idx_ventas_fecha ON fact_ventas (fecha);
CREATE INDEX IF NOT EXISTS idx_ventas_canal ON fact_ventas (canal);
CREATE INDEX IF NOT EXISTS idx_ventas_anio_mes ON fact_ventas (anio, mes);

-- 3. TABLA DE METAS
-- ============================================================

CREATE TABLE IF NOT EXISTS fact_metas (
    id SERIAL PRIMARY KEY,
    anio INTEGER NOT NULL,
    mes INTEGER NOT NULL,
    canal VARCHAR(100) NOT NULL,
    regional VARCHAR(100) NOT NULL,
    key_meta VARCHAR(255) UNIQUE NOT NULL,
    meta_venta_neta NUMERIC(14,2) DEFAULT 0,
    meta_margen NUMERIC(14,2) DEFAULT 0,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_metas_key_meta ON fact_metas (key_meta);
