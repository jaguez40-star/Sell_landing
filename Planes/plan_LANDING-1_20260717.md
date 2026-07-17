# PLAN LANDING-1 — Implementar la landing de LA POLA como componentes Astro

> **Rol del ejecutor:** Eres un agente EXECUTOR sin acceso a conversaciones previas ni al repo original.
> Lee este plan completo y ejecútalo **al pie de la letra**. CERO decisiones propias.
> Orden secuencial. Si un paso falla, **DETENTE** y reporta `❌ Paso N` con el error.
> Al final: lista de archivos tocados + "¿Hago commit?".

---

## 1. Contexto del proyecto (todo lo que necesitas saber)

**Proyecto:** DISPOLA SAS — sitio público (landing + tienda). Marca de cara al público: **LA POLA** (distribuidora de bebidas en Colombia). Todo en **español**. Moneda **COP**.

**Stack ya instalado (NO instalar nada nuevo):**
- Astro 5 (SSR, adapter node) + React 19 (islas) + TypeScript estricto.
- Sass (`sass` ya en devDependencies). Estado global de cliente: **Zustand 5** (ya instalado).
- Gestor: **pnpm** (workspace). El repo ya tiene `node_modules`, `pnpm-lock.yaml`.
- Alias TS: **`@/*` → `src/*`** (definido en `frontend/tsconfig.json`, funciona en Astro vía Vite).
- Dev server Astro: **puerto 8889**. API FastAPI: 8890 (NO se usa en este plan — datos mock).

**Directorio raíz del repo (rutas absolutas Windows):** `c:\APLICACIONES\sellweb`

**Estructura frontend actual (ya scaffoldeada):**
```
c:\APLICACIONES\sellweb\frontend\
├── astro.config.mjs
├── package.json
├── tsconfig.json          # alias @/* -> src/*
└── src\
    ├── env.d.ts
    ├── layouts\Base.astro          # layout con <head> SEO (props: titulo, descripcion, imagenOg)
    ├── pages\index.astro           # landing placeholder -> SE REEMPLAZA
    ├── styles\global.scss          # tokens placeholder -> SE REEMPLAZA
    └── features\health\components\EstadoApi.tsx   # isla de ejemplo (NO tocar)
```

**Convenciones (obligatorias):**
- **Vertical slicing:** cada feature es autocontenida en `src/features/<feature>/`. Una feature solo importa de `shared/`, `core/` o su propio árbol — **nunca** de otra feature.
- Componentes `.astro` **estáticos** (contenido SEO, renderizado en el servidor) van en `src/components/`.
- Islas React + su lógica (stores, hooks) van en `src/features/<feature>/`.
- Naming backend/JSON = `snake_case`; frontend TS = `camelCase`. (Aquí solo hay TS, todo camelCase.)
- **R5 (regla dura):** el contenido SEO-crítico (nombre, precio, categoría de producto) va en el HTML **SSR**. Las islas React solo agregan interacción, nunca contenido indexable. Por eso las tarjetas de producto se renderizan en `.astro` (servidor); solo el **carrito** es isla React.
- Islas React se hidratan con `client:idle`/`client:visible`, **nunca** `client:load` sin justificación (Core Web Vitals, §4 del proyecto).

**Marca / identidad visual (ADR-001, decisión cerrada D9):** LA POLA — paleta **navy + dorado cervecero**. Los tokens exactos están en el `global.scss` que crearás (Paso 3). No inventes colores.

**Modelo de dominio (decisión cerrada D6/D7):** distribuidora B2B de bebidas; catálogo real de 9 categorías. En esta fase se usan **datos mock** (arrays TS) que replican el catálogo real; luego se cambiarán por la API. Precio público = un solo precio (mostrador). Checkout fase 1 = pedido por **WhatsApp** + botón de formulario (placeholder).

### 1.1 Pipelines existentes — NO romper (auditado)

- **Único gate de build:** `pnpm build` (raíz) = `pnpm --filter frontend build`. `deploy.py` (paso 10) corre ese mismo comando y **valida SSR + genera sitemap**. Tu trabajo debe dejar ese build en verde.
- **NO hay** ESLint, Prettier, Husky, git-hooks, `astro check` ni `tsc` en el pipeline → `astro build` transpila con esbuild pero **no hace type-check**. Aun así, escribe el código correcto (los tipos están para el editor y para un futuro `astro check`).
- ⚠️ **NO ejecutes `pnpm test` / `pnpm test:web`.** Es `vitest run` sin `passWithNoTests`: al no haber tests en la landing, **falla con exit 1** y no aporta nada a esta tarea. El gate de esta tarea es `pnpm build` + prueba en navegador.
- El backend (FastAPI, Ruff/mypy/pytest) **no se toca** en este plan. `dev:api`, `lint:api`, `test:api` quedan intactos.
- Rutas ignoradas por git: `frontend/dist/`, `frontend/.astro/` (no versionar; se regeneran).

---

## 2. Objetivo

Convertir el diseño de la home de LA POLA (ya aprobado) en componentes Astro reales, reemplazando la landing placeholder. Resultado: `http://localhost:8889/` muestra la home completa (header con logo centrado, buscador, barra lateral flotante, menú desplegable, carrusel, categorías, descuentos, destacados, banda promo, horarios, footer) con **carrito funcional por WhatsApp** (isla React + Zustand) y **tema claro/oscuro**.

---

## 3. Prerequisitos + verificación

Ejecuta y confirma que el proyecto compila ANTES de empezar:

```powershell
cd c:\APLICACIONES\sellweb\frontend
pnpm build
```
**Esperado:** build termina en `✅` sin errores (genera `dist/`). Si falla aquí, DETENTE: el entorno no está listo (no es culpa de este plan).

---

## 4. Inventario de archivos

### CREAR (10)
| # | Ruta absoluta |
|---|---|
| C1 | `c:\APLICACIONES\sellweb\frontend\src\shared\formato.ts` |
| C2 | `c:\APLICACIONES\sellweb\frontend\src\features\catalogo\data\catalogo.ts` |
| C3 | `c:\APLICACIONES\sellweb\frontend\src\features\carrito\stores\carrito.ts` |
| C4 | `c:\APLICACIONES\sellweb\frontend\src\features\carrito\components\CarritoDrawer.tsx` |
| C5 | `c:\APLICACIONES\sellweb\frontend\src\components\landing\Header.astro` |
| C6 | `c:\APLICACIONES\sellweb\frontend\src\components\landing\Carrusel.astro` |
| C7 | `c:\APLICACIONES\sellweb\frontend\src\components\landing\Categorias.astro` |
| C8 | `c:\APLICACIONES\sellweb\frontend\src\components\landing\Descuentos.astro` |
| C9 | `c:\APLICACIONES\sellweb\frontend\src\components\landing\Destacados.astro` |
| C10 | `c:\APLICACIONES\sellweb\frontend\src\components\landing\PieDePagina.astro` |

### MODIFICAR (2)
| # | Ruta absoluta | Acción |
|---|---|---|
| M1 | `c:\APLICACIONES\sellweb\frontend\src\styles\global.scss` | **Reemplazar contenido completo** |
| M2 | `c:\APLICACIONES\sellweb\frontend\src\pages\index.astro` | **Reemplazar contenido completo** |

### NO TOCAR
`astro.config.mjs`, `package.json`, `tsconfig.json`, `pnpm-lock.yaml`, `Base.astro`, `EstadoApi.tsx`.

---

## 5. Especificación por archivo (código completo, pegar tal cual)

### C1 — `src\shared\formato.ts`
```ts
// Utilidades de formato transversales (shared).
export const cop = (n: number): string => "$" + n.toLocaleString("es-CO");
```

---

### C2 — `src\features\catalogo\data\catalogo.ts`
```ts
// Datos MOCK del catálogo (fase de diseño). Replican el catálogo real de POLA.db.
// TODO[LANDING]: reemplazar por la API FastAPI (openapi-fetch) cuando exista el endpoint.

export type Etiqueta = "top" | "rt" | "nrt" | null;

export interface Categoria {
  slug: string;
  nombre: string;
  emoji: string;
  skus: number;
  color: string; // color del círculo (fijo, no depende del tema)
}

export interface Producto {
  id: string;
  emoji: string;
  categoria: string;
  nombre: string;
  presentacion: string;
  precio: number; // precio mostrador (COP)
  etiqueta: Etiqueta;
}

export interface Promo {
  productoId: string;
  descuento: number; // % OFF
}

export const CATEGORIAS: Categoria[] = [
  { slug: "gaseosas", nombre: "Gaseosas", emoji: "🥤", skus: 29, color: "#F3D9C0" },
  { slug: "cervezas-lata", nombre: "Cervezas Lata", emoji: "🍺", skus: 28, color: "#F6E3A6" },
  { slug: "agua", nombre: "Agua", emoji: "💧", skus: 18, color: "#CFE6F2" },
  { slug: "cerveza-retornable", nombre: "Cerveza Retornable", emoji: "🍻", skus: 13, color: "#E7CFA0" },
  { slug: "cerveza-no-retornable", nombre: "Cerveza No Retornable", emoji: "🍾", skus: 10, color: "#DBCDB2" },
  { slug: "jugos", nombre: "Jugos", emoji: "🧃", skus: 9, color: "#F5C6C6" },
  { slug: "energizantes-pet", nombre: "Energizantes PET", emoji: "⚡", skus: 5, color: "#D3E8C4" },
  { slug: "cigarrillos", nombre: "Cigarrillos", emoji: "🚬", skus: 4, color: "#E1DAD0" },
  { slug: "energizantes-lata", nombre: "Energizantes Lata", emoji: "🔋", skus: 2, color: "#C9E1DD" },
];

export const PRODUCTOS: Producto[] = [
  { id: "p01", emoji: "🍺", categoria: "Cervezas Lata", nombre: "Club Colombia Dorada Lata 473cc", presentacion: "Six pack · 6 uds", precio: 20500, etiqueta: "top" },
  { id: "p02", emoji: "🍺", categoria: "Cervezas NR", nombre: "Corona No Retornable 330cc", presentacion: "Six pack · 6 uds", precio: 23000, etiqueta: "nrt" },
  { id: "p03", emoji: "🍺", categoria: "Cervezas Lata", nombre: "Águila Original Lata 330cc", presentacion: "Six pack · 6 uds", precio: 18000, etiqueta: "top" },
  { id: "p04", emoji: "🍺", categoria: "Cervezas Lata", nombre: "Poker Lata 330cc", presentacion: "Six pack · 6 uds", precio: 18000, etiqueta: null },
  { id: "p05", emoji: "🍺", categoria: "Cervezas NR", nombre: "Stella Artois No Retornable 300cc", presentacion: "Six pack · 6 uds", precio: 21000, etiqueta: "nrt" },
  { id: "p06", emoji: "🍺", categoria: "Cervezas RT", nombre: "Águila Original Retornable 750cc", presentacion: "Unidad · canasta x16", precio: 4250, etiqueta: "rt" },
  { id: "p07", emoji: "🥤", categoria: "Gaseosas", nombre: "Coca-Cola Pet 3 L", presentacion: "Paca · 6 uds", precio: 10000, etiqueta: null },
  { id: "p08", emoji: "🥤", categoria: "Gaseosas", nombre: "Bebida Pony Malta 1.5 L", presentacion: "Paca · 6 uds", precio: 6000, etiqueta: null },
  { id: "p09", emoji: "💧", categoria: "Agua", nombre: "Agua Cristal 1 L", presentacion: "Paca · 12 uds", precio: 24000, etiqueta: null },
  { id: "p10", emoji: "💧", categoria: "Agua", nombre: "Agua Manantial Gas 600ml", presentacion: "Unidad", precio: 3000, etiqueta: null },
  { id: "p11", emoji: "🧃", categoria: "Jugos", nombre: "Té Mr Tea 1.5 L", presentacion: "Paca · 6 uds", precio: 5500, etiqueta: null },
  { id: "p12", emoji: "🧃", categoria: "Jugos", nombre: "Jugo Hit Pet 500ml", presentacion: "Unidad", precio: 2500, etiqueta: null },
  { id: "p13", emoji: "⚡", categoria: "Energizantes", nombre: "Gatorade 500ml", presentacion: "Caja · 12 uds", precio: 3500, etiqueta: null },
  { id: "p14", emoji: "⚡", categoria: "Energizantes", nombre: "Vive100 380ml", presentacion: "Unidad", precio: 2500, etiqueta: null },
  { id: "p15", emoji: "🍺", categoria: "Cervezas NR", nombre: "Coronita No Retornable 210cc", presentacion: "Six pack · 6 uds", precio: 18000, etiqueta: "nrt" },
  { id: "p16", emoji: "🥤", categoria: "Gaseosas", nombre: "Quatro Pet 3 L", presentacion: "Paca · 6 uds", precio: 7000, etiqueta: null },
];

export const PROMOS: Promo[] = [
  { productoId: "p01", descuento: 20 },
  { productoId: "p02", descuento: 15 },
  { productoId: "p05", descuento: 15 },
  { productoId: "p13", descuento: 20 },
  { productoId: "p09", descuento: 18 },
  { productoId: "p07", descuento: 12 },
  { productoId: "p11", descuento: 15 },
  { productoId: "p03", descuento: 10 },
];

export const productoPorId = (id: string): Producto | undefined =>
  PRODUCTOS.find((p) => p.id === id);

// Precio original tachado a partir de la oferta y el % de descuento.
export const precioOriginal = (oferta: number, descuento: number): number =>
  Math.round(oferta / (1 - descuento / 100) / 100) * 100;
```

