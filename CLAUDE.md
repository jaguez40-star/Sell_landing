# CLAUDE.md — DISPOLA SAS: Landing Page + Tienda Virtual

Sitio web público para DISPOLA SAS: landing page corporativa + tienda virtual, con SEO como requisito de primer nivel.

---

## 1. Idioma y estilo de comunicación

- **Todo en español** (mensajes, respuestas, comentarios de código, commits, ramas).
- **Respuestas breves y directas.** Sin preámbulos ("Claro", "Por supuesto"). No explicar antes de hacer ni resumir después salvo que el resultado lo amerite. Si la respuesta es código, entregar el código. Máximo 2-3 líneas de explicación cuando haga falta. Tuteo informal.

---

## 2. Stack tecnológico

### Frontend público (`frontend/`)

| Componente | Versión | Uso |
|------------|---------|-----|
| Astro | 5.x | Framework del sitio público — SSR, páginas SEO (landing, catálogo, fichas de producto) |
| React | 19 | Islas interactivas (carrito, buscador, checkout, admin futuro) |
| TypeScript | 5.x | Tipado estricto |
| TanStack Query | v5 | Estado de servidor en islas React |
| Zustand | 5 | Estado global de cliente (carrito) |
| react-hook-form | 7.x | Formularios |
| zod | 4.x | Validación de schemas |
| Sass | latest | Estilos (Sass Modules) |
| Lucide React | latest | Iconografía tree-shakeable |
| openapi-typescript + openapi-fetch | latest | Tipos auto + cliente HTTP tipado desde OpenAPI de FastAPI |
| Vitest + RTL | latest | Tests unitarios |
| Playwright | latest | Tests E2E |
| pnpm | latest | Gestor de paquetes + workspaces |

### Backend (`backend/`)

| Componente | Versión | Uso |
|------------|---------|-----|
| Python | 3.12+ | Lenguaje base |
| FastAPI | latest | API REST + generación automática de OpenAPI |
| SQLAlchemy | 2.0+ | ORM |
| Alembic | latest | Migraciones de base de datos |
| Pydantic | 2.x | Validación |
| structlog | latest | Logs en formato JSON UTC |
| itsdangerous | 2.x | Cookie firmada de sesión |
| uv | latest | Gestor de paquetes / entorno |
| Ruff + Black + mypy | latest | Lint + formateo + chequeo de tipos |
| pytest | latest | Tests unitarios e integración |

### Base de datos

| BD | Tipo | Rol |
|----|------|-----|
| `data/dispola.db` | SQLite | BD principal fase de desarrollo (catálogo, pedidos, clientes) |

> SQLite es la decisión de la fase inicial (D2). Antes de salir a producción se evalúa migrar a PostgreSQL (las migraciones Alembic deben mantenerse compatibles: evitar SQL específico de SQLite).

### Puertos y despliegue

| Entorno | Componente | URL |
|---------|-----------|-----|
| Desarrollo | Sitio (Astro SSR) | `http://localhost:8889` |
| Desarrollo | API (FastAPI/uvicorn) | `http://localhost:8890` |
| Producción | Todo bajo dominio único | Reverse proxy Caddy (HTTPS automático) — dominio pendiente (D4) |

---

## 3. Arquitectura

### Tres capas

1. **Astro (SSR)** — renderiza todas las páginas públicas con HTML completo: landing, catálogo, fichas de producto. Son las páginas que posicionan en Google.
2. **Islas React** — solo las partes interactivas se hidratan como componentes React dentro de páginas Astro: carrito, buscador, checkout.
3. **FastAPI + SQLite** — única fuente de datos. Astro (server-side) y las islas React consumen la misma API.

### Estructura de directorios

```
sellweb/
├── CLAUDE.md
├── package.json              # raíz pnpm workspace (orquesta front + back con concurrently)
├── frontend/                 # Astro + islas React
│   ├── astro.config.mjs
│   └── src/
│       ├── pages/            # rutas Astro (SEO): index, catalogo/, producto/[slug]
│       ├── layouts/          # layouts base con <head> SEO
│       ├── components/       # componentes .astro estáticos
│       ├── features/         # feature-based (islas React + su lógica)
│       │   └── <feature>/
│       │       ├── components/   # islas React del dominio
│       │       ├── hooks/        # TanStack Query
│       │       ├── mappers/      # to<Entity>UI(api) — snake_case → camelCase
│       │       ├── services/     # cliente HTTP tipado (openapi-fetch)
│       │       └── stores/       # Zustand (patrón draft/applied si hay filtros)
│       ├── shared/           # utilidades y componentes transversales
│       └── styles/           # Sass global + tokens de marca
├── backend/
│   ├── pyproject.toml
│   ├── alembic/
│   └── app/
│       ├── main.py
│       ├── core/             # config, logging, middleware (correlation_id + request_logger)
│       ├── shared/
│       └── features/         # vertical slicing
│           └── <feature>/
│               ├── api.py            # endpoints FastAPI
│               ├── services.py       # lógica de negocio
│               ├── repositories.py   # ÚNICO punto de SQL
│               ├── models.py         # SQLAlchemy
│               └── schemas.py        # Pydantic
├── data/                     # SQLite (NO versionada)
├── Planes/                   # planes generados en modo plan:
├── docs/decisions/           # ADRs ligeros
└── scripts/                  # backup.ps1, seeds, helpers
```

