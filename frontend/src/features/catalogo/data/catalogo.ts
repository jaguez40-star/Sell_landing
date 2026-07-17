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