---

### C3 — `src\features\carrito\stores\carrito.ts`
```ts
// Estado global del carrito (Zustand). Usable desde React (hook) y desde scripts vanilla
// vía useCarrito.getState(). Keyed por id de producto -> cantidad.
//
// IMPORTANTE (R2 + Zustand v5): el store expone SOLO estado crudo (`items`, `abierto`) y
// acciones (referencias estables). Los datos derivados (líneas, total, URL) NO se calculan
// dentro de selectores del hook, porque devolver una referencia nueva en cada render dispara
// "getSnapshot should be cached" -> re-render infinito. Se calculan con funciones puras
// (abajo) y se memoizan en el componente con deps = [items].
import { create } from "zustand";
import { PRODUCTOS, productoPorId, type Producto } from "@/features/catalogo/data/catalogo";

const TEL_WHATSAPP = "573000000000"; // TODO[LANDING]: número real de pedidos.

export type ItemsCarrito = Record<string, number>;
export interface LineaCarrito {
  producto: Producto;
  cantidad: number;
}

interface CarritoState {
  items: ItemsCarrito;
  abierto: boolean;
  agregar: (id: string) => void;
  incrementar: (id: string) => void;
  decrementar: (id: string) => void;
  abrir: () => void;
  cerrar: () => void;
}

export const useCarrito = create<CarritoState>((set) => ({
  items: {},
  abierto: false,
  agregar: (id) => set((s) => ({ items: { ...s.items, [id]: (s.items[id] ?? 0) + 1 } })),
  incrementar: (id) => set((s) => ({ items: { ...s.items, [id]: (s.items[id] ?? 0) + 1 } })),
  decrementar: (id) =>
    set((s) => {
      const n = (s.items[id] ?? 0) - 1;
      const items = { ...s.items };
      if (n <= 0) delete items[id];
      else items[id] = n;
      return { items };
    }),
  abrir: () => set({ abierto: true }),
  cerrar: () => set({ abierto: false }),
}));

// --- Derivados PUROS (fuera de los selectores del hook). Reciben `items` crudo. ---
export const unidadesDe = (items: ItemsCarrito): number =>
  Object.values(items).reduce((a, b) => a + b, 0);

export const lineasDe = (items: ItemsCarrito): LineaCarrito[] =>
  Object.entries(items)
    .map(([id, cantidad]) => {
      const producto = productoPorId(id);
      return producto ? { producto, cantidad } : null;
    })
    .filter((x): x is LineaCarrito => x !== null);

export const totalCopDe = (items: ItemsCarrito): number =>
  Object.entries(items).reduce((a, [id, c]) => a + (productoPorId(id)?.precio ?? 0) * c, 0);

export const whatsappUrlDe = (items: ItemsCarrito): string => {
  const cop = (n: number) => "$" + n.toLocaleString("es-CO");
  const detalle = lineasDe(items)
    .map((l) => `- ${l.cantidad}x ${l.producto.nombre} - ${cop(l.producto.precio * l.cantidad)}`)
    .join("\n");
  const msg = `Hola LA POLA, quiero este pedido:\n${detalle}\n\nTotal: ${cop(totalCopDe(items))}`;
  return `https://wa.me/${TEL_WHATSAPP}?text=${encodeURIComponent(msg)}`;
};

export { PRODUCTOS };
```

---

### C4 — `src\features\carrito\components\CarritoDrawer.tsx`
```tsx
// Isla React: cajón lateral del carrito + fondo (scrim). Lee el store Zustand.
// Los botones "Agregar" de las tarjetas (SSR) y los botones del header/rail se conectan
// al mismo store desde un script vanilla en index.astro (useCarrito.getState()).
import { useMemo } from "react";
import {
  useCarrito,
  lineasDe,
  totalCopDe,
  whatsappUrlDe,
} from "@/features/carrito/stores/carrito";
import { cop } from "@/shared/formato";

export default function CarritoDrawer() {
  // Selectores ESTABLES: primitivos + referencias de acciones. NUNCA funciones que crean
  // objetos/arrays nuevos (eso provoca re-render infinito en Zustand v5).
  const items = useCarrito((s) => s.items);
  const abierto = useCarrito((s) => s.abierto);
  const cerrar = useCarrito((s) => s.cerrar);
  const incrementar = useCarrito((s) => s.incrementar);
  const decrementar = useCarrito((s) => s.decrementar);

  // Datos derivados (R2): deps = [items] (dato crudo), jamás estado de UI.
  const lineas = useMemo(() => lineasDe(items), [items]);
  const totalCop = useMemo(() => totalCopDe(items), [items]);
  const whatsappUrl = useMemo(() => whatsappUrlDe(items), [items]);

  return (
    <>
      <div className={"scrim" + (abierto ? " on" : "")} onClick={cerrar} />
      <aside className={"drawer" + (abierto ? " on" : "")} aria-label="Mi pedido">
        <div className="drawer-head">
          <b>Mi pedido</b>
          <button onClick={cerrar} aria-label="Cerrar">×</button>
        </div>
        <div className="drawer-body">
          {lineas.length === 0 ? (
            <div className="drawer-empty">Tu pedido está vacío.<br />Agrega productos del catálogo. 🍺</div>
          ) : (
            lineas.map((l) => (
              <div className="line" key={l.producto.id}>
                <span className="li-emoji">{l.producto.emoji}</span>
                <div className="li-info">
                  <b>{l.producto.nombre}</b>
                  <span>{cop(l.producto.precio)}</span>
                </div>
                <div className="qty">
                  <button onClick={() => decrementar(l.producto.id)}>−</button>
                  <span>{l.cantidad}</span>
                  <button onClick={() => incrementar(l.producto.id)}>+</button>
                </div>
              </div>
            ))
          )}
        </div>
        {lineas.length > 0 && (
          <div className="drawer-foot">
            <div className="tot"><span>Total</span><span>{cop(totalCop)}</span></div>
            <small>Precio mostrador. Regístrate como negocio para ver precios mayorista.</small>
            <a className="btn btn-wa" href={whatsappUrl} target="_blank" rel="noopener">
              Enviar pedido por WhatsApp
            </a>
            <button className="btn btn-form" type="button" onClick={() => alert("Formulario de pedido — próximamente")}>
              Enviar por formulario
            </button>
          </div>
        )}
      </aside>
    </>
  );
}
```

---

### M1 — `src\styles\global.scss` (REEMPLAZAR TODO el archivo)

> Pega **exactamente** este bloque. Son los tokens de marca LA POLA + todos los estilos de las secciones. Es CSS válido (Sass lo compila sin cambios). No modifiques valores.

```scss
:root {
  --bg: #F3F1EC;
  --surface: #FFFFFF;
  --surface-2: #F4EBD9;
  --text: #1C2433;
  --text-soft: #5B6577;
  --text-mut: #8A93A3;
  --border: #E5E0D5;
  --gold: #C79A2E;
  --gold-deep: #A8801C;
  --gold-bright: #F5C518;
  --amber: #C8860A;
  --malta: #6B3F13;
  --negro: #141A26;
  --foam: #FFF9EC;
  --header-bg: #FBFAF7;
  --header-text: #1C2433;
  --r-sm: 8px; --r-md: 12px; --r-lg: 20px; --r-pill: 999px;
  --shadow-1: 0 1px 2px rgba(20,26,38,.05), 0 4px 14px rgba(20,26,38,.06);
  --shadow-2: 0 10px 34px rgba(20,26,38,.16);
  --shadow-float: 0 6px 22px rgba(20,26,38,.14);
  --maxw: 1240px;
  --display: "Bahnschrift", "Arial Narrow", "Franklin Gothic Medium", "Segoe UI", system-ui, sans-serif;
  --serif: "Georgia", "Times New Roman", serif;
  --body: "Segoe UI", system-ui, -apple-system, Roboto, Helvetica, Arial, sans-serif;
}
@media (prefers-color-scheme: dark) {
  :root {
    --bg: #14100B; --surface: #1E1811; --surface-2: #262017;
    --text: #F7EFDF; --text-soft: #C3B291; --text-mut: #9A8967; --border: #33291A;
    --gold: #E4B948; --gold-deep: #C79A2E; --gold-bright: #FFD630; --amber: #E8A80C; --malta: #C89B5A;
    --foam: #201A12; --negro: #0F0C08; --header-bg: #1A150E; --header-text: #F7EFDF;
    --shadow-1: 0 1px 2px rgba(0,0,0,.4); --shadow-2: 0 12px 34px rgba(0,0,0,.55);
    --shadow-float: 0 6px 22px rgba(0,0,0,.5);
  }
}
:root[data-theme="light"] {
  --bg:#F3F1EC; --surface:#FFFFFF; --surface-2:#F4EBD9; --text:#1C2433; --text-soft:#5B6577;
  --text-mut:#8A93A3; --border:#E5E0D5; --gold:#C79A2E; --gold-deep:#A8801C; --gold-bright:#F5C518;
  --amber:#C8860A; --malta:#6B3F13; --foam:#FFF9EC; --negro:#141A26; --header-bg:#FBFAF7; --header-text:#1C2433;
  --shadow-1:0 1px 2px rgba(20,26,38,.05),0 4px 14px rgba(20,26,38,.06); --shadow-2:0 10px 34px rgba(20,26,38,.16);
  --shadow-float:0 6px 22px rgba(20,26,38,.14);
}
:root[data-theme="dark"] {
  --bg:#14100B; --surface:#1E1811; --surface-2:#262017; --text:#F7EFDF; --text-soft:#C3B291;
  --text-mut:#9A8967; --border:#33291A; --gold:#E4B948; --gold-deep:#C79A2E; --gold-bright:#FFD630;
  --amber:#E8A80C; --malta:#C89B5A; --foam:#201A12; --negro:#0F0C08; --header-bg:#1A150E; --header-text:#F7EFDF;
  --shadow-1:0 1px 2px rgba(0,0,0,.4); --shadow-2:0 12px 34px rgba(0,0,0,.55); --shadow-float:0 6px 22px rgba(0,0,0,.5);
}