### Reglas de arquitectura

- **Vertical slicing:** cada feature es autocontenida. Una feature solo importa de `shared/` o `core/` — **nunca** de otra feature.
- **Repository–Service–Route:** `repositories.py` (único punto de SQL) → `services.py` (lógica) → `api.py` (endpoints).
- El contrato JSON de la API es `snake_case` (sin alias Pydantic — no hay sistema legado).

### Naming entre capas

| Lugar | Convención | Ejemplo |
|-------|-----------|---------|
| Backend (Python) | `snake_case` | `precio_unitario` |
| Contrato JSON (API) | `snake_case` | `precio_unitario` |
| Frontend (TS) | `camelCase` | `precioUnitario` |

- **Mapper único** — funciones puras `to<Entity>UI(api)` en `mappers/` traducen `snake_case → camelCase`. Es el único punto de traducción.

---

## 4. SEO — requisito de primer nivel

Toda página pública debe cumplir:

- HTML completo servido por SSR (nunca contenido crítico solo-cliente).
- `<title>` y `<meta name="description">` únicos por página.
- Open Graph + Twitter Card en fichas de producto.
- **JSON-LD `Product`** en cada ficha (nombre, precio en COP, disponibilidad) — habilita rich results.
- URLs limpias con slug: `/producto/guantes-nitrilo-caja-100`.
- Sitemap XML automático (`@astrojs/sitemap`) + `robots.txt`.
- Imágenes con `alt`, lazy loading y formatos modernos (`astro:assets`).
- Core Web Vitals: las islas React se hidratan con `client:visible`/`client:idle`, nunca `client:load` sin justificación.

---

## 4-bis. Dominio del negocio

**LA POLA** (marca pública de DISPOLA SAS): **distribuidora B2B de bebidas** que revende a negocios (tiendas, asaderos, billares) y personas. Fuente de datos real: `data_ref/POLA.db` (POS/inventario del negocio hermano), 118 SKUs.

### Categorías del catálogo (`DIM_productos.categoria_inventarios`)

| Código | Categoría | SKUs |
|--------|-----------|------|
| GASPET001 | Gaseosa PET | 29 |
| CVZLT001 | Cervezas Lata | 28 |
| AGUA001 | Agua | 18 |
| CVZRT001 | Cervezas Botella Retornable (RT) | 13 |
| CVZNRT001 | Cervezas Botella No Retornable (NRT) | 10 |
| JUG001 | Jugos | 9 |
| BEBREH001 | Bebidas Energizantes PET | 5 |
| CIGARRO001 | Cigarrillos | 4 |
| BELT001 | Bebidas Energizantes Lata | 2 |

- **Producto:** físico. Venta por unidad y por pack (`facturacion_pack` / `unidades_facturacion_pack`, unidad `uds` vs `SXP`). Flag retornable RT/NRT en cervezas. Stock real con costeo FIFO por lotes.
- **Clientes:** `persona_natural` (19) y `persona_juridica` (1); muchas "personas naturales" son negocios. Crédito (`dias_credito`, `limite_credito_cop`) modelado, en 0 → desactivado fase 1.
- **Precios:** 3 niveles en BD (`precio_venta_1` mostrador / `_2` mayorista / `_3` volumen). Regla: público solo `precio_venta_1`; escalones mayoristas solo para clientes logueados.
- **Seed fase 1:** importar `DIM_productos` → `productos`, `DIM_inventarios` → stock; excluir 4 SKUs con `precio_venta_1 <= 0`; traducir `snake_case` legado al contrato nuevo.

### Landing — secciones

Hero (CTA catálogo/WhatsApp) · Categorías destacadas · Productos destacados · Quiénes somos · Cobertura/zona de reparto · Contacto (WhatsApp + formulario).

---

## 5. Decisiones bloqueadas

Nunca cambiarlas sin confirmación explícita del usuario.

