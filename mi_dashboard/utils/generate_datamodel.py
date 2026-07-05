"""Genera el diagrama del modelo de datos (esquema estrella)."""
import os
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.patches import FancyBboxPatch

OUTPUT = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'assets', 'data_model.png')

def draw_table(ax, x, y, name, columns, color, pk_cols=None, width=2.8, row_height=0.35):
    """Dibuja una tabla como rectangulo con columnas."""
    if pk_cols is None:
        pk_cols = []
    n = len(columns) + 1  # +1 for header
    h = n * row_height + 0.1
    bbox = FancyBboxPatch((x - width/2, y - h), width, h, boxstyle="round,pad=0.05",
                          facecolor=color, edgecolor='white', linewidth=1.5, alpha=0.9)
    ax.add_patch(bbox)
    # Title / header
    ax.text(x, y - 0.15, name, fontsize=9, fontweight='bold', color='white',
            ha='center', va='top')
    # Columns
    for i, col in enumerate(columns):
        yy = y - 0.45 - i * row_height
        is_pk = col in pk_cols
        prefix = 'PK ' if is_pk else '   '
        color_col = '#e8d5f5' if is_pk else '#f0f0f0'
        ax.text(x - width/2 + 0.15, yy, prefix + col, fontsize=7, color='#1a1a2e',
                ha='left', va='top',
                bbox=dict(boxstyle='round,pad=0.02', facecolor=color_col, alpha=0.7, edgecolor='none'))

def draw_arrow(ax, x1, y1, x2, y2, label=''):
    """Dibuja una flecha entre dos tablas."""
    ax.annotate('', xy=(x2, y2), xytext=(x1, y1),
                arrowprops=dict(arrowstyle='->', color='#818cf8', lw=1.5, connectionstyle='arc3,rad=0.2'))
    if label:
        mx, my = (x1 + x2) / 2, (y1 + y2) / 2
        ax.text(mx + 0.1, my, label, fontsize=6, color='#818cf8', ha='center', va='center',
                style='italic')

fig, ax = plt.subplots(figsize=(16, 10))
ax.set_xlim(-1, 17)
ax.set_ylim(-1, 11)
ax.axis('off')
fig.patch.set_facecolor('#0B0F19')
ax.set_facecolor('#0B0F19')

# Title
ax.text(8, 10.5, 'MODELO ESTRELLA - Comercial Andina S.A.', fontsize=14, fontweight='bold',
        color='white', ha='center', va='center')
ax.text(8, 10.0, 'Hecho (fact_ventas) + 4 Dimensiones + Metas', fontsize=9,
        color='#a0aec0', ha='center', va='center')

# ===== DIMENSIONES =====

# Productos (top-left)
draw_table(ax, 1.8, 8.5, 'dim_productos', [
    'codigo_producto_homologado', 'producto', 'categoria', 'subcategoria',
    'marca', 'estado_producto', 'precio_lista', 'costo_base'
], '#2d3748', pk_cols=['codigo_producto_homologado'])

# Homologacion (left middle)
draw_table(ax, 1.8, 5.2, 'dim_homologacion', [
    'codigo_producto_origen (PK)', 'codigo_producto_homologado (PK)', 'tipo_codigo'
], '#2d3748', pk_cols=['codigo_producto_origen (PK)'], width=2.8)

# Clientes (top-right)
draw_table(ax, 14.2, 8.5, 'dim_clientes', [
    'id_cliente', 'cliente', 'segmento', 'ciudad',
    'tipo_cliente', 'fecha_alta', 'estado_cliente'
], '#2d3748', pk_cols=['id_cliente'])

# Sucursales (right middle)
draw_table(ax, 14.2, 5.2, 'dim_sucursales', [
    'id_sucursal', 'sucursal', 'ciudad_sucursal', 'regional',
    'responsable_sucursal', 'formato_sucursal'
], '#2d3748', pk_cols=['id_sucursal'])

# ===== TABLA DE HECHOS =====
draw_table(ax, 8, 5.2, 'fact_ventas', [
    'id_transaccion (PK)', 'fecha_hora_transaccion', 'fecha', 'anio', 'mes',
    'periodo', 'codigo_producto_origen', 'codigo_producto_homologado (FK)',
    'id_cliente (FK)', 'id_sucursal (FK)', 'canal', 'cantidad',
    'precio_unitario', 'descuento_pct', 'costo_unitario',
    'ejecutivo_venta', 'estado_venta',
    'venta_bruta', 'descuento_valor', 'venta_neta',
    'costo_total', 'margen_bruto', 'margen_pct'
], '#4338ca', pk_cols=['id_transaccion (PK)'], width=3.2, row_height=0.30)

# Metas (bottom-center)
draw_table(ax, 8, 1.5, 'fact_metas', [
    'id (PK)', 'anio', 'mes', 'canal', 'regional',
    'key_meta (UNIQUE)', 'meta_venta_neta', 'meta_margen'
], '#2d3748', pk_cols=['id (PK)'], width=2.8)

# ===== FLECHAS =====
# Productos -> Ventas
draw_arrow(ax, 3.4, 6.8, 6.2, 6.0, 'FK')
# Clientes -> Ventas
draw_arrow(ax, 12.6, 6.8, 9.8, 6.0, 'FK')
# Sucursales -> Ventas
draw_arrow(ax, 12.6, 5.8, 9.8, 5.4, 'FK')
# Homologacion -> Productos
draw_arrow(ax, 2.8, 4.8, 2.8, 6.2, '')

# Legend
legend_x, legend_y = 0.2, 0.3
ax.text(legend_x, legend_y, 'Leyenda:', fontsize=8, fontweight='bold', color='white')
ax.text(legend_x + 2, legend_y, 'Tablas Dimension', fontsize=7, color='#a0aec0')
ax.text(legend_x + 5.5, legend_y, 'Tabla de Hechos', fontsize=7, color='#a0aec0')
ax.text(legend_x + 9, legend_y, 'PK = Primary Key | FK = Foreign Key', fontsize=7, color='#a0aec0')

plt.tight_layout(pad=1)
os.makedirs(os.path.dirname(OUTPUT), exist_ok=True)
plt.savefig(OUTPUT, dpi=200, bbox_inches='tight', facecolor='#0B0F19')
print(f"Diagrama generado: {OUTPUT}")
