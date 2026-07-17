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