| ID | Estado | Decisión |
|----|--------|----------|
| D1 | ✅ Cerrada | Astro SSR + islas React para el sitio público, FastAPI como API. Dev: Astro `:8889`, API `:8890`. Producción: reverse proxy Caddy bajo dominio único. Migración a SSG como opción futura (solo config). |
| D2 | ✅ Cerrada | SQLite (`data/dispola.db`) para la fase inicial de desarrollo. Migración a PostgreSQL evaluable antes de producción. |
| D3 | 🔶 Pendiente | Pasarela de pagos — el pipeline de venta aún no está definido (candidatas Colombia: Wompi, Mercado Pago, ePayco, PayU). |
| D4 | 🔶 Pendiente | Dominio — se suministra con el desarrollo ~80% avanzado. |
| D5 | ✅ Cerrada | Checkout fase 1 = **ambos**: formulario que persiste el pedido en `data/dispola.db` + botón WhatsApp de respaldo. Sin pago online hasta cerrar D3. |
| D6 | ✅ Cerrada | Catálogo físico (~114 SKUs comercializables de 118), 9 categorías de bebidas. Variantes = presentación/pack (unidad `uds` / six-pack `SXP` / caja). Flag retornable RT/NRT en cervezas. Stock real (FIFO por lotes). Ver ADR-001 y § 4-bis. |
| D7 | ✅ Cerrada | B2B con registro + invitado. Precios escalonados: público solo ve `precio_venta_1`; mayorista (`_2`/`_3`) solo para clientes logueados, nunca en HTML público. Crédito modelado pero desactivado en fase 1. |
| D8 | ✅ Cerrada | Fase 1 por **seed/importación** desde `data_ref/POLA.db` → `data/dispola.db`. CRUD admin en fase posterior. |
| D9 | ✅ Cerrada | Marca pública **LA POLA** (DISPOLA SAS = razón social). Escudo cervecero negro + dorado/ámbar. Paleta: dorado `#f7db17`, ámbar `#c8860a`/`#a3631c`, malta `#824711`/`#441a09`, negro `#1c1917`, crema `#fdfaf7`. Logos en el proyecto hermano `01032026_WebApp/app/static/images/POLA_0{1,2,3}.png`. |
| — | Asumido | Moneda COP, sitio solo en español, `git init` al arrancar. |

Detalle completo del dominio, mapeo de columnas y secciones de landing: `docs/decisions/ADR-001_dominio_e_identidad.md`.

---

## 6. Modos de invocación (prefijos de mensaje)

### `plan:` — Modo Planner (no ejecuta, solo especifica)

Claude actúa exclusivamente como Planner: genera un archivo `.md` en `Planes/` con la especificación completa para que un **agente externo sin acceso al repo ni contexto previo** lo ejecute al pie de la letra.

Reglas clave:
1. Solo genera el plan, nunca ejecuta. Cero ediciones a código.
2. El plan es 100% autocontenido (el executor no ve conversaciones ni git previos).
3. Rutas **absolutas** siempre.
4. Código de referencia completo para cada archivo a crear.
5. Contexto del proyecto inline (stack, estructura, convenciones, env vars).
6. Dependencias explícitas + check de verificación ejecutable.
7. Criterios de aceptación verificables (tabla comando → resultado esperado).
8. Decisiones cerradas: el executor no decide nada.
9. Secciones: Contexto → Objetivo → Prerequisitos → Inventario archivos → Especificación → Orden ejecución → Reglas no negociables → Validaciones → Fuera de alcance.
10. Naming: `Planes/plan_[ID_TAREA]_[fecha].md`.
11. Mostrar ruta + resumen de 5 líneas → esperar "¿Aprobado?".

Prompt estándar para el executor:
```
Eres un agente EXECUTOR. Lee completo el plan indicado y ejecútalo AL PIE DE LA LETRA.
Reglas: CERO modificaciones. Orden secuencial. Si falla, DETENTE. Reporta: ✅/❌ Paso N.
Al final: archivos tocados + "¿Hago commit?"
```

### `backup:` — Modo Backup

Ejecuta `scripts/backup.ps1`. Naming con timestamp (`backup_{YYYYMMDD_HHMM}.zip`). Respalda Tier 1 irrecuperables (`.env`, `data/*.db`) y Tier 2 caros de regenerar (seeds, imágenes de producto). Incluye `MANIFEST.md` dentro del zip con git HEAD, branch y receta de restauración.

---

## 7. Directiva de auditoría previa antes de escribir un plan

🔴 **Nunca entregar un plan "v1 improvisado" para mejorarlo en "v2" cuando el usuario detecte fallos.** El plan entregado debe ser ya un v2 auditado.

