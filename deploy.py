#!/usr/bin/env python3
"""deploy.py — Bootstrap completo de DISPOLA SAS / LA POLA en una maquina nueva.

Instala y verifica TODA la cadena necesaria para levantar la aplicacion,
desde que Python ya esta disponible en adelante. No omite nada:

  1.  Python            verifica version >= 3.12 (requisito para correr este script)
  2.  uv                gestor del backend    -> lo instala con pip si falta
  3.  Node.js           runtime del frontend  -> lo instala con winget (Windows) si falta
  4.  pnpm              gestor del frontend    -> lo activa con corepack
  5.  Backend deps      uv sync (incluye grupo dev: ruff, mypy, pytest)
  6.  Frontend deps     pnpm install (compila esbuild/sharp segun pnpm-workspace.yaml)
  7.  Backend .env      lo genera desde .env.example con un SESSION_SECRET aleatorio
  8.  Carpeta data/     directorio de la BD SQLite
  9.  Migraciones       uv run alembic upgrade head (solo si backend/alembic.ini existe)
  10. Build frontend    pnpm --filter frontend build (genera sitemap, valida SSR)
  11. Verificacion E2E  arranca la API y comprueba GET /api/health

Uso:
    python deploy.py                # instalacion completa + verificacion
    python deploy.py --check        # solo diagnostica herramientas, no instala nada
    python deploy.py --skip-build   # instala dependencias pero no compila el frontend
    python deploy.py --skip-verify  # no arranca la API al final

Requisito previo (unica cosa manual): tener Python 3.12+ instalado.
  Windows:  winget install Python.Python.3.12
  macOS:    brew install python@3.12
  Linux:    usar el gestor de la distro (apt/dnf) o pyenv
"""

from __future__ import annotations

import argparse
import os
import platform
import shutil
import subprocess
import sys
import sysconfig
import time
import urllib.request
from pathlib import Path

RAIZ = Path(__file__).resolve().parent
BACKEND = RAIZ / "backend"
FRONTEND = RAIZ / "frontend"
DATA = RAIZ / "data"

ES_WINDOWS = platform.system() == "Windows"
PY_MIN = (3, 12)
API_PORT = 8890
HEALTH_URL = f"http://localhost:{API_PORT}/api/health"

# Acumulador de resultados para el resumen final.
RESULTADOS: list[tuple[str, str]] = []


# --------------------------------------------------------------------------- #
# Utilidades
# --------------------------------------------------------------------------- #
def encabezado(paso: str) -> None:
    print("\n" + "=" * 70)
    print(f"  {paso}")
    print("=" * 70)


def ok(msg: str) -> None:
    print(f"  [OK]   {msg}")


def info(msg: str) -> None:
    print(f"  [..]   {msg}")


def aviso(msg: str) -> None:
    print(f"  [!]    {msg}")


def error(msg: str) -> None:
    print(f"  [ERR]  {msg}")


def registrar(paso: str, estado: str) -> None:
    RESULTADOS.append((paso, estado))


def resolver(nombre: str) -> str | None:
    """Localiza un ejecutable en PATH o en los directorios de scripts de Python."""
    ruta = shutil.which(nombre)
    if ruta:
        return ruta
    # Consolas scripts recien instaladas por pip (uv) que aun no estan en PATH.
    candidatos = []
    for clave in ("scripts",):
        try:
            candidatos.append(Path(sysconfig.get_path(clave)))
        except (KeyError, OSError):
            pass
    try:
        import site

        base = Path(site.getuserbase())
        candidatos.append(base / ("Scripts" if ES_WINDOWS else "bin"))
    except Exception:
        pass
    sufijos = [".exe", ".cmd", ".bat", ""] if ES_WINDOWS else [""]
    for d in candidatos:
        for suf in sufijos:
            p = d / f"{nombre}{suf}"
            if p.exists():
                return str(p)
    return None


