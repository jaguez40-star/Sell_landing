# Reglas y convenciones reutilizables — plantilla para nuevos proyectos

Resumen de los modos de trabajo, directivas y convenciones útiles usados en Robustez V2.0, extraídos para reutilizarse en un proyecto nuevo. Copia las secciones que apliquen al `CLAUDE.md` del nuevo proyecto y ajusta rutas/nombres.

---

## 1. Idioma y estilo de comunicación

- **Todo en español** (mensajes, respuestas, comentarios de código, commits, ramas).
- **Respuestas breves y directas.** Sin preámbulos ("Claro", "Por supuesto"). No explicar antes de hacer ni resumir después salvo que el resultado lo amerite. Si la respuesta es código, entregar el código. Máximo 2-3 líneas de explicación cuando haga falta. Tuteo informal.

---

## 2. Modos de invocación (prefijos de mensaje)

Modos que se activan cuando el usuario escribe una palabra clave al inicio del mensaje:

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

Ejecuta un script de respaldo (`scripts/backup.ps1` o equivalente). Definir: destino fijo, naming con timestamp (`backup_{YYYYMMDD_HHMM}.zip`), qué se respalda (Tier 1 irrecuperables: `.env`, BDs, allowlists; Tier 2 caros de regenerar: seeds/datasets), y un `MANIFEST.md` dentro del zip con git HEAD, branch y receta de restauración.

### `auditoria:` — Modo Auditoría de migración

Cuando se migra desde un proyecto legado, auditar **antes** de implementar. 5 pasos obligatorios:
1. Tabla(s) y campos fuente.
2. Lógica de cálculo (memoria de cálculo — fórmula exacta).
3. Lógica de filtrado (WHERE/IF del código legado).
4. Mapeo de campos legado → nuevo.
5. Verificación de paridad de datos (conteos, agregados, **duplicados en dimensiones que inflan JOINs**, filtros de negocio implícitos).

Solo auditar, no implementar.

---

## 3. Directiva de auditoría previa antes de escribir un plan

🔴 **Nunca entregar un plan "v1 improvisado" para mejorarlo en "v2" cuando el usuario detecte fallos.** El plan entregado debe ser ya un v2 auditado.

Si la tarea toca >3 archivos, introduce primitivos/hooks/utils nuevos, modifica archivos compartidos, o cambia contratos entre capas → ejecutar antes:
1. Grep de archivos similares existentes (confirmar convención).
2. Read completo del archivo a modificar (no de memoria).
3. Verificar paths de imports contra archivos vecinos.
4. Leer configs relevantes (`vite.config`, `package.json`, `tsconfig`, `.npmrc`).
5. Cruzar contra la deuda técnica.
6. Cruzar contra reglas duras.

Si la auditoría revela un bloqueante (decisión bloqueada afectada, riesgo crítico) → detener y escalar **antes** de escribir el plan.

Anti-patrones prohibidos: plan v1 "rápido" a sabiendas, asumir paths/configs de memoria, "esto probablemente funciona, lo confirma el typecheck", esperar a que el usuario pida "aplica el flujo profesional".

---

## 4. Flujo profesional de ejecución (6 pasos)

Antes de cualquier tarea no trivial:

**Mapeo → Auditoría → Diagnóstico → Propuesta → Aplicación → Verificación**

- No saltear pasos. Propuesta completa antes de aplicar.
- Si un hallazgo afecta una decisión bloqueada → detener y escalar.
- **Verificación = build verde + lint verde + tests verde + INTERACCIÓN HUMANA EN NAVEGADOR** (para features visuales). Sin lo último, el estado es "implementado pendiente de validación", no "completado".

---

## 5. Reglas duras (lecciones caras aprendidas)

Adaptables a cualquier stack; las de Plotly aplican a cualquier librería de charts (D3/Chart.js):

- **R1 — No modificar infraestructura compartida sin ADR.** `.npmrc`, lockfiles, `vite.config`, `tsconfig`, config de gestores de paquetes. Si una librería falla al instalar: diagnosticar peer deps, no aplicar atajos (`node-linker=hoisted`, mover `store-dir`). Si no se resuelve en 15 min → detener y escalar con ADR. Leer `.npmrc` antes de cualquier `install`.
- **R2 — Charts: el `data` memoizado nunca depende de selección/hover.** Acoplar UI state interactivo (`selectedKey`, `hoveredKey`) al `data` del chart re-anima y rompe la interacción. Deps del `useMemo` = solo datos crudos. `onHover` nunca muta estado global.
- **R3 — "Build verde" ≠ "feature verificada".** El linter/typecheck/tests no detectan animaciones rotas, layout colapsado, eventos mal cableados, race conditions en `useEffect`. El único que marca ✅ una feature visual es el usuario tras probarla en el navegador.
- **P4 — Si un fix reactivo se acumula >2 iteraciones sin resolver el bug, detener y revertir** al último estado bueno conocido. No seguir parchando.