Si la tarea toca >3 archivos, introduce primitivos/hooks/utils nuevos, modifica archivos compartidos, o cambia contratos entre capas → ejecutar antes:
1. Grep de archivos similares existentes (confirmar convención).
2. Read completo del archivo a modificar (no de memoria).
3. Verificar paths de imports contra archivos vecinos.
4. Leer configs relevantes (`astro.config.mjs`, `package.json`, `tsconfig`, `pyproject.toml`).
5. Cruzar contra la deuda técnica (§ 10).
6. Cruzar contra reglas duras (§ 9).

Si la auditoría revela un bloqueante (decisión bloqueada afectada, riesgo crítico) → detener y escalar **antes** de escribir el plan.

Anti-patrones prohibidos: plan v1 "rápido" a sabiendas, asumir paths/configs de memoria, "esto probablemente funciona, lo confirma el typecheck", esperar a que el usuario pida "aplica el flujo profesional".

---

## 8. Flujo profesional de ejecución (6 pasos)

Antes de cualquier tarea no trivial:

**Mapeo → Auditoría → Diagnóstico → Propuesta → Aplicación → Verificación**

- No saltear pasos. Propuesta completa antes de aplicar.
- Si un hallazgo afecta una decisión bloqueada → detener y escalar.
- **Verificación = build verde + lint verde + tests verde + INTERACCIÓN HUMANA EN NAVEGADOR** (para features visuales). Sin lo último, el estado es "implementado pendiente de validación", no "completado".

---

## 9. Reglas duras

- **R1 — No modificar infraestructura compartida sin ADR.** Lockfiles, `astro.config.mjs`, `tsconfig`, `pyproject.toml`, config de gestores de paquetes. Si una librería falla al instalar: diagnosticar peer deps, no aplicar atajos. Si no se resuelve en 15 min → detener y escalar con ADR.
- **R2 — Estado interactivo desacoplado de datos memoizados.** En islas React, los `useMemo` de datos nunca dependen de selección/hover. Deps del `useMemo` = solo datos crudos.
- **R3 — "Build verde" ≠ "feature verificada".** El linter/typecheck/tests no detectan layout colapsado, eventos mal cableados ni race conditions en `useEffect`. El único que marca ✅ una feature visual es el usuario tras probarla en el navegador.
- **R4 — Si un fix reactivo se acumula >2 iteraciones sin resolver el bug, detener y revertir** al último estado bueno conocido. No seguir parchando.
- **R5 — Contenido SEO-crítico nunca solo-cliente.** Nombre, precio, descripción y disponibilidad de producto siempre en el HTML SSR. Las islas React solo agregan interacción, no contenido indexable.

---

## 10. Deuda técnica

| # | Item | Resolver en | Detalle |
|---|------|-------------|---------|
| DT-1 | Migración SQLite → PostgreSQL | Antes de producción | Mantener Alembic compatible; evitar SQL específico de SQLite |
| DT-2 | `scripts/backup.ps1` | Setup inicial | Crear script + destino de backups |
| DT-3 | Bitácora (`bitacora.db` + helper CLI) | Setup inicial | Opcional: replicar esquema de Robustez si el proyecto lo amerita |

Cualquier `// TODO[Sx]:` en código → entrada espejo en esta tabla. Al cerrar, eliminar de tabla + referenciar commit.

---

## 11. Reglas operativas de commits y ramas

1. **Cada commit referencia su tarea por ID:** `feat(T1.4): crear modelo de producto`.
2. Commits, mensajes y ramas en español.
3. **Nunca `git add -A`** en commits acumulados grandes: formatear antes de stagear, stagear por bloque lógico.
4. Si una tarea se bloquea: marcar `🔴 BLOCKED`, pasar a la siguiente, no atascarse >1h.
5. Nunca saltar hooks (`--no-verify`) ni firmar/omitir sin pedido explícito.

---

## 12. Bitácora de sesiones

| Fecha | ID | Descripción | Archivos | Commits |
|-------|----|-------------|----------|---------|
| 2026-07-17 | SETUP-0 | Evaluación de factibilidad del stack heredado de Robustez V2.0; cierre de D1 (Astro SSR + islas React) y D2 (SQLite dev); creación de este CLAUDE.md | `CLAUDE.md` | — |
| 2026-07-17 | DOM-1 | Análisis de dominio desde `data_ref/POLA.db` + identidad del proyecto hermano; cierre de D5, D6, D7, D8, D9; ADR-001 | `CLAUDE.md`, `docs/decisions/ADR-001_dominio_e_identidad.md` | — |