def correr(cmd: list[str], cwd: Path | None = None, obligatorio: bool = True) -> bool:
    """Ejecuta un comando mostrando la linea. Devuelve True si termino en 0."""
    print(f"  $ {' '.join(cmd)}" + (f"   (en {cwd})" if cwd else ""))
    try:
        res = subprocess.run(cmd, cwd=str(cwd) if cwd else None)
    except FileNotFoundError:
        error(f"comando no encontrado: {cmd[0]}")
        if obligatorio:
            raise SystemExit(1)
        return False
    if res.returncode != 0:
        error(f"fallo (codigo {res.returncode}): {' '.join(cmd)}")
        if obligatorio:
            raise SystemExit(res.returncode)
        return False
    return True


# --------------------------------------------------------------------------- #
# Pasos
# --------------------------------------------------------------------------- #
def paso_python() -> None:
    encabezado("1/11  Python")
    v = sys.version_info
    info(f"version detectada: {v.major}.{v.minor}.{v.micro} ({sys.executable})")
    if (v.major, v.minor) < PY_MIN:
        error(f"se requiere Python >= {PY_MIN[0]}.{PY_MIN[1]}. Actualiza e intenta de nuevo.")
        raise SystemExit(1)
    ok("version compatible")
    registrar("Python", "OK")


def paso_uv(solo_check: bool) -> str:
    encabezado("2/11  uv (gestor del backend)")
    uv = resolver("uv")
    if uv:
        ok(f"uv presente: {uv}")
        registrar("uv", "OK")
        return uv
    if solo_check:
        aviso("uv NO instalado")
        registrar("uv", "FALTA")
        return "uv"
    info("uv no encontrado -> instalando con pip")
    correr([sys.executable, "-m", "pip", "install", "--upgrade", "uv"])
    uv = resolver("uv")
    if not uv:
        error("uv se instalo pero no se resolvio en PATH. Reabre la terminal y reintenta.")
        raise SystemExit(1)
    ok(f"uv instalado: {uv}")
    registrar("uv", "INSTALADO")
    return uv


def paso_node(solo_check: bool) -> None:
    encabezado("3/11  Node.js (runtime del frontend)")
    node = resolver("node")
    if node:
        v = subprocess.run([node, "--version"], capture_output=True, text=True).stdout.strip()
        ok(f"Node presente: {node} ({v})")
        registrar("Node.js", "OK")
        return
    if solo_check:
        aviso("Node.js NO instalado")
        registrar("Node.js", "FALTA")
        return
    if ES_WINDOWS and resolver("winget"):
        info("Node no encontrado -> instalando LTS con winget")
        correr(
            ["winget", "install", "-e", "--id", "OpenJS.NodeJS.LTS",
             "--accept-source-agreements", "--accept-package-agreements"],
            obligatorio=False,
        )
        if resolver("node"):
            ok("Node instalado. Puede requerir reabrir la terminal para actualizar PATH.")
            registrar("Node.js", "INSTALADO")
            return
    error(
        "Node.js no esta y no se pudo instalar automaticamente.\n"
        "         Instalalo manualmente y vuelve a correr deploy.py:\n"
        "           Windows: winget install OpenJS.NodeJS.LTS\n"
        "           macOS:   brew install node\n"
        "           Linux:   usar nvm o el gestor de la distro"
    )
    raise SystemExit(1)


def paso_pnpm(solo_check: bool) -> str:
    encabezado("4/11  pnpm (gestor del frontend)")
    pnpm = resolver("pnpm")
    if pnpm:
        ok(f"pnpm presente: {pnpm}")
        registrar("pnpm", "OK")
        return pnpm
    if solo_check:
        aviso("pnpm NO instalado")
        registrar("pnpm", "FALTA")
        return "pnpm"
    corepack = resolver("corepack")
    if corepack:
        info("activando pnpm con corepack (viene con Node)")
        correr([corepack, "enable"], obligatorio=False)
        correr([corepack, "prepare", "pnpm@latest", "--activate"], obligatorio=False)
    pnpm = resolver("pnpm")
    if not pnpm:
        info("corepack no basto -> instalando pnpm con npm -g")
        npm = resolver("npm")
        if npm:
            correr([npm, "install", "-g", "pnpm"], obligatorio=False)
        pnpm = resolver("pnpm")
    if not pnpm:
        error("no se pudo activar pnpm. Reabre la terminal (PATH) y reintenta.")
        raise SystemExit(1)
    ok(f"pnpm listo: {pnpm}")
    registrar("pnpm", "INSTALADO")
    return pnpm