* { box-sizing: border-box; }
body { margin:0; background:var(--bg); color:var(--text); font-family:var(--body); font-size:16px; line-height:1.55; -webkit-font-smoothing:antialiased; }
h1,h2,h3,h4 { margin:0; text-wrap:balance; }
a { color:inherit; text-decoration:none; }
img { max-width:100%; display:block; }
button { font-family:inherit; cursor:pointer; }
.wrap { max-width:var(--maxw); margin:0 auto; padding:0 20px; }
.eyebrow { font-family:var(--display); text-transform:uppercase; letter-spacing:.16em; font-size:.74rem; font-weight:700; color:var(--amber); }

.agebar { background:var(--negro); color:#E7C868; font-size:.74rem; text-align:center; padding:7px 20px; letter-spacing:.02em; }
.agebar strong { color:var(--gold-bright); }

header.site { position:sticky; top:0; z-index:40; background:var(--header-bg); color:var(--header-text); border-bottom:1px solid var(--border); box-shadow:var(--shadow-1); }
.hdr { display:grid; grid-template-columns:1fr auto 1fr; align-items:center; gap:14px; padding:14px 24px; max-width:var(--maxw); margin:0 auto; }
.hdr-left { display:flex; align-items:center; gap:10px; }
.hchip { display:inline-flex; align-items:center; gap:8px; padding:9px 15px; border-radius:var(--r-pill); border:1px solid var(--border); background:var(--surface); color:var(--text); font-size:.9rem; font-weight:600; }
.hchip:hover { border-color:var(--gold); color:var(--gold-deep); }
.hchip svg { width:17px; height:17px; }
.hchip .caret { width:12px; height:12px; opacity:.6; }
.hchip b { color:var(--gold-deep); }
.brand { display:flex; flex-direction:column; align-items:center; gap:1px; justify-self:center; text-align:center; }
.brand .crest { display:flex; align-items:center; gap:6px; color:var(--gold-deep); font-size:.6rem; letter-spacing:.24em; text-transform:uppercase; font-weight:700; }
.brand .crest .line { width:26px; height:1px; background:linear-gradient(90deg,transparent,var(--gold)); }
.brand .crest .line.r { background:linear-gradient(90deg,var(--gold),transparent); }
.brand .word { font-family:var(--serif); font-weight:700; font-size:2rem; line-height:1; letter-spacing:.01em; background:linear-gradient(180deg,#E7C55B,#B8891E 60%,#8A6412); -webkit-background-clip:text; background-clip:text; -webkit-text-fill-color:transparent; }
.brand .word .dot { -webkit-text-fill-color:var(--text); font-size:1rem; }
.brand .tagline { font-size:.58rem; letter-spacing:.34em; text-transform:uppercase; color:var(--text-mut); margin-top:2px; }
.hdr-right { display:flex; align-items:center; justify-content:flex-end; gap:10px; }
.cart-chip { position:relative; }
.cart-chip .cart-count { position:absolute; top:-7px; right:-7px; min-width:20px; height:20px; padding:0 5px; background:var(--gold-bright); color:#3a2a04; font-size:.68rem; font-weight:800; border-radius:var(--r-pill); display:grid; place-items:center; font-variant-numeric:tabular-nums; border:2px solid var(--header-bg); }
.theme-toggle { background:var(--surface); border:1px solid var(--border); color:var(--text-soft); border-radius:var(--r-pill); width:40px; height:40px; display:grid; place-items:center; }
.theme-toggle:hover { border-color:var(--gold); color:var(--gold-deep); }
.theme-toggle svg { width:18px; height:18px; }

.searchrow { background:var(--bg); padding:20px 20px 6px; }
.searchrow .box { max-width:820px; margin:0 auto; position:relative; }
.searchrow input { width:100%; border:1px solid var(--border); background:var(--surface); color:var(--text); border-radius:var(--r-pill); padding:16px 22px 16px 54px; font-size:1rem; outline:none; box-shadow:var(--shadow-1); }
.searchrow input::placeholder { color:var(--text-mut); }
.searchrow input:focus { border-color:var(--gold); box-shadow:0 0 0 4px rgba(199,154,46,.18); }
.searchrow .mag { position:absolute; left:20px; top:50%; transform:translateY(-50%); width:22px; height:22px; color:var(--gold-deep); }

.railbar { position:fixed; left:14px; top:50%; transform:translateY(-50%); z-index:35; display:flex; flex-direction:column; gap:6px; padding:8px 6px; background:var(--surface); border:1px solid var(--border); border-radius:var(--r-pill); box-shadow:var(--shadow-float); }
.railbar button { width:44px; height:44px; border-radius:50%; border:none; background:transparent; color:var(--text-soft); display:grid; place-items:center; position:relative; }
.railbar button svg { width:20px; height:20px; }
.railbar button:hover { background:var(--surface-2); color:var(--gold-deep); }
.railbar button.active { background:linear-gradient(180deg,#E4B948,#C08E1C); color:#3a2a04; box-shadow:0 3px 10px rgba(199,154,46,.4); }
.railbar .rc { position:absolute; top:2px; right:2px; min-width:16px; height:16px; padding:0 4px; background:var(--gold-bright); color:#3a2a04; font-size:.6rem; font-weight:800; border-radius:var(--r-pill); display:grid; place-items:center; }

.carousel-sec { padding:8px 0 4px; }
.carousel { position:relative; border-radius:var(--r-lg); overflow:hidden; box-shadow:var(--shadow-1); }
.track { display:flex; transition:transform .5s cubic-bezier(.4,0,.2,1); }
.slide { min-width:100%; position:relative; aspect-ratio:1240/430; display:flex; align-items:center; padding:0 clamp(28px,6vw,80px); color:#FBF3DF; overflow:hidden; }
@media (max-width:700px){ .slide { aspect-ratio:16/12; } }
.slide .art { position:absolute; right:-2%; bottom:-6%; font-size:clamp(6rem,20vw,15rem); line-height:1; opacity:.9; filter:drop-shadow(0 12px 24px rgba(0,0,0,.4)); transform:rotate(-6deg); }
.slide .content { position:relative; z-index:2; max-width:60%; }
.slide .kicker { font-family:var(--display); text-transform:uppercase; letter-spacing:.2em; font-size:.8rem; color:var(--gold-bright); font-weight:700; }
.slide h2 { font-family:var(--display); text-transform:uppercase; font-weight:700; font-size:clamp(2rem,6vw,4rem); line-height:.94; margin:8px 0 4px; }
.slide h2 em { font-style:normal; color:var(--gold-bright); }
.slide p { font-size:clamp(.9rem,1.6vw,1.1rem); color:#E6D6B4; max-width:36ch; margin:6px 0 0; }
.slide .sbtn { display:inline-flex; align-items:center; gap:8px; margin-top:18px; background:linear-gradient(180deg,#F7DB17,#E29B08); color:#241604; border:none; border-radius:var(--r-pill); padding:12px 22px; font-weight:800; font-size:.92rem; }
.slide .sbtn:hover { filter:brightness(1.06); }
.slide .fine { position:absolute; left:0; right:0; bottom:10px; text-align:center; font-size:.66rem; color:rgba(255,255,255,.6); padding:0 20px; z-index:2; }
.s0 { background:radial-gradient(70% 120% at 78% 20%,rgba(245,197,24,.28),transparent 60%),linear-gradient(120deg,#0d1420,#20304a 65%,#123); }
.s1 { background:radial-gradient(60% 120% at 20% 20%,rgba(245,197,24,.25),transparent 60%),linear-gradient(120deg,#2a1707,#5a3410 70%,#7a4a12); }
.s2 { background:radial-gradient(70% 120% at 80% 30%,rgba(80,180,110,.3),transparent 60%),linear-gradient(120deg,#0f2417,#134a2b 70%,#0c3d22); }
.cbtn { position:absolute; top:50%; transform:translateY(-50%); width:44px; height:44px; border-radius:50%; border:none; background:rgba(255,255,255,.16); color:#fff; display:grid; place-items:center; backdrop-filter:blur(4px); z-index:3; }
.cbtn:hover { background:rgba(255,255,255,.28); }
.cbtn svg { width:22px; height:22px; }
.cbtn.prev { left:14px; } .cbtn.next { right:14px; }
.dots { display:flex; gap:8px; justify-content:center; padding:14px 0 2px; }
.dots button { width:9px; height:9px; border-radius:50%; border:none; background:var(--border); padding:0; }
.dots button.on { background:var(--gold); width:26px; border-radius:var(--r-pill); }

section.block { padding:48px 0; }
.sec-head { display:flex; align-items:flex-end; justify-content:space-between; gap:16px; margin-bottom:24px; }
.sec-head h2 { font-family:var(--display); text-transform:uppercase; font-weight:700; font-size:clamp(1.5rem,3.2vw,2.1rem); letter-spacing:.02em; margin-top:4px; }
.sec-head a.more { font-size:.86rem; font-weight:700; color:var(--amber); white-space:nowrap; }
.sec-head a.more:hover { color:var(--gold-deep); }

.catcard { background:var(--surface); border:1px solid var(--border); border-radius:22px; box-shadow:var(--shadow-1); padding:26px 28px 18px; }
.cat-title { font-family:var(--serif); font-weight:700; font-size:clamp(1.35rem,3vw,1.85rem); color:var(--text); margin:4px 0 4px; }
.cat-rail { display:flex; gap:20px; overflow-x:auto; padding:22px 2px 18px; scroll-snap-type:x proximity; scrollbar-width:thin; scrollbar-color:var(--text-mut) var(--surface-2); }
.cat-rail::-webkit-scrollbar { height:8px; }
.cat-rail::-webkit-scrollbar-track { background:var(--surface-2); border-radius:var(--r-pill); }
.cat-rail::-webkit-scrollbar-thumb { background:var(--text-mut); border-radius:var(--r-pill); }
.cat-item { flex:0 0 auto; width:104px; text-align:center; scroll-snap-align:start; }
.cat-item .circle { width:96px; height:96px; border-radius:50%; display:grid; place-items:center; margin:0 auto 12px; font-size:2.7rem; box-shadow:inset 0 -6px 14px rgba(0,0,0,.08); transition:transform .14s, box-shadow .14s; filter:drop-shadow(0 6px 10px rgba(20,26,38,.12)); }
.cat-item:hover .circle { transform:translateY(-4px) scale(1.05); box-shadow:inset 0 -6px 14px rgba(0,0,0,.08), 0 8px 18px rgba(20,26,38,.18); }
.cat-item b { display:block; font-size:.9rem; font-weight:600; color:var(--text); line-height:1.2; }
.cat-item .cnt { font-size:.72rem; color:var(--text-mut); }

.prod-grid { display:grid; grid-template-columns:repeat(auto-fill,minmax(220px,1fr)); gap:18px; }
.card { background:var(--surface); border:1px solid var(--border); border-radius:var(--r-md); overflow:hidden; display:flex; flex-direction:column; transition:transform .12s,box-shadow .12s,border-color .12s; }
.card:hover { transform:translateY(-4px); box-shadow:var(--shadow-2); border-color:var(--gold); }
.card .thumb { position:relative; aspect-ratio:1/1; background:radial-gradient(90% 90% at 50% 22%,var(--foam),var(--surface-2)); display:grid; place-items:center; }
.card .thumb .bottle { font-size:3.4rem; filter:drop-shadow(0 8px 12px rgba(200,134,10,.28)); }
.tag { position:absolute; top:10px; left:10px; font-size:.66rem; font-weight:800; text-transform:uppercase; letter-spacing:.06em; padding:4px 9px; border-radius:var(--r-pill); color:#3a2a04; background:var(--gold-bright); }
.tag.rt { background:#6FA9DA; color:#08213a; } .tag.nrt { background:#C7B299; color:#2c2114; }
.card .body { padding:13px 14px 15px; display:flex; flex-direction:column; gap:4px; flex:1; }
.card .cat-lbl { font-size:.68rem; text-transform:uppercase; letter-spacing:.09em; color:var(--amber); font-weight:700; }
.card h3 { font-size:.95rem; font-weight:600; line-height:1.28; min-height:2.5em; }
.card .pres { font-size:.77rem; color:var(--text-mut); }
.card .foot { margin-top:auto; display:flex; align-items:center; justify-content:space-between; gap:8px; padding-top:10px; }
.price { font-family:var(--display); font-weight:700; font-size:1.28rem; letter-spacing:.01em; font-variant-numeric:tabular-nums; }
.price small { font-size:.66rem; color:var(--text-mut); font-family:var(--body); font-weight:500; display:block; margin-top:-2px; }
.add { display:inline-flex; align-items:center; gap:6px; background:var(--negro); color:var(--gold-bright); border:none; border-radius:var(--r-pill); padding:9px 14px; font-weight:700; font-size:.82rem; }
.add:hover { filter:brightness(1.15); transform:scale(1.04); }
.add svg { width:15px; height:15px; }

.promos { background:var(--surface-2); border-radius:22px; padding:32px; display:grid; grid-template-columns:250px 1fr; gap:26px; align-items:center; }
.promos-left { padding-left:6px; }
.promos-title { font-family:var(--serif); font-weight:700; font-size:clamp(1.4rem,2.6vw,1.9rem); line-height:1.15; color:var(--text); margin:6px 0 18px; max-width:12ch; }
.promos-btn { display:inline-flex; align-items:center; gap:10px; background:var(--negro); color:var(--gold-bright); border-radius:var(--r-pill); padding:13px 24px; font-weight:800; font-size:.82rem; letter-spacing:.06em; text-transform:uppercase; }
.promos-btn:hover { filter:brightness(1.15); }
.promos-btn svg { width:16px; height:16px; }
.promos-right { min-width:0; }
.promo-rail { display:flex; gap:16px; overflow-x:auto; padding:6px 2px 14px; scroll-snap-type:x proximity; scrollbar-width:thin; scrollbar-color:var(--gold-deep) rgba(0,0,0,.08); }
.promo-rail::-webkit-scrollbar { height:6px; }
.promo-rail::-webkit-scrollbar-track { background:rgba(0,0,0,.08); border-radius:var(--r-pill); }
.promo-rail::-webkit-scrollbar-thumb { background:var(--gold-deep); border-radius:var(--r-pill); }
.promo-card { flex:0 0 auto; width:186px; background:var(--surface); border-radius:16px; padding:16px 16px 14px; position:relative; scroll-snap-align:start; box-shadow:var(--shadow-1); transition:transform .12s, box-shadow .12s; }
.promo-card:hover { transform:translateY(-3px); box-shadow:var(--shadow-2); }
.off-badge { position:absolute; top:-8px; right:-6px; width:44px; height:44px; border-radius:50%; background:#E8324B; color:#fff; display:grid; place-items:center; text-align:center; font-size:.62rem; font-weight:800; line-height:1; box-shadow:0 4px 10px rgba(232,50,75,.4); }
.promo-card .pemoji { font-size:3.1rem; text-align:center; height:96px; display:grid; place-items:center; filter:drop-shadow(0 8px 12px rgba(200,134,10,.25)); }
.promo-card h4 { font-size:.86rem; font-weight:600; color:var(--text); line-height:1.28; min-height:3.3em; margin-bottom:10px; }
.promo-foot { display:flex; align-items:flex-end; justify-content:space-between; gap:8px; }
.promo-price .now { font-family:var(--display); font-weight:700; font-size:1.24rem; color:var(--gold-deep); font-variant-numeric:tabular-nums; letter-spacing:.01em; }
.promo-price .old { display:block; font-size:.78rem; color:var(--text-mut); text-decoration:line-through; font-variant-numeric:tabular-nums; }
.padd { width:38px; height:38px; border-radius:50%; border:none; background:var(--negro); color:var(--gold-bright); display:grid; place-items:center; flex:0 0 auto; }
.padd:hover { filter:brightness(1.2); transform:scale(1.08); }
.padd svg { width:17px; height:17px; }
.promos-explore { display:block; text-align:center; margin-top:6px; font-size:.78rem; font-weight:800; letter-spacing:.08em; text-transform:uppercase; color:var(--gold-deep); }
.promos-explore:hover { color:var(--amber); }
@media (max-width:760px){ .promos { grid-template-columns:1fr; padding:24px; } .promos-title { max-width:none; } }

.promo { background:linear-gradient(115deg,#141a26,#2a3a56 70%,#1c2a44); color:#F7EFDF; border-radius:var(--r-lg); overflow:hidden; position:relative; }
.promo::after { content:""; position:absolute; inset:0; background:radial-gradient(50% 120% at 90% 10%,rgba(245,197,24,.2),transparent 60%); }
.promo-grid { position:relative; display:grid; grid-template-columns:repeat(3,1fr); gap:14px; padding:30px; }
.promo-item { display:flex; gap:13px; align-items:flex-start; }
.promo-item .pic { width:44px; height:44px; border-radius:12px; background:rgba(245,197,24,.16); display:grid; place-items:center; flex:0 0 auto; }
.promo-item .pic svg { width:22px; height:22px; color:var(--gold-bright); }
.promo-item b { display:block; font-size:1rem; }
.promo-item p { margin:3px 0 0; font-size:.84rem; color:#C5D0E0; }

.horarios { display:grid; grid-template-columns:1fr 1fr; gap:30px; align-items:center; max-width:840px; }
.hor-left { text-align:center; }
.hor-art { font-size:5rem; line-height:1; filter:drop-shadow(0 12px 18px rgba(20,26,38,.2)); }
.hor-title { font-family:var(--serif); font-weight:700; font-size:clamp(1.8rem,4vw,2.6rem); color:var(--text); line-height:1.05; margin-top:8px; }
.hor-card { background:var(--surface); border:1px solid var(--border); border-radius:18px; box-shadow:var(--shadow-1); padding:24px 26px; }
.hor-card .eyebrow { display:block; margin-bottom:8px; }
.hor-row { display:flex; align-items:center; gap:16px; padding:16px 2px; }
.hor-row + .hor-row { border-top:1px solid var(--border); }
.hor-row .hicon { width:34px; height:34px; flex:0 0 auto; display:grid; place-items:center; color:var(--text); }
.hor-row .hicon svg { width:30px; height:30px; }
.hor-row p { margin:0; color:var(--text-soft); font-size:.94rem; line-height:1.35; }

.trustband { padding:36px 20px 10px; }
.trust-inner { max-width:var(--maxw); margin:0 auto; display:flex; gap:64px; justify-content:center; flex-wrap:wrap; }
.trust-group { text-align:center; }
.trust-group h5 { font-family:var(--display); text-transform:uppercase; letter-spacing:.12em; font-size:.78rem; color:var(--text-soft); margin-bottom:14px; font-weight:700; }
.trust-logos { display:flex; gap:26px; align-items:center; justify-content:center; flex-wrap:wrap; }
.trust-chip { display:inline-flex; align-items:center; gap:8px; font-weight:800; font-size:.84rem; color:var(--text); opacity:.72; letter-spacing:.01em; }
.trust-chip .tdot { width:24px; height:24px; border-radius:7px; display:grid; place-items:center; color:#fff; font-size:.7rem; font-weight:800; }

footer.site { background:var(--negro); color:#C3D0DF; margin-top:14px; border-top:none; }
.foot-top { max-width:var(--maxw); margin:0 auto; padding:46px 20px 6px; text-align:center; }
.foot-logo { font-family:var(--serif); font-weight:700; font-size:1.8rem; color:#FBFAF7; letter-spacing:.01em; }
.foot-logo .dot { color:var(--gold-bright); }
.foot-logo small { display:block; font-size:.58rem; letter-spacing:.34em; text-transform:uppercase; color:#8296AC; margin-top:4px; font-family:var(--body); }
.foot-cards { display:grid; grid-template-columns:1fr 1fr 1.7fr; gap:18px; max-width:var(--maxw); margin:30px auto 0; padding:0 20px; }
.fcard { background:rgba(255,255,255,.045); border:1px solid rgba(255,255,255,.07); border-radius:16px; padding:22px 24px; }
.fcard .fhead { display:flex; align-items:center; gap:11px; color:#fff; font-weight:700; margin-bottom:16px; font-size:1rem; }
.fcard .fhead .fi { width:36px; height:36px; border-radius:50%; background:rgba(245,197,24,.16); display:grid; place-items:center; flex:0 0 auto; }
.fcard .fhead .fi svg { width:19px; height:19px; color:var(--gold-bright); }
.fcard a.flink { display:block; color:#AEC0D3; padding:6px 0; font-size:.9rem; }
.fcard a.flink:hover { color:var(--gold-bright); }
.contact-grid { display:grid; grid-template-columns:1fr 1fr; gap:6px 26px; }
.cg { padding:6px 0 12px; border-bottom:1px solid rgba(255,255,255,.09); }
.cg h6 { color:#fff; font-size:.82rem; font-weight:700; margin-bottom:7px; }
.cg p, .cg a { color:#AEC0D3; font-size:.88rem; margin:2px 0; display:block; }
.cg a:hover { color:var(--gold-bright); }
.foot-social { display:flex; gap:14px; justify-content:center; margin:32px 0 6px; }
.foot-social a { width:42px; height:42px; border-radius:50%; border:1px solid rgba(255,255,255,.2); display:grid; place-items:center; color:#C3D0DF; }
.foot-social a:hover { border-color:var(--gold-bright); color:var(--gold-bright); }
.foot-social a svg { width:19px; height:19px; }
.foot-bottom { background:var(--bg); text-align:center; padding:24px 20px 34px; }
.foot-bottom .flinks a { color:var(--text); text-decoration:underline; text-underline-offset:3px; font-size:.82rem; font-weight:600; margin:0 12px; }
.foot-bottom .flinks a:hover { color:var(--gold-deep); }
.foot-bottom .fco { color:var(--text-soft); font-size:.82rem; margin-top:12px; font-weight:700; letter-spacing:.02em; }
.foot-bottom .falert { color:var(--text-mut); font-size:.74rem; margin-top:10px; max-width:62ch; margin-left:auto; margin-right:auto; line-height:1.5; }
@media (max-width:820px){ .foot-cards { grid-template-columns:1fr; } .horarios { grid-template-columns:1fr; } }
@media (max-width:560px){ .contact-grid { grid-template-columns:1fr; } }

.scrim { position:fixed; inset:0; background:rgba(10,7,3,.55); opacity:0; pointer-events:none; transition:opacity .2s; z-index:60; }
.scrim.on { opacity:1; pointer-events:auto; }
.drawer { position:fixed; top:0; right:0; height:100%; width:min(400px,92vw); background:var(--surface); z-index:70; transform:translateX(100%); transition:transform .24s cubic-bezier(.4,0,.2,1); display:flex; flex-direction:column; box-shadow:var(--shadow-2); }
.drawer.on { transform:translateX(0); }
.drawer-head { display:flex; align-items:center; justify-content:space-between; padding:18px 20px; border-bottom:1px solid var(--border); }
.drawer-head b { font-family:var(--display); text-transform:uppercase; font-size:1.2rem; letter-spacing:.04em; }
.drawer-head button { background:none; border:none; color:var(--text-soft); font-size:1.5rem; line-height:1; }
.drawer-body { flex:1; overflow-y:auto; padding:12px 20px; }
.drawer-empty { text-align:center; color:var(--text-mut); padding:60px 20px; font-size:.9rem; }
.line { display:flex; gap:12px; padding:12px 0; border-bottom:1px solid var(--border); align-items:center; }
.line .li-emoji { font-size:1.7rem; width:44px; text-align:center; }
.line .li-info { flex:1; min-width:0; }
.line .li-info b { font-size:.84rem; font-weight:600; display:block; }
.line .li-info span { font-size:.78rem; color:var(--amber); font-weight:700; }
.qty { display:flex; align-items:center; gap:8px; }
.qty button { width:26px; height:26px; border-radius:7px; border:1px solid var(--border); background:var(--surface-2); color:var(--text); font-weight:700; }
.qty span { min-width:18px; text-align:center; font-variant-numeric:tabular-nums; font-weight:700; font-size:.9rem; }
.drawer-foot { padding:18px 20px 22px; border-top:1px solid var(--border); background:var(--surface-2); }
.drawer-foot .tot { display:flex; justify-content:space-between; font-family:var(--display); font-size:1.3rem; text-transform:uppercase; margin-bottom:4px; }
.drawer-foot .tot span:last-child { color:var(--amber); font-variant-numeric:tabular-nums; }
.drawer-foot small { color:var(--text-mut); font-size:.74rem; }
.btn { display:inline-flex; align-items:center; gap:9px; border:none; border-radius:var(--r-pill); padding:13px 22px; font-weight:700; font-size:.94rem; }
.btn svg { width:18px; height:18px; }
.btn-wa { background:#1FA855; color:#fff; } .btn-wa:hover { background:#22b95d; }
.drawer-foot .btn { width:100%; justify-content:center; margin-top:14px; }
.drawer-foot .btn-form { background:var(--negro); color:var(--gold-bright); margin-top:9px; }

.toast { position:fixed; bottom:22px; left:50%; transform:translateX(-50%) translateY(24px); background:var(--negro); color:var(--gold-bright); padding:12px 20px; border-radius:var(--r-pill); font-size:.86rem; font-weight:600; box-shadow:var(--shadow-2); opacity:0; pointer-events:none; transition:opacity .2s,transform .2s; z-index:80; border:1px solid rgba(245,197,24,.3); }
.toast.on { opacity:1; transform:translateX(-50%) translateY(0); }

.menu-scrim { position:fixed; inset:0; background:rgba(20,26,38,.30); backdrop-filter:blur(5px); -webkit-backdrop-filter:blur(5px); opacity:0; pointer-events:none; transition:opacity .2s; z-index:50; }
.menu-scrim.on { opacity:1; pointer-events:auto; }
.menu-panel { position:fixed; top:76px; left:20px; width:min(432px,calc(100vw - 40px)); max-height:calc(100vh - 104px); overflow-y:auto; background:var(--surface); border-radius:24px; box-shadow:var(--shadow-2); z-index:55; padding:18px; transform-origin:top left; transform:translateY(-10px) scale(.97); opacity:0; pointer-events:none; transition:opacity .18s, transform .18s; }
.menu-panel.on { opacity:1; pointer-events:auto; transform:translateY(0) scale(1); }
.menu-top { display:flex; align-items:center; justify-content:space-between; padding:6px 8px 16px; }
.menu-top a { display:inline-flex; align-items:center; gap:8px; font-size:.82rem; font-weight:800; letter-spacing:.04em; text-transform:uppercase; color:var(--gold-deep); text-decoration:underline; text-underline-offset:3px; }
.menu-top a svg { width:16px; height:16px; }
.menu-list { display:flex; flex-direction:column; gap:10px; }
.menu-row { position:relative; display:flex; align-items:center; gap:14px; padding:15px 16px; background:var(--surface-2); border-radius:15px; color:var(--text); font-weight:600; font-size:.98rem; transition:background .12s, transform .12s; }
.menu-row:hover { background:color-mix(in srgb, var(--gold) 15%, var(--surface-2)); transform:translateX(2px); }
.menu-row .mi { width:26px; display:grid; place-items:center; color:var(--gold-deep); flex:0 0 auto; }
.menu-row .mi svg { width:22px; height:22px; }
.menu-row .chev { margin-left:auto; color:var(--text-mut); display:grid; place-items:center; }
.menu-row .chev svg { width:18px; height:18px; }
.menu-row .newbadge { position:absolute; left:-9px; top:50%; transform:translateY(-50%); background:#E8324B; color:#fff; font-size:.6rem; font-weight:800; letter-spacing:.04em; text-transform:uppercase; padding:4px 9px; border-radius:var(--r-pill); box-shadow:0 3px 9px rgba(232,50,75,.45); }
.hchip .caret { transition:transform .18s; }
.hchip.open .caret { transform:rotate(180deg); }

@media (max-width:980px){ .railbar { display:none; } }
@media (max-width:760px){
  .hdr { grid-template-columns:auto 1fr auto; }
  .hchip .txt { display:none; }
  .brand .word { font-size:1.6rem; }
  .foot-grid { grid-template-columns:1fr 1fr; }
  .promo-grid { grid-template-columns:1fr; }
}
@media (prefers-reduced-motion:reduce){ *{ transition:none !important; } }
```

---

### C5 — `src\components\landing\Header.astro`

> Contiene: barra de edad, header (logo centrado, chips menú/ciudad, tema, carrito), fila de buscador, barra lateral flotante y el panel de menú desplegable. Incluye los scripts de **menú, tema y buscador** (Astro los hoista y ejecuta en el cliente). El carrito y sus contadores se manejan desde `index.astro`.

```astro
---
// Header estático (SSR). Interacción (menú/tema/buscador) por script de cliente.
---
<div class="agebar">🔞 <strong>Venta prohibida a menores de edad.</strong> El exceso de alcohol es perjudicial para la salud — Ley 30 de 1986 · Ley 124 de 1994.</div>

<header class="site">
  <div class="hdr">
    <div class="hdr-left">
      <button class="hchip" type="button" id="menuChip">
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M4 7h16M4 12h16M4 17h16"/></svg>
        <span class="txt">Menú</span>
        <svg class="caret" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><path d="m6 9 6 6 6-6"/></svg>
      </button>
      <button class="hchip" type="button" title="Cambiar ciudad">
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M12 21s7-5.6 7-11a7 7 0 1 0-14 0c0 5.4 7 11 7 11Z"/><circle cx="12" cy="10" r="2.5"/></svg>
        <b>Girardot</b>
        <svg class="caret" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><path d="m6 9 6 6 6-6"/></svg>
      </button>
    </div>
    <a class="brand" href="/" aria-label="LA POLA inicio">
      <span class="crest"><span class="line"></span> Est. 2012 · 24 h <span class="line r"></span></span>
      <span class="word">La&nbsp;Pola<span class="dot">.com</span></span>
      <span class="tagline">Distribuidora de bebidas</span>
    </a>
    <div class="hdr-right">
      <button class="theme-toggle" id="themeBtn" type="button" title="Cambiar tema" aria-label="Cambiar tema">
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M21 12.8A9 9 0 1 1 11.2 3 7 7 0 0 0 21 12.8Z"/></svg>
      </button>
      <button class="hchip cart-chip" type="button" id="cartBtn">
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M6 6h15l-1.5 9h-12L5 3H2"/><circle cx="9" cy="20" r="1.4"/><circle cx="18" cy="20" r="1.4"/></svg>
        <span class="txt">Carrito</span>
        <svg class="caret" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><path d="m6 9 6 6 6-6"/></svg>
        <span class="cart-count" id="cartCount" hidden>0</span>
      </button>
    </div>
  </div>
</header>

<div class="searchrow">
  <div class="box">
    <svg class="mag" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="11" cy="11" r="7"/><path d="m20 20-3-3"/></svg>
    <input type="search" placeholder="¿Qué estás buscando?" aria-label="Buscar productos" />
  </div>
</div>

<div class="railbar" aria-label="Accesos rápidos">
  <button type="button" title="Menú" id="railMenu"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M4 7h16M4 12h16M4 17h16"/></svg></button>
  <button type="button" title="Llámanos"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M4 5c0 9 6 15 15 15 1 0 2-1 2-2v-2.5c0-.8-.6-1.3-1.3-1.5l-2.6-.5c-.6-.1-1.2.1-1.6.6l-.7.9C13 14 10 11 9.5 8.7l.9-.7c.5-.4.7-1 .6-1.6l-.5-2.6C10.3 3.1 9.8 2.5 9 2.5H6.5C5.5 2.5 4 3.5 4 5Z"/></svg></button>
  <button type="button" class="active" title="Mi pedido" id="railCart"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M6 6h15l-1.5 9h-12L5 3H2"/><circle cx="9" cy="20" r="1.4"/><circle cx="18" cy="20" r="1.4"/></svg><span class="rc" id="railCount" hidden>0</span></button>
  <button type="button" title="Buscar" id="railSearch"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="11" cy="11" r="7"/><path d="m20 20-3-3"/></svg></button>
  <button type="button" title="Mi cuenta"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="8" r="4"/><path d="M4 21c0-4 4-6 8-6s8 2 8 6"/></svg></button>
</div>

<div class="menu-scrim" id="menuScrim"></div>
<nav class="menu-panel" id="menuPanel" aria-label="Menú principal">
  <div class="menu-top">
    <a href="#" title="Cambiar ciudad"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M12 21s7-5.6 7-11a7 7 0 1 0-14 0c0 5.4 7 11 7 11Z"/><circle cx="12" cy="10" r="2.5"/></svg> Girardot</a>
    <a href="#" title="Mi cuenta"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="8" r="4"/><path d="M4 21c0-4 4-6 8-6s8 2 8 6"/></svg> Mi cuenta</a>
  </div>
  <div class="menu-list">
    <a class="menu-row" href="#cat"><span class="mi"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M6 3h12l-1 6a5 5 0 0 1-10 0L6 3Z"/><path d="M12 14v5M8 21h8"/></svg></span>Productos<span class="chev"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.4"><path d="m9 6 6 6-6 6"/></svg></span></a>
    <a class="menu-row" href="#promos"><span class="mi"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M12 3l2.5 5 5.5.8-4 3.9.9 5.5L12 16.5 7.1 18.2 8 12.7 4 8.8 9.5 8 12 3Z"/></svg></span>Promociones<span class="chev"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.4"><path d="m9 6 6 6-6 6"/></svg></span></a>
    <a class="menu-row" href="#"><span class="mi"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M3 8h18v3H3zM5 11h14v9H5zM12 8v12M9 8a2 2 0 1 1 3-2 2 2 0 1 1 3 2"/></svg></span>Combos por caja<span class="chev"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.4"><path d="m9 6 6 6-6 6"/></svg></span></a>
    <a class="menu-row" href="#mayorista"><span class="newbadge">Nuevo</span><span class="mi"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M20 12l-8 8-9-9V3h8l9 9Z"/><circle cx="7.5" cy="7.5" r="1.4"/></svg></span>Precios mayorista<span class="chev"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.4"><path d="m9 6 6 6-6 6"/></svg></span></a>
    <a class="menu-row" href="#"><span class="mi"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M4 4h13a3 3 0 0 1 0 6h-2M4 4v9a5 5 0 0 0 10 0V4M9 21v-3M6 21h6"/></svg></span>Recetas y maridajes<span class="chev"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.4"><path d="m9 6 6 6-6 6"/></svg></span></a>
    <a class="menu-row" href="#horarios"><span class="mi"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M3 7h13v8H3zM16 10h3l2 3v2h-5"/><circle cx="7" cy="18" r="1.6"/><circle cx="18" cy="18" r="1.6"/></svg></span>Zona de cobertura<span class="chev"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.4"><path d="m9 6 6 6-6 6"/></svg></span></a>
    <a class="menu-row" href="#"><span class="mi"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="9"/><path d="M9.5 9a2.5 2.5 0 1 1 3.5 2.3c-.8.4-1 .9-1 1.7M12 17h.01"/></svg></span>Preguntas Frecuentes<span class="chev"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.4"><path d="m9 6 6 6-6 6"/></svg></span></a>
    <a class="menu-row" href="https://wa.me/573000000000" target="_blank" rel="noopener"><span class="mi"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M4 5h16v11H8l-4 4V5Z"/></svg></span>Contacto<span class="chev"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.4"><path d="m9 6 6 6-6 6"/></svg></span></a>
    <a class="menu-row" href="#"><span class="mi"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M5 4h11l3 3v13H5zM9 9h7M9 13h7M9 17h4"/></svg></span>Blog<span class="chev"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.4"><path d="m9 6 6 6-6 6"/></svg></span></a>
  </div>
</nav>

<script>
  const $ = (id: string) => document.getElementById(id);
  // Menú desplegable
  let menuOpen = false;
  const panel = $("menuPanel"), scrim = $("menuScrim"), chip = $("menuChip");
  const openMenu = () => { menuOpen = true; panel?.classList.add("on"); scrim?.classList.add("on"); chip?.classList.add("open"); };
  const closeMenu = () => { menuOpen = false; panel?.classList.remove("on"); scrim?.classList.remove("on"); chip?.classList.remove("open"); };
  const toggleMenu = () => (menuOpen ? closeMenu() : openMenu());
  $("menuChip")?.addEventListener("click", (e) => { e.stopPropagation(); toggleMenu(); });
  $("railMenu")?.addEventListener("click", (e) => { e.stopPropagation(); toggleMenu(); });
  scrim?.addEventListener("click", closeMenu);
  panel?.addEventListener("click", (e) => { if ((e.target as HTMLElement).closest(".menu-row")) closeMenu(); });
  document.addEventListener("keydown", (e) => { if (e.key === "Escape") closeMenu(); });
  // Buscador
  const focusSearch = () => {
    const i = document.querySelector<HTMLInputElement>(".searchrow input");
    i?.focus(); i?.scrollIntoView({ behavior: "smooth", block: "center" });
  };
  $("railSearch")?.addEventListener("click", focusSearch);
  // Tema claro/oscuro
  const root = document.documentElement;
  const currentDark = () => {
    const a = root.getAttribute("data-theme");
    if (a) return a === "dark";
    return window.matchMedia("(prefers-color-scheme: dark)").matches;
  };
  $("themeBtn")?.addEventListener("click", () => root.setAttribute("data-theme", currentDark() ? "light" : "dark"));
</script>
```

---

### C6 — `src\components\landing\Carrusel.astro`
```astro
---
// Carrusel de banners promocionales (contenido estático + script de rotación).
---
<section class="carousel-sec">
  <div class="wrap">
    <div class="carousel" id="carousel">
      <div class="track" id="track">
        <div class="slide s0">
          <div class="content">
            <span class="kicker">Combo del mes</span>
            <h2>Lleva más,<br /><em>paga menos</em></h2>
            <p>Cerveza por caja + hielo + gaseosa al precio más frío de la ciudad.</p>
            <button class="sbtn" type="button">Ver combos 🍺</button>
          </div>
          <span class="art">🍻</span>
          <div class="fine">Aplican términos y condiciones. El exceso de alcohol es perjudicial para la salud. Ley 30 de 1986 · Ley 124 de 1994.</div>
        </div>
        <div class="slide s1">
          <div class="content">
            <span class="kicker">Solo hoy</span>
            <h2>Domicilio<br /><em>gratis</em></h2>
            <p>En pedidos desde $80.000 dentro de tu zona de cobertura. Pide antes de las 4 p.m.</p>
            <button class="sbtn" type="button">Pedir ahora 🛵</button>
          </div>
          <span class="art">🛵</span>
          <div class="fine">Cobertura sujeta a disponibilidad. Consulta condiciones de entrega.</div>
        </div>
        <div class="slide s2">
          <div class="content">
            <span class="kicker">Para tu negocio</span>
            <h2>Precio<br /><em>mayorista</em></h2>
            <p>Tienda, asadero o billar: regístrate y compra por caja al precio de distribuidor.</p>
            <button class="sbtn" type="button">Registrar mi negocio 📦</button>
          </div>
          <span class="art">📦</span>
          <div class="fine">Precios mayorista visibles tras registro y verificación del negocio.</div>
        </div>
      </div>
      <button class="cbtn prev" id="cPrev" aria-label="Anterior"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><path d="m15 6-6 6 6 6"/></svg></button>
      <button class="cbtn next" id="cNext" aria-label="Siguiente"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><path d="m9 6 6 6-6 6"/></svg></button>
    </div>
    <div class="dots" id="dots"></div>
  </div>
</section>

<script>
  const track = document.getElementById("track")!;
  const dots = document.getElementById("dots")!;
  const slides = track.children.length;
  let idx = 0;
  for (let i = 0; i < slides; i++) {
    const b = document.createElement("button");
    b.setAttribute("aria-label", "Ir al banner " + (i + 1));
    b.dataset.d = String(i);
    dots.appendChild(b);
  }
  const go = (n: number) => {
    idx = (n + slides) % slides;
    track.style.transform = "translateX(-" + idx * 100 + "%)";
    Array.from(dots.children).forEach((d, j) => d.classList.toggle("on", j === idx));
  };
  let timer = window.setInterval(() => go(idx + 1), 5000);
  const reset = () => { window.clearInterval(timer); timer = window.setInterval(() => go(idx + 1), 5000); };
  document.getElementById("cPrev")!.addEventListener("click", () => { go(idx - 1); reset(); });
  document.getElementById("cNext")!.addEventListener("click", () => { go(idx + 1); reset(); });
  dots.addEventListener("click", (e) => {
    const t = (e.target as HTMLElement).closest<HTMLElement>("[data-d]");
    if (t) { go(Number(t.dataset.d)); reset(); }
  });
  const car = document.getElementById("carousel")!;
  car.addEventListener("mouseenter", () => window.clearInterval(timer));
  car.addEventListener("mouseleave", reset);
  go(0);
</script>
```

---

### C7 — `src\components\landing\Categorias.astro`
```astro
---
import { CATEGORIAS } from "@/features/catalogo/data/catalogo";
---
<section class="block" id="cat" style="padding-top:24px;">
  <div class="wrap">
    <div class="catcard">
      <span class="eyebrow">Nuestras categorías</span>
      <h2 class="cat-title">Explora nuestra variedad de bebidas</h2>
      <div class="cat-rail">
        {CATEGORIAS.map((c) => (
          <a class="cat-item" href="#destacados">
            <span class="circle" style={`background:${c.color}`}>{c.emoji}</span>
            <b>{c.nombre}</b>
            <span class="cnt">{c.skus} productos</span>
          </a>
        ))}
      </div>
    </div>
  </div>
</section>
```

---

### C8 — `src\components\landing\Descuentos.astro`
```astro
---
import { PROMOS, productoPorId, precioOriginal } from "@/features/catalogo/data/catalogo";
import { cop } from "@/shared/formato";
const items = PROMOS.map((pr) => {
  const p = productoPorId(pr.productoId)!;
  return { p, descuento: pr.descuento, original: precioOriginal(p.precio, pr.descuento) };
});
---
<section class="block" id="promos" style="padding-top:0;">
  <div class="wrap">
    <div class="promos">
      <div class="promos-left">
        <span class="eyebrow">Descuentos en bebidas</span>
        <h3 class="promos-title">¿Buscas precios realmente especiales?</h3>
        <a class="promos-btn" href="#promos">Descuentos <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.6"><path d="m9 6 6 6-6 6"/></svg></a>
      </div>
      <div class="promos-right">
        <div class="promo-rail">
          {items.map((it) => (
            <article class="promo-card">
              <span class="off-badge">{it.descuento}%<br />OFF</span>
              <div class="pemoji">{it.p.emoji}</div>
              <h4>{it.p.nombre}</h4>
              <div class="promo-foot">
                <span class="promo-price">
                  <span class="now">{cop(it.p.precio)}</span>
                  <span class="old">{cop(it.original)}</span>
                </span>
                <button class="padd" data-add={it.p.id} title="Agregar">
                  <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M6 6h15l-1.5 9h-12L5 3H2"/><circle cx="9" cy="20" r="1.4"/><circle cx="18" cy="20" r="1.4"/></svg>
                </button>
              </div>
            </article>
          ))}
        </div>
        <a class="promos-explore" href="#">Explorar todas las promos →</a>
      </div>
    </div>
  </div>
</section>
```

---

### C9 — `src\components\landing\Destacados.astro`
```astro
---
import { PRODUCTOS } from "@/features/catalogo/data/catalogo";
import { cop } from "@/shared/formato";
const tagHtml = (t: string | null) =>
  t === "rt" ? { cls: "tag rt", txt: "Retornable" }
  : t === "nrt" ? { cls: "tag nrt", txt: "No retornable" }
  : t ? { cls: "tag", txt: "Top" } : null;
---
<section class="block" id="destacados" style="padding-top:0;">
  <div class="wrap">
    <div class="sec-head">
      <div><span class="eyebrow">Los que más rotan</span><h2>Favoritos de La Pola</h2></div>
      <a class="more" href="#">Ver catálogo completo →</a>
    </div>
    <div class="prod-grid">
      {PRODUCTOS.map((p) => {
        const tag = tagHtml(p.etiqueta);
        return (
          <article class="card">
            <div class="thumb">
              {tag && <span class={tag.cls}>{tag.txt}</span>}
              <span class="bottle">{p.emoji}</span>
            </div>
            <div class="body">
              <span class="cat-lbl">{p.categoria}</span>
              <h3>{p.nombre}</h3>
              <span class="pres">{p.presentacion}</span>
              <div class="foot">
                <span class="price">{cop(p.precio)}<small>precio mostrador</small></span>
                <button class="add" data-add={p.id}>
                  <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.4"><path d="M12 5v14M5 12h14"/></svg>Agregar
                </button>
              </div>
            </div>
          </article>
        );
      })}
    </div>
  </div>
</section>
```

---

### C10 — `src\components\landing\PieDePagina.astro`

> Contiene: banda promo (mayorista), sección Horarios, banda de confianza y footer. Datos de contacto = MOCK.

```astro
---
// Cierre de la página: banda promo + horarios + confianza + footer. Todo estático (SSR).
---
<section class="block" id="mayorista" style="padding-top:0;">
  <div class="wrap">
    <div class="promo"><div class="promo-grid">
      <div class="promo-item"><div class="pic"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M3 7h13v8H3zM16 10h3l2 3v2h-5"/><circle cx="7" cy="18" r="1.6"/><circle cx="18" cy="18" r="1.6"/></svg></div><div><b>Domicilio el mismo día</b><p>Pide antes de las 4 p.m. y recíbelo hoy en tu zona.</p></div></div>
      <div class="promo-item"><div class="pic"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M4 7h16v10H4zM8 7V5h8v2M9 11h6"/></svg></div><div><b>¿Tienes un negocio?</b><p>Regístrate y accede a precios mayorista por caja y volumen.</p></div></div>
      <div class="promo-item"><div class="pic"><svg viewBox="0 0 24 24" fill="currentColor"><path d="M12 2a10 10 0 1 0 0 20 10 10 0 0 0 0-20Zm0 4a6 6 0 1 1 0 12A6 6 0 0 1 12 6Z"/></svg></div><div><b>Pide como quieras</b><p>Carrito directo a WhatsApp o formulario de pedido.</p></div></div>
    </div></div>
  </div>
</section>

<section class="block" id="horarios">
  <div class="wrap horarios">
    <div class="hor-left">
      <div class="hor-art">🛵</div>
      <h3 class="hor-title">Horarios<br />Girardot</h3>
    </div>
    <div class="hor-card">
      <span class="eyebrow">Abierto: lunes a domingo</span>
      <div class="hor-row">
        <span class="hicon"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8"><circle cx="12" cy="13" r="8"/><path d="M12 9v4l2.5 2M5 3 2.5 5.5M19 3l2.5 2.5"/></svg></span>
        <p><b>Pedidos 24/7</b><br />(Página web)</p>
      </div>
      <div class="hor-row">
        <span class="hicon"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8"><rect x="4" y="5" width="16" height="16" rx="2"/><path d="M4 9h16M8 3v4M16 3v4M9 14l2 2 4-4"/></svg></span>
        <p>Escoge fecha y hora de<br />entrega en el checkout</p>
      </div>
    </div>
  </div>
</section>

<div class="trustband">
  <div class="trust-inner">
    <div class="trust-group">
      <h5>Respaldados por</h5>
      <div class="trust-logos">
        <span class="trust-chip"><span class="tdot" style="background:#E8324B">CC</span>Cámara de Comercio</span>
        <span class="trust-chip"><span class="tdot" style="background:#1E6FD9">F</span>Fenalco</span>
        <span class="trust-chip"><span class="tdot" style="background:#0F9D58">A</span>Acopi</span>
      </div>
    </div>
    <div class="trust-group">
      <h5>Vigilados por</h5>
      <div class="trust-logos">
        <span class="trust-chip"><span class="tdot" style="background:#C79A2E">IN</span>Invima</span>
        <span class="trust-chip"><span class="tdot" style="background:#1C2433">SIC</span>Superintendencia de Industria y Comercio</span>
      </div>
    </div>
  </div>
</div>

<footer class="site">
  <div class="foot-top">
    <div class="foot-logo">La&nbsp;Pola<span class="dot">.com</span><small>Distribuidora de bebidas · Est. 2012</small></div>
  </div>
  <div class="foot-cards">
    <div class="fcard">
      <div class="fhead"><span class="fi"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M6 3h12l-1 6a5 5 0 0 1-10 0L6 3Z"/><path d="M12 15v4M8 21h8"/></svg></span>Descubre aún más</div>
      <a class="flink" href="#">Recetas y maridajes</a>
      <a class="flink" href="#">Combos por caja</a>
      <a class="flink" href="#mayorista">Precios mayorista</a>
    </div>
    <div class="fcard">
      <div class="fhead"><span class="fi"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="8" r="4"/><path d="M4 21c0-4 4-6 8-6s8 2 8 6"/></svg></span>Acerca de nosotros</div>
      <a class="flink" href="#">Quiénes somos</a>
      <a class="flink" href="#horarios">Zona de cobertura</a>
      <a class="flink" href="#">Blog</a>
    </div>
    <div class="fcard">
      <div class="fhead"><span class="fi"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M4 5c0 9 6 15 15 15 1 0 2-1 2-2v-2.5c0-.8-.6-1.3-1.3-1.5l-2.6-.5c-.6-.1-1.2.1-1.6.6l-.7.9C13 14 10 11 9.5 8.7l.9-.7c.5-.4.7-1 .6-1.6l-.5-2.6C10.3 3.1 9.8 2.5 9 2.5H6.5C5.5 2.5 4 3.5 4 5Z"/></svg></span>Datos de contacto</div>
      <div class="contact-grid">
        <div class="cg"><h6>Dirección</h6><p>Cra. 10 # 15 - 30<br />Girardot, Cundinamarca</p></div>
        <div class="cg"><h6>Teléfono</h6><a href="tel:+573000000000">(+57) 300 000 0000</a><a href="tel:+576010000000">(601) 000 0000</a></div>
        <div class="cg"><h6>WhatsApp</h6><a href="https://wa.me/573000000000" target="_blank" rel="noopener">300 000 0000</a></div>
        <div class="cg"><h6>E-mail</h6><a href="mailto:pedidos@lapola.com">pedidos@lapola.com</a></div>
      </div>
    </div>
  </div>
  <div class="foot-social">
    <a href="#" aria-label="Instagram"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect x="3" y="3" width="18" height="18" rx="5"/><circle cx="12" cy="12" r="4"/><circle cx="17.5" cy="6.5" r="1" fill="currentColor" stroke="none"/></svg></a>
    <a href="#" aria-label="Facebook"><svg viewBox="0 0 24 24" fill="currentColor"><path d="M14 9h3V6h-3c-2.2 0-4 1.8-4 4v2H8v3h2v6h3v-6h3l1-3h-4v-2c0-.6.4-1 1-1Z"/></svg></a>
    <a href="#" aria-label="TikTok"><svg viewBox="0 0 24 24" fill="currentColor"><path d="M16 3c.3 2.3 1.7 3.8 4 4v3c-1.5 0-2.9-.5-4-1.3V16a6 6 0 1 1-6-6c.3 0 .7 0 1 .1v3.2A2.8 2.8 0 1 0 13 16V3h3Z"/></svg></a>
    <a href="#" aria-label="YouTube"><svg viewBox="0 0 24 24" fill="currentColor"><path d="M22 12s0-3-.4-4.4a2.5 2.5 0 0 0-1.7-1.8C18.3 5.4 12 5.4 12 5.4s-6.3 0-7.9.4A2.5 2.5 0 0 0 2.4 7.6C2 9 2 12 2 12s0 3 .4 4.4a2.5 2.5 0 0 0 1.7 1.8c1.6.4 7.9.4 7.9.4s6.3 0 7.9-.4a2.5 2.5 0 0 0 1.7-1.8C22 15 22 12 22 12Zm-12 3V9l5 3-5 3Z"/></svg></a>
  </div>
  <div class="foot-bottom">
    <div class="flinks"><a href="#">Términos y condiciones</a><a href="#">Política de privacidad</a><a href="#">Política de cookies</a></div>
    <p class="fco">DISPOLA SAS · LA POLA © 2026 — Todos los derechos reservados</p>
    <p class="falert">Prohíbase el expendio de bebidas embriagantes a menores de edad. El exceso de alcohol es perjudicial para la salud — Ley 30 de 1986 · Ley 124 de 1994. Prohibido fumar — Ley 1335 de 2009. Precios en COP. Maqueta de demostración con datos de referencia.</p>
  </div>
</footer>
```

---

### M2 — `src\pages\index.astro` (REEMPLAZAR TODO el archivo)

> Compone todos los componentes, monta la isla del carrito, incluye el toast y el **script puente** que conecta los botones "Agregar" (SSR) y los botones de carrito con el store Zustand, y sincroniza los contadores.

```astro
---
import Base from "../layouts/Base.astro";
import Header from "../components/landing/Header.astro";
import Carrusel from "../components/landing/Carrusel.astro";
import Categorias from "../components/landing/Categorias.astro";
import Descuentos from "../components/landing/Descuentos.astro";
import Destacados from "../components/landing/Destacados.astro";
import PieDePagina from "../components/landing/PieDePagina.astro";
import CarritoDrawer from "../features/carrito/components/CarritoDrawer.tsx";

const jsonLd = {
  "@context": "https://schema.org",
  "@type": "Store",
  name: "LA POLA",
  description: "Distribuidora de bebidas: cervezas, gaseosas, agua, jugos y energizantes a domicilio.",
  address: { "@type": "PostalAddress", addressLocality: "Girardot", addressRegion: "Cundinamarca", addressCountry: "CO" },
  priceRange: "$$",
};
---

<Base
  titulo="LA POLA — Distribuidora de bebidas a domicilio"
  descripcion="Cervezas, gaseosas, agua, jugos y energizantes al mejor precio para tu negocio y tu casa. Pedido fácil por WhatsApp en Girardot."
>
  <script type="application/ld+json" slot="head" set:html={JSON.stringify(jsonLd)} />

  <Header />
  <Carrusel />
  <main>
    <Categorias />
    <Descuentos />
    <Destacados />
    <PieDePagina />
  </main>

  <CarritoDrawer client:idle />
  <div class="toast" id="toast"></div>
</Base>

<script>
  import { useCarrito, unidadesDe } from "@/features/carrito/stores/carrito";
  import { productoPorId } from "@/features/catalogo/data/catalogo";

  const toast = document.getElementById("toast");
  let toastT: number | undefined;
  const mostrarToast = (msg: string) => {
    if (!toast) return;
    toast.textContent = msg;
    toast.classList.add("on");
    window.clearTimeout(toastT);
    toastT = window.setTimeout(() => toast.classList.remove("on"), 1800);
  };

  // Delegación de clics: botones "Agregar" (data-add) y aperturas del carrito.
  document.addEventListener("click", (e) => {
    const target = e.target as HTMLElement;
    const addEl = target.closest<HTMLElement>("[data-add]");
    if (addEl) {
      const id = addEl.getAttribute("data-add")!;
      useCarrito.getState().agregar(id);
      mostrarToast("Agregado: " + (productoPorId(id)?.nombre ?? "producto"));
      return;
    }
    if (target.closest("#cartBtn") || target.closest("#railCart")) {
      useCarrito.getState().abrir();
    }
  });

  // Sincroniza los contadores del header y de la barra lateral con el store.
  const badges = [document.getElementById("cartCount"), document.getElementById("railCount")];
  const pintarBadges = (n: number) => {
    badges.forEach((b) => {
      if (!b) return;
      if (n > 0) { b.hidden = false; b.textContent = String(n); }
      else { b.hidden = true; }
    });
  };
  pintarBadges(unidadesDe(useCarrito.getState().items)); // estado inicial
  useCarrito.subscribe((s) => pintarBadges(unidadesDe(s.items)));
</script>
```

---

## 6. Orden de ejecución

1. C1 `formato.ts`
2. C2 `catalogo.ts`
3. C3 `carrito.ts`
4. C4 `CarritoDrawer.tsx`
5. M1 `global.scss` (reemplazar)
6. C5 `Header.astro`
7. C6 `Carrusel.astro`
8. C7 `Categorias.astro`
9. C8 `Descuentos.astro`
10. C9 `Destacados.astro`
11. C10 `PieDePagina.astro`
12. M2 `index.astro` (reemplazar)
13. Validar (§8).

> Los directorios nuevos (`src/shared`, `src/features/catalogo/data`, `src/features/carrito/stores`, `src/features/carrito/components`, `src/components/landing`) se crean al crear los archivos.

---

## 7. Reglas no negociables

1. **NO** instalar dependencias, **NO** tocar `package.json`, `pnpm-lock.yaml`, `astro.config.mjs`, `tsconfig.json`, `Base.astro`, `EstadoApi.tsx`.
2. **NO** cambiar valores de colores, textos legales, ni números. Pegar el código **exactamente**.
3. Rutas de import: usar `@/...` (ya configurado). No usar rutas relativas profundas.
4. La isla del carrito se hidrata **solo** con `client:idle` (nunca `client:load`).
5. Todo el contenido de producto (nombre, precio, categoría) queda en HTML SSR (`.astro`) — **regla R5**. No mover contenido a la isla.
6. Idioma español en todo. No renombrar clases CSS (el `global.scss` depende de esos nombres exactos).
7. Si un archivo ya existe, **reemplazar** su contenido completo (aplica a M1 y M2). Los C# son nuevos.
8. **NO ejecutar `pnpm test`** (falla sin tests). El único gate automatizado es `pnpm build`.
9. En la isla del carrito, **nunca** seleccionar datos derivados con `useCarrito((s) => s.fn())` que devuelvan objetos/arrays nuevos — usar solo `items`/acciones y derivar con `useMemo([items])` (evita re-render infinito; regla R2).

---

## 8. Validaciones (criterios de aceptación)

Ejecutar en orden. Todos deben pasar.

| # | Comando (desde `c:\APLICACIONES\sellweb\frontend`) | Resultado esperado |
|---|---|---|
| V1 | `pnpm build` | Termina sin errores. Genera `dist/`. Sin errores de TypeScript ni de import. |
| V2 | `pnpm dev` (dejar corriendo) | Server en `http://localhost:8889/` sin errores en consola. |
| V3 | Abrir `http://localhost:8889/` en el navegador | Se ve la home completa: header con logo "La Pola.com" centrado, buscador, barra lateral izquierda, carrusel rotando, categorías (9 círculos), descuentos, destacados, horarios, footer. |
| V4 | Ver código fuente de la página (Ctrl+U) | Los nombres y precios de productos aparecen en el HTML (SSR), no solo por JS. |
| V4b | `curl -s http://localhost:8889/` (otra terminal) → buscar `Club Colombia` y `20.500` | Ambos aparecen en el HTML servido (prueba SSR real, regla R5). |
| V5 | Clic en "Menú" | Abre el panel desplegable con fondo difuminado; cierra con Esc o clic afuera. |
| V6 | Clic en "Agregar" de un producto | Aparece toast, el contador del carrito (header y barra lateral) sube. **Verifica la coherencia del store compartido** entre el `<script>` de Astro y la isla React (deben ser el mismo módulo/instancia). |
| V7 | Clic en el botón "Carrito" | Abre el cajón lateral con el producto, permite +/−, muestra total y botón "Enviar pedido por WhatsApp" con enlace `wa.me` que incluye el detalle. **Sin errores en consola** (especialmente NO debe aparecer "getSnapshot should be cached" ni "Maximum update depth"). |
| V8 | Clic en el botón de tema (☀/☾) | La página alterna entre claro y oscuro. |

> **Verificación final = build verde + interacción humana en navegador** (V3–V8). Sin la prueba visual, el estado es "implementado pendiente de validación".

---

## 9. Fuera de alcance (NO hacer)

- Conexión a la API FastAPI real (los datos son mock). El endpoint de catálogo es trabajo posterior.
- Checkout con persistencia en BD, pasarela de pagos (D3 pendiente), formulario real (el botón "Enviar por formulario" solo muestra un `alert`).
- Imágenes reales de producto (se usan emojis; luego se cambian por `astro:assets`).
- Páginas internas (catálogo `/catalogo`, ficha `/producto/[slug]`, cuenta, blog): los enlaces del menú/footer apuntan a `#` a propósito.
- Sitemap/robots (ya cubiertos por `@astrojs/sitemap` en config).
- Tests unitarios/E2E de la landing.
- Persistir el carrito en `localStorage` (fase posterior).

---

## 10. Reporte esperado del ejecutor

```
✅/❌ Paso 1..13
Archivos creados: [lista]
Archivos modificados: [lista]
Resultado V1..V8: [✅/❌ por cada uno]
¿Hago commit?
```
Mensaje de commit sugerido (si se aprueba): `feat(LANDING-1): implementar landing LA POLA con componentes Astro + carrito Zustand`
