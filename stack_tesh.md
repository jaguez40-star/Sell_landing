# Stack Tecnológico — Robustez V2.0

Descripción de la tecnología usada en el backend y el frontend de la aplicación.

---

## Backend (`robustez_v02_backend/`)

| Componente | Versión | Uso |
|------------|---------|-----|
| Python | 3.12+ | Lenguaje base |
| FastAPI | latest | Framework web + generación automática de OpenAPI |
| SQLAlchemy | 2.0+ | ORM |
| Alembic | latest | Migraciones de base de datos |
| Pydantic | 2.x | Validación + Interceptor 1 (alias snake_case ↔ JSON heredado) |
| ldap3 | 2.9+ | Autenticación contra AD `red.ecopetrol.com.co` |
| structlog | latest | Logs en formato JSON UTC |
| itsdangerous | 2.x | Cookie firmada de sesión |
| uv | latest | Gestor de paquetes / entorno |
| Ruff + Black + mypy | latest | Lint + formateo + chequeo de tipos |
| pytest | latest | Tests unitarios e integración |

### Bases de datos

| BD | Tipo | Rol |
|----|------|-----|
| `robustez_v02_auth.db` | SQLite | Auth + auditoría (8 tablas, RBAC) |
| `bitacora.db` | SQLite | Bitácora de cambios diarios |
| `docs/MM/matriz_multivariable.db` | SQLite | Matriz Multivariable (tablas espejo del Excel fuente) |
| PostgreSQL `ops.*` (schema v11) | PostgreSQL 18.4 | BD operacional (esquema estrella: 2 dimensiones + 4 hechos) |

### Patrón de arquitectura backend

- **Vertical slicing por features** — cada feature es autocontenida (`api.py`, `services.py`, `repositories.py`, `models.py`, `schemas.py`).
- **Repository–Service–Route:** `repositories.py` (único punto de SQL) → `services.py` (lógica de negocio) → `api.py` (endpoints FastAPI).
- **Interceptor 1** — Pydantic `alias` en `schemas.py` traduce `snake_case ↔ "EBITDA (KUSD)"`.
- **Middleware stack:** `correlation_id` + `auth` + `request_logger`.
- Una feature solo importa de `shared/` o `core/` — **nunca** de otra feature.

---

## Frontend (`robustez_v02_frontend/`)

| Componente | Versión | Uso |
|------------|---------|-----|
| React | 19 | Librería de UI |
| TypeScript | 5.x | Tipado estricto |
| Vite | latest | Bundler + dev server |
| TanStack Query | v5 | Estado de servidor (fetching, caché) |
| Zustand | 5 | Estado global de cliente |
| react-hook-form | 7.74 | Formularios |
| zod | 4.3 | Validación de schemas |
| react-router-dom | latest | Routing SPA |
| Sass | latest | Estilos (Sass Modules) |
| Lucide React | latest | Iconografía tree-shakeable |
| Plotly.js | latest | Gráficos (activado en F7) |
| openapi-typescript + openapi-fetch | latest | Tipos auto + cliente HTTP tipado |
| Vitest + RTL | latest | Tests unitarios |
| Playwright | latest | Tests E2E |
| pnpm | latest | Gestor de paquetes + workspaces |

### Patrón de arquitectura frontend

- **Feature-based:** `pages/` (pantallas), `components/` (UI del dominio), `hooks/` (TanStack Query), `mappers/` (Interceptor 2), `services/` (cliente HTTP tipado).
- **Interceptor 2** — funciones puras `to<Entity>UI(api)` en `mappers/` traducen `"EBITDA (KUSD)" ↔ camelCase`.
- **Patrón draft/applied** en los stores de filtros (Zustand).
- **NO** Bootstrap, **NO** date-fns en los paneles de filtro.

### Identidad visual (Ecopetrol)

- Verde primario `#004236` · Verde brillante `#6CD300` · Amarillo `#F7DB17` · Naranja `#FF5F00`.
- Tipografía Inter con `tabular-nums` en KPIs.
- Espaciado base 4px · Elevación 3 niveles · Transiciones ≤ 300ms con `cubic-bezier(0.4, 0, 0.2, 1)`.

---

## Monorepo y orquestación

- **pnpm workspaces** — un `package.json` raíz orquesta back + front con `concurrently`, `husky` y `lint-staged`.
- **Puertos:** backend `:6024` (uvicorn) · frontend `:6023` (Vite), unificados en dev local y servidor (`10.100.26.139`).
- **Convención de naming entre capas:** Python `snake_case` (`ebitda_kusd`) ↔ TypeScript `camelCase` (`ebitdaKusd`) ↔ contrato JSON heredado V01 (`"EBITDA (KUSD)"`).