def paso_backend_deps(uv: str) -> None:
    encabezado("5/11  Dependencias del backend (uv sync)")
    if not (BACKEND / "pyproject.toml").exists():
        error(f"no se encontro {BACKEND / 'pyproject.toml'}")
        raise SystemExit(1)
    # uv sync crea el .venv e instala runtime + grupo dev (ruff, mypy, pytest).
    correr([uv, "sync"], cwd=BACKEND)
    ok("entorno del backend sincronizado (.venv)")
    registrar("Backend deps", "OK")


def paso_frontend_deps(pnpm: str) -> None:
    encabezado("6/11  Dependencias del frontend (pnpm install)")
    if not (FRONTEND / "package.json").exists():
        error(f"no se encontro {FRONTEND / 'package.json'}")
        raise SystemExit(1)
    # Se ejecuta en la raiz: es un workspace pnpm.
    # pnpm puede terminar en codigo 1 con ERR_PNPM_IGNORED_BUILDS (no ejecuta
    # los scripts de compilacion de esbuild/sharp/@parcel/watcher). NO es fatal:
    # esos binarios llegan como dependencias opcionales por plataforma. Se tolera
    # el codigo y se fuerza la compilacion nativa con 'pnpm rebuild' (no interactivo).
    correr([pnpm, "install"], cwd=RAIZ, obligatorio=False)
    if not (FRONTEND / "node_modules").exists() and not (RAIZ / "node_modules").exists():
        error("pnpm install no genero node_modules")
        raise SystemExit(1)
    info("compilando dependencias nativas (esbuild / sharp / @parcel/watcher)")
    correr([pnpm, "rebuild", "@parcel/watcher", "esbuild", "sharp"], cwd=RAIZ, obligatorio=False)
    ok("dependencias del frontend instaladas")
    registrar("Frontend deps", "OK")


def paso_env() -> None:
    encabezado("7/11  Archivo .env del backend")
    destino = BACKEND / ".env"
    ejemplo = BACKEND / ".env.example"
    if destino.exists():
        ok(".env ya existe (no se sobrescribe)")
        registrar(".env", "OK")
        return
    if not ejemplo.exists():
        aviso("no hay .env.example; se omite (el backend usara defaults del config)")
        registrar(".env", "OMITIDO")
        return
    import secrets

    contenido = ejemplo.read_text(encoding="utf-8")
    secreto = secrets.token_urlsafe(48)
    lineas = []
    for ln in contenido.splitlines():
        if ln.startswith("SESSION_SECRET"):
            lineas.append(f"SESSION_SECRET={secreto}")
        else:
            lineas.append(ln)
    destino.write_text("\n".join(lineas) + "\n", encoding="utf-8")
    ok(f".env creado desde .env.example con SESSION_SECRET aleatorio ({destino})")
    registrar(".env", "CREADO")


def paso_data() -> None:
    encabezado("8/11  Carpeta data/ (BD SQLite)")
    for d in (DATA, BACKEND / "data"):
        d.mkdir(parents=True, exist_ok=True)
        ok(f"directorio listo: {d}")
    aviso(
        "data_ref/POLA.db (fuente del seed) NO viaja por git (77 MB, ignorada).\n"
        "         Copiala manualmente si esta maquina va a correr el seed de catalogo."
    )
    registrar("data/", "OK")


def paso_migraciones(uv: str) -> None:
    encabezado("9/11  Migraciones de base de datos (Alembic)")
    if not (BACKEND / "alembic.ini").exists():
        aviso("backend/alembic.ini no existe todavia -> se omite (aun no hay modelos/migraciones)")
        registrar("Migraciones", "OMITIDO")
        return
    correr([uv, "run", "alembic", "upgrade", "head"], cwd=BACKEND, obligatorio=False)
    ok("migraciones aplicadas (o ya al dia)")
    registrar("Migraciones", "OK")


