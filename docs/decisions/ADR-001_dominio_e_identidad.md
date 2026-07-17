# ADR-001 — Dominio de negocio, modelo de datos e identidad visual

> Estado: **Aprobado** (2026-07-17). Cierra parcialmente D6, D7, D9 y orienta D8.
> Fuentes: BD real `data_ref/POLA.db` (POS/inventario del negocio) + proyecto hermano `C:\APLICACIONES\01032026_WebApp` (identidad).

---

## 1. Qué es el negocio

**DISPOLA SAS** (razón social) opera la marca comercial **LA POLA**: **distribuidora de bebidas** que revende a negocios (tiendas, asaderos, billares) y personas. No es B2C de consumidor final puro: es **B2B/mayorista con precios escalonados**.

- Marca pública en la tienda: **LA POLA**. DISPOLA SAS queda como razón social en footer/legal.
- Catálogo real: **118 SKUs**, todos producto físico (`P-Producto`).

## 2. Modelo de catálogo (cierra D6)

### 2.1 Categorías reales (de `DIM_productos.categoria_inventarios`)

| Código | Categoría | SKUs | Rango precio_1 (COP) |
|--------|-----------|------|----------------------|
| GASPET001 | Gaseosa PET | 29 | 166 – 10.000 |
| CVZLT001 | Cervezas Lata | 28 | 3.500 – 20.500 |
| AGUA001 | Agua | 18 | 1.000 – 24.000 |
| CVZRT001 | Cervezas Botella Retornable (RT) | 13 | 1.666 – 5.076 |
| CVZNRT001 | Cervezas Botella No Retornable (NRT) | 10 | 2.200 – 23.000 |
| JUG001 | Jugos | 9 | 1.200 – 5.500 |
| BEBREH001 | Bebidas Energizantes PET | 5 | 1.500 – 3.500 |
| CIGARRO001 | Cigarrillos | 4 | 1.000 |
| BELT001 | Bebidas Energizantes Lata | 2 | 1.500 – 3.000 |

### 2.2 Atributos por producto (columnas fuente en `DIM_productos`)

| Campo tienda | Fuente `DIM_productos` | Notas |
|--------------|------------------------|-------|
| `nombre` | `nombre_producto` | Incluye presentación en el texto (ej. "600ml x 24") |
| `slug` | derivar de `nombre_producto` | Para URL SEO limpia |
| `categoria` | `categoria_inventarios` | Mapear código→etiqueta legible |
| `codigo` | `codigo_producto` | SKU interno |
| `codigo_barras` | `codigo_barras` | 117/118 lo tienen |
| `descripcion` | `descripcion_larga` | 118/118 lo tienen |
| `referencia_fabrica` | `referencia_fabrica` | |
| `precio` (público) | `precio_venta_1` | Ver §4 |
| `unidad` | `unidad_medida_factura` | `uds` (unidad) o `SXP` (six-pack) |
| `pack` | `facturacion_pack`, `unidades_facturacion_pack` | Venta por unidad y por pack |
| `envase` | derivar de categoría | RT (retornable) / NRT (no retornable) / N/A |
| `stock` | `DIM_inventarios.unidades_inventario` | Manejo real de stock, FIFO por lotes |

**Reglas del catálogo:**
- Producto físico, ~114 SKUs comercializables (excluir los **4 con `precio_venta_1 <= 0`**).
- Variantes = **presentación/pack** (unidad vs six-pack vs caja x24), no talla/color.
- Flag **retornable/no retornable** visible en cervezas (dato relevante por el envase).
- Stock real disponible → la ficha puede mostrar disponibilidad (SSR, ver R5 SEO).

## 3. Modelo de clientes (cierra D7)

- **B2B con registro** (negocio) + **invitado** para pedido puntual.
- Tipos reales (`cxc_clientes.tipo_cliente`): `persona_natural` (19), `persona_juridica` (1). Muchas "personas naturales" son negocios (Asadero Álamos, Billares, etc.).
- Campos fuente: `nombre_razon_social`, `nit_cc`, `tipo_cliente`, `email`, `telefono`, `direccion`, `dias_credito`, `limite_credito_cop`, `activo`.
- **Crédito** (`dias_credito`, `limite_credito_cop`): modelado en la BD pero **en 0 → desactivado en fase 1**.

## 4. Precios escalonados (regla de negocio)

La BD trae 3 niveles: `precio_venta_1` (mostrador), `precio_venta_2` (mayorista), `precio_venta_3` (volumen).

**Decisión:**
- **Público / invitado:** solo `precio_venta_1`.
- **Cliente registrado (logueado):** habilitar `precio_venta_2/3` según su tipo. (Fase posterior; requiere auth.)
- Nunca exponer precios mayoristas en HTML público.

## 5. Checkout fase 1 (orienta D3/D5)

Sin pasarela definida (D3 pendiente). Fase 1 = **Ambos**:
1. **Formulario de pedido** que persiste el pedido en la BD (`data/dispola.db`).
2. **Botón WhatsApp** que arma el detalle del carrito y abre el chat como respaldo.

Sin pago online en fase 1. La pasarela (Wompi/MercadoPago/ePayco/PayU) se integra cuando se cierre D3.

## 6. Origen de datos / admin (orienta D8)

Existe una BD fuente real y completa (`POLA.db`). Fase 1 = **seed/importación** desde `POLA.db` hacia `data/dispola.db` (114 SKUs válidos). CRUD admin queda para fase posterior.
- Mapear `DIM_productos` → tabla `productos`; `DIM_inventarios` → stock.
- Excluir SKUs con precio ≤ 0.
- Traducir `snake_case` de la BD legada a los nombres del nuevo contrato.

## 7. Identidad visual (cierra D9)

Marca: **LA POLA** (logos `POLA_01/02/03.png` en el hermano). Emblema/escudo cervecero, estilo **negro + dorado/ámbar**.

### Paleta (extraída del CSS del hermano + logos)

| Token | Hex | Uso |
|-------|-----|-----|
| `--pola-dorado` | `#f7db17` | Acento primario (cerveza/dorado) |
| `--pola-ambar` | `#c8860a` | Acento secundario, hovers |
| `--pola-ambar-osc` | `#a3631c` | Bordes, detalles |
| `--pola-malta` | `#824711` / `#441a09` | Marrón malta profundo |
| `--pola-negro` | `#1c1917` | Fondos, escudo |
| `--pola-crema` | `#fdfaf7` | Fondo claro / texto sobre oscuro |

Assets reutilizables del hermano: `app/static/images/POLA_0{1,2,3}.png` (logos), `001/corona.jpg` y fotos de producto, `productos_nombres.csv`.

## 8. Landing — secciones propuestas (D-landing)

Coherente con distribuidora B2B de bebidas:
1. **Hero** — "Tu distribuidora de bebidas" + CTA (ver catálogo / pedir por WhatsApp).
2. **Categorías destacadas** — Cervezas · Gaseosas · Agua · Energizantes.
3. **Productos destacados** — selección del catálogo.
4. **Quiénes somos** — DISPOLA SAS / LA POLA.
5. **Cobertura / zona de reparto**.
6. **Contacto** — WhatsApp de pedidos + formulario.

## 9. Pendientes / a confirmar

- Textos definitivos de landing e imágenes propias (hay placeholders reutilizables).
- Zona geográfica de cobertura (no está en la BD explícita).
- Mapeo código-categoría → etiquetas legibles finales (ej. "GASPET001" → "Gaseosas").
- D3 (pasarela) y D4 (dominio) siguen pendientes, no bloquean fase 1.
