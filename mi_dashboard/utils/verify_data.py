# encoding: utf-8
from utils.cache import _run_etl

d = _run_etl()
v = d["ventas"]
p = d["productos"]
c = d["clientes"]
s = d["sucursales"]
m = d["metas"]
h = d["homologacion"]

ANIO = "A\u00f1o"

print("=" * 60)
print("VERIFICACION DE DATOS - Dashboard Andina S.A.")
print("=" * 60)

print("\n=== VENTAS ===")
print(f"  Filas totales: {len(v)}")
print(f"  Estado_Venta: {list(v['Estado_Venta'].unique())}")
print(f"  Canales: {list(v['Canal'].unique())}")
print(f"  A\u00f1os: {sorted(v[ANIO].unique())}")
print(f"  Meses: {sorted(v['Mes'].unique())}")
print(f"  Ejecutivos unicos: {v['Ejecutivo_Venta'].nunique()}")
print(f"  Clientes unicos: {v['ID_Cliente'].nunique()}")
print(f"  Sucursales unicas: {v['ID_Sucursal'].nunique()}")
print(f"  IDs duplicados: {v['ID_Transaccion'].duplicated().sum()}")
vb = (abs(v['Venta_Bruta'] - v['Cantidad'] * v['Precio_Unitario']) > 0.01).sum()
print(f"  Errores Venta_Bruta: {vb}")
vn = (abs(v['Venta_Neta'] - (v['Venta_Bruta'] - v['Descuento_Valor'])) > 0.01).sum()
print(f"  Errores Venta_Neta: {vn}")
mn = (abs(v['Margen_Bruto'] - (v['Venta_Neta'] - v['Costo_Total'])) > 0.01).sum()
print(f"  Errores Margen_Bruto: {mn}")

total_vn = v['Venta_Neta'].sum()
total_mb = v['Margen_Bruto'].sum()
print(f"  Venta Neta Total: {total_vn:,.2f}")
print(f"  Margen Bruto Total: {total_mb:,.2f}")
print(f"  Margen %%: {total_mb/total_vn*100:.2f}%%")
tp = total_vn / v['ID_Transaccion'].nunique()
print(f"  Ticket Promedio: {tp:,.2f}")
print(f"  Clientes Activos: {v['ID_Cliente'].nunique()}")

print("\n=== PRODUCTOS ===")
print(f"  Filas: {len(p)}")
print(f"  Categorias: {list(p['Categoria'].unique())}")
print(f"  Codigos duplicados: {p['Codigo_Producto_Homologado'].duplicated().sum()}")

print("\n=== CLIENTES ===")
print(f"  Filas: {len(c)}")
print(f"  Segmentos: {list(c['Segmento'].unique())}")
print(f"  IDs duplicados: {c['ID_Cliente'].duplicated().sum()}")

print("\n=== SUCURSAL ===")
print(f"  Filas: {len(s)}")
print(f"  Regionals: {list(s['Regional'].unique())}")
print(f"  Formatos: {list(s['Formato_Sucursal'].unique())}")

print("\n=== METAS ===")
print(f"  Filas: {len(m)}")
print(f"  KeyMeta duplicados: {m['KeyMeta'].duplicated().sum()}")
print(f"  Meta_Venta_Neta total: {m['Meta_Venta_Neta'].sum():,.2f}")

print("\n=== HOMOLOGACION ===")
print(f"  Filas: {len(h)}")
conectados = v['Codigo_Producto'].isin(h['Codigo_Producto_Origen']).sum()
print(f"  Ventas con homologacion: {conectados}/{len(v)} ({conectados/len(v)*100:.1f}%)")
prod_encontrados = h['Codigo_Producto_Homologado'].isin(p['Codigo_Producto_Homologado']).sum()
print(f"  Homologados en productos: {prod_encontrados}/{len(h)}")

print("\n=== RESPUESTAS DE NEGOCIO ===")
canal = v.groupby('Canal')['Venta_Neta'].sum().sort_values(ascending=False)
print(f"1. Canal > Venta Neta: {canal.index[0]} ({canal.iloc[0]:,.2f})")

vm = v.merge(p, on='Codigo_Producto_Homologado', how='left')
cat = vm.groupby('Categoria')['Margen_Bruto'].sum().sort_values(ascending=False)
print(f"2. Categoria > Margen Bruto: {cat.index[0]} ({cat.iloc[0]:,.2f})")

vs = v.merge(s, on='ID_Sucursal', how='left')
vs['KeyMeta'] = vs[ANIO].astype(str) + '|' + vs['Mes'].astype(str) + '|' + vs['Canal'] + '|' + vs['Regional']
cumpl = vs.groupby('KeyMeta').agg(VN=('Venta_Neta', 'sum')).reset_index()
cumpl = cumpl.merge(m[['KeyMeta', 'Meta_Venta_Neta']], on='KeyMeta', how='left')
cumpl['pct'] = cumpl.apply(lambda r: r['VN']/r['Meta_Venta_Neta'] if r['Meta_Venta_Neta'] > 0 else 0, axis=1)
km_reg = vs[['KeyMeta', 'Regional']].drop_duplicates()
cumpl_reg = cumpl.merge(km_reg, on='KeyMeta', how='left').groupby('Regional')['pct'].mean()
print(f"3. Regional > cumplimiento: {cumpl_reg.idxmax()} ({cumpl_reg.max()*100:.2f}%)")

ejec = v.groupby('Ejecutivo_Venta')['Venta_Neta'].sum().sort_values(ascending=False)
print(f"4. Ejecutivo > Venta Neta: {ejec.index[0]} ({ejec.iloc[0]:,.2f})")

vp = v.merge(p, on='Codigo_Producto_Homologado', how='left')
prod_margen = vp.groupby('Producto').agg(VN=('Venta_Neta', 'sum'), MB=('Margen_Bruto', 'sum'))
prod_margen['MP'] = prod_margen.apply(lambda r: r['MB']/r['VN'] if r['VN'] > 0 else 0, axis=1)
peor = prod_margen.sort_values('MP').head(1)
print(f"5. Producto menor Margen%%: {peor.index[0]} ({peor['MP'].iloc[0]*100:.2f}%)")

vc = v.merge(c, on='ID_Cliente', how='left')
cli = vc.groupby(['ID_Cliente', 'Cliente'])['Venta_Neta'].sum().sort_values(ascending=False)
print(f"6. Cliente mayor compra: {cli.index[0][1]} ({cli.iloc[0]:,.2f})")

desc = (v['Descuento_Pct'] > 0.20).sum()
print(f"7. Transacciones descuento >20%%: {desc}")

print("\n" + "=" * 60)
print("VERIFICACION COMPLETADA")
print("=" * 60)
