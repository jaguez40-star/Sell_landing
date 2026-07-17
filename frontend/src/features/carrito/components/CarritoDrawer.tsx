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