---

## 6. Bitácora de cambios (`bitacora.db`)

BD SQLite no versionada que registra cambios diarios con narrativa técnica. Tablas: `semanas`, `cambios_diarios`, `archivos_afectados`, `detalles_tecnicos`, `artefactos`.

**Regla de oro:** NUNCA UPDATE/DELETE. Solo INSERT. Si hay un error pasado, agregar una entrada correctiva nueva.

Helper CLI (`log_bitacora.py`):
```bash
uv run python scripts/log_bitacora.py add-day --semana N --fecha FECHA --dia "Lunes" --resumen "..." --tareas ID --personas J C
uv run python scripts/log_bitacora.py list-changes --semana N
```

Complementarla con un changelog en `CLAUDE.md` (§ bitácora de sesiones): tabla `Fecha | ID | Descripción | Archivos | Commits`.

---

## 7. Convenciones de código

### Naming entre capas (Interceptores)

| Lugar | Convención | Ejemplo |
|-------|-----------|---------|
| Backend (Python) | `snake_case` | `ebitda_kusd` |
| Frontend (TS) | `camelCase` | `ebitdaKusd` |
| Contrato JSON heredado | literal (tildes, espacios) | `"EBITDA (KUSD)"` |

- **Interceptor 1** — Pydantic `alias` en `schemas.py` traduce `snake_case ↔ JSON heredado`.
- **Interceptor 2** — mappers `to<Entity>UI(api)` (funciones puras) traducen `JSON heredado ↔ camelCase`.

### Backend: Repository–Service–Route

`repositories.py` (único punto de SQL) → `services.py` (lógica) → `api.py` (endpoints) · `models.py` (dominio) · `schemas.py` (Pydantic).

### Frontend: feature autocontenida

`pages/` · `components/` · `hooks/` (server state) · `mappers/` (Interceptor 2) · `services/` (cliente HTTP tipado). **Una feature solo importa de `shared/`/`core/`, nunca de otra feature** (vertical slicing).

---

## 8. Gestión de decisiones y deuda técnica

- **Decisiones bloqueadas (D1–DN):** tabla de decisiones cerradas. Nunca cambiarlas sin confirmación explícita del usuario.
- **ADRs ligeros** en `docs/decisions/` para decisiones técnicas no triviales.
- **Deuda técnica (DT-N):** tabla con `# | Item | Resolver en | Detalle`. Cualquier `// TODO[Sx]:` en código → entrada espejo en la tabla. Al cerrar, eliminar de tabla + referenciar commit.

---

## 9. Reglas operativas de commits y ramas

1. **Cada commit referencia su tarea por ID:** `feat(W1.4): crear BD con DDL v0.2`.
2. Commits, mensajes y ramas en español.
3. **Nunca `git add -A`** en commits acumulados grandes: formatear antes de stagear, stagear por bloque lógico.
4. Si una tarea se bloquea: marcar `🔴 BLOCKED`, pasar a la siguiente, no atascarse >1h.
5. Nunca saltar hooks (`--no-verify`) ni firmar/omitir sin pedido explícito.

---

## 10. Memoria de proyecto (persistente entre sesiones)

Archivos de memoria (`memory/*.md`) con frontmatter (`name`, `description`, `type: user|feedback|project|reference`) + índice en `MEMORY.md` (una línea por memoria). Guardar lo **no derivable** del código/git: preferencias del usuario, guías de trabajo (con el porqué), objetivos y restricciones del proyecto. No duplicar lo que ya registran el código, los commits o el CLAUDE.md.

---

## 11. Checklist para arrancar un proyecto nuevo con estas reglas

- [ ] Crear `CLAUDE.md` con: idioma, estilo, modos (`plan:`/`backup:`/`auditoria:`), flujo 6 pasos, decisiones bloqueadas, deuda técnica, convenciones de código.
- [ ] Definir estructura (monorepo / vertical slicing / feature-based).
- [ ] Configurar `scripts/backup.ps1` + destino y manifest.
- [ ] Inicializar `bitacora.db` + helper CLI.
- [ ] Crear `Planes/`, `docs/decisions/`, `memory/`.
- [ ] Configurar lint/format/typecheck + pre-commit hook (husky o equivalente).
- [ ] Documentar el naming entre capas (Interceptores 1 y 2) si hay back + front.
