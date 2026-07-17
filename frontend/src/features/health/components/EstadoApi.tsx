import { useEffect, useState } from "react";

// Isla React de ejemplo — verifica la conexión con la API FastAPI end-to-end.
// Se reemplazará por las features reales (catálogo, carrito, checkout).
type Estado = "cargando" | "ok" | "error";

export default function EstadoApi() {
  const [estado, setEstado] = useState<Estado>("cargando");
  const [servicio, setServicio] = useState<string>("");

  useEffect(() => {
    fetch("/api/health")
      .then((r) => r.json())
      .then((d) => {
        setServicio(d.service);
        setEstado("ok");
      })
      .catch(() => setEstado("error"));
  }, []);

  const texto =
    estado === "cargando"
      ? "Conectando con la API…"
      : estado === "ok"
        ? `API conectada: ${servicio}`
        : "API no disponible (¿backend en :8890?)";

  const color = estado === "ok" ? "#0a7d33" : estado === "error" ? "#c0392b" : "#666";

  return (
    <p style={{ color, fontWeight: 600 }} role="status">
      ● {texto}
    </p>
  );
}