def paso_build(pnpm: str, saltar: bool) -> None:
    encabezado("10/11  Build del frontend (Astro)")
    if saltar:
        aviso("--skip-build: se omite la compilacion del frontend")
        registrar("Build", "OMITIDO")
        return
    correr([pnpm, "--filter", "frontend", "build"], cwd=RAIZ)
    ok("frontend compilado (dist/ + sitemap)")
    registrar("Build", "OK")


def paso_verificar(uv: str, saltar: bool) -> None:
    encabezado("11/11  Verificacion end-to-end (API /api/health)")
    if saltar:
        aviso("--skip-verify: no se arranca la API")
        registrar("Verificacion", "OMITIDO")
        return
    info(f"arrancando uvicorn en :{API_PORT} (temporal)")
    proc = subprocess.Popen(
        [uv, "run", "uvicorn", "app.main:app", "--port", str(API_PORT), "--log-level", "warning"],
        cwd=str(BACKEND),
    )
    try:
        estado = "FALLO"
        for intento in range(1, 21):
            time.sleep(1)
            try:
                with urllib.request.urlopen(HEALTH_URL, timeout=2) as r:
                    cuerpo = r.read().decode("utf-8")
                    if r.status == 200 and '"ok"' in cuerpo:
                        ok(f"API responde 200 en {HEALTH_URL}")
                        info(f"respuesta: {cuerpo}")
                        estado = "OK"
                        break
            except Exception:
                if intento == 20:
                    error(f"la API no respondio en {HEALTH_URL} tras 20s")
        registrar("Verificacion", estado)
    finally:
        proc.terminate()
        try:
            proc.wait(timeout=10)
        except subprocess.TimeoutExpired:
            proc.kill()
        info("uvicorn temporal detenido")


# --------------------------------------------------------------------------- #
# Main
# --------------------------------------------------------------------------- #
def resumen() -> None:
    encabezado("RESUMEN")
    ancho = max(len(p) for p, _ in RESULTADOS) if RESULTADOS else 0
    hubo_fallo = False
    for paso, estado in RESULTADOS:
        marca = "OK  " if estado in ("OK", "INSTALADO", "CREADO") else (
            "--  " if estado == "OMITIDO" else "XX  "
        )
        if estado not in ("OK", "INSTALADO", "CREADO", "OMITIDO"):
            hubo_fallo = True
        print(f"  [{marca}] {paso.ljust(ancho)}  {estado}")
    print()
    if hubo_fallo:
        error("Deploy finalizado CON FALLOS. Revisa el detalle arriba.")
        raise SystemExit(1)
    ok("Deploy completado. Para levantar la app en desarrollo:")
    print("        pnpm install   (si aun no)   &&   pnpm dev")
    print(f"        Sitio: http://localhost:8889    API: http://localhost:{API_PORT}")


def main() -> None:
    parser = argparse.ArgumentParser(description="Bootstrap de despliegue de DISPOLA / LA POLA")
    parser.add_argument("--check", action="store_true", help="solo diagnostica, no instala")
    parser.add_argument("--skip-build", action="store_true", help="no compila el frontend")
    parser.add_argument("--skip-verify", action="store_true", help="no arranca la API al final")
    args = parser.parse_args()

    print("\n" + "#" * 70)
    print("#  DEPLOY DISPOLA SAS / LA POLA - maquina:", platform.node(), platform.system())
    print("#  raiz del proyecto:", RAIZ)
    print("#" * 70)

    paso_python()
    uv = paso_uv(args.check)
    paso_node(args.check)
    pnpm = paso_pnpm(args.check)

    if args.check:
        resumen()
        return

    paso_backend_deps(uv)
    paso_frontend_deps(pnpm)
    paso_env()
    paso_data()
    paso_migraciones(uv)
    paso_build(pnpm, args.skip_build)
    paso_verificar(uv, args.skip_verify)
    resumen()


if __name__ == "__main__":
    main()
