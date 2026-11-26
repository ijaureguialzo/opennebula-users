#!/usr/bin/env python3

import json
import os
import subprocess
import sys

import click

print()
print("----------------------------------------------------------")
print("--- Modificar los datastores de los usuarios de OpenNebula ---")
print("----------------------------------------------------------")
print()

print("--- Datos del usuario --------------")
nombre = click.prompt("Nombre de usuario", default="test")
separador = click.prompt("Separador", default="-")
inicial = click.prompt("Número de usuario inicial", default=1, type=int)
final = click.prompt("Número de usuario final", default=15, type=int)

if inicial > final:
    print("\nERROR: el número inicial no puede ser mayor que el final.")
    sys.exit(1)

USUARIOS = [nombre + separador + "{0:0>2}".format(i) for i in range(inicial, final + 1)]


def cargar_datastores():
    """Lista los datastores del sistema y devuelve una lista de {'id', 'name'}."""
    proc = subprocess.run(["onedatastore", "list", "-j", "--no-pager"],
                          capture_output=True, text=True)
    if proc.returncode != 0:
        raise RuntimeError(f"onedatastore list falló: {proc.stderr.strip() or proc.stdout.strip()}")

    texto = proc.stdout
    try:
        data = json.loads(texto)
    except json.JSONDecodeError:
        # El aviso de validación puede aparecer en stdout; intentar extraer el JSON
        inicio, fin = texto.find("{"), texto.rfind("}")
        if inicio == -1 or fin <= inicio:
            raise RuntimeError(f"No se pudo parsear la salida de onedatastore list: {texto.strip()[:300]}")
        try:
            data = json.loads(texto[inicio:fin + 1])
        except json.JSONDecodeError as e:
            raise RuntimeError(f"No se pudo parsear la salida de onedatastore list: {e}")

    pool = data.get("DATASTORE_POOL", {}) if isinstance(data, dict) else {}
    entries = pool.get("DATASTORE", []) if isinstance(pool, dict) else []
    if isinstance(entries, dict):
        entries = [entries]

    datastores = []
    for entry in entries:
        if not isinstance(entry, dict):
            continue
        did = entry.get("ID")
        if did is None:
            continue
        datastores.append({"id": str(did), "name": str(entry.get("NAME") or "")})
    return datastores


def seleccionar_datastores(datastores):
    """Interfaz de selección múltiple: flechas para moverse, ESPACIO para marcar
    y ENTER para aceptar. Devuelve la lista de índices seleccionados."""
    hint = "Flechas: moverse  |  ESPACIO: marcar/desmarcar  |  ENTER: aceptar  |  q: salir"

    if not sys.stdin.isatty():
        # Consola no interactiva: selección por números separados por comas
        print(hint)
        for i, ds in enumerate(datastores, start=1):
            print(f"  {i}) {ds['id']:>4}  {ds['name']}")
        seleccion = click.prompt("Escribe los números seleccionados (separados por comas)", default="")
        if not seleccion.strip():
            print("\nERROR: no se ha seleccionado ningún datastore.")
            sys.exit(1)
        indices = []
        for token in seleccion.split(","):
            token = token.strip()
            if not token.isdigit() or not (1 <= int(token) <= len(datastores)):
                print(f"\nERROR: '{token}' no es un número válido.")
                sys.exit(1)
            idx = int(token) - 1
            if idx not in indices:
                indices.append(idx)
        return indices

    import termios
    import tty

    fd = sys.stdin.fileno()
    old = termios.tcgetattr(fd)
    tty.setraw(fd)

    cursor = 0
    checked = [False] * len(datastores)
    hint_texto = None
    lineas_renderizadas = 0

    def render_block():
        nonlocal lineas_renderizadas
        if lineas_renderizadas:
            sys.stdout.write(f"\x1b[{lineas_renderizadas}A")
        lines = [hint]
        for i, ds in enumerate(datastores):
            mark = "[x]" if checked[i] else "[ ]"
            pointer = ">" if i == cursor else " "
            lines.append(f"  {pointer}  {mark}  {ds['id']:>4}  {ds['name']}")
        if hint_texto:
            lines.append(f"  {hint_texto}")
        for line in lines:
            sys.stdout.write("\r\x1b[K" + line + "\n")
        lineas_renderizadas = len(lines)
        sys.stdout.flush()

    def read_key():
        import select
        ch = os.read(fd, 1)
        if ch != b"\x1b":
            return ch
        seq = b""
        for _ in range(2):
            r, _, _ = select.select([fd], [], [], 0.05)
            if not r:
                break
            seq += os.read(fd, 1)
        return b"\x1b" + seq

    try:
        sys.stdout.write("\x1b[?25l")  # ocultar cursor
        render_block()
        while True:
            key = read_key()
            if key == b"\x1b[A" or key == b"\x1bOA":     # flecha arriba
                cursor = (cursor - 1) % len(datastores)
            elif key == b"\x1b[B" or key == b"\x1bOB":   # flecha abajo
                cursor = (cursor + 1) % len(datastores)
            elif key == b"q":
                sys.stdout.write("\x1b[?25h")
                print("\nSelección cancelada.")
                sys.exit(0)
            elif key == b" ":
                checked[cursor] = not checked[cursor]
            elif key == b"\r" or key == b"\n":
                seleccion = [i for i, c in enumerate(checked) if c]
                if not seleccion:
                    hint_texto = "Selecciona al menos un datastore antes de aceptar."
                    render_block()
                    continue
                sys.stdout.write("\x1b[?25h")
                print()
                return seleccion
            else:
                continue
            hint_texto = None
            render_block()
    except KeyboardInterrupt:
        sys.stdout.write("\x1b[?25h")
        print("\nSelección cancelada.")
        sys.exit(130)
    finally:
        sys.stdout.write("\x1b[?25h")
        termios.tcsetattr(fd, termios.TCSADRAIN, old)


try:
    datastores = cargar_datastores()
except RuntimeError as e:
    print(f"\nERROR: {e}")
    sys.exit(1)

if not datastores:
    print("\nERROR: no hay datastores disponibles en el sistema.")
    sys.exit(1)

print(f"--- Datastores disponibles ({len(datastores)}) ---")
print()

indices = seleccionar_datastores(datastores)
selected = [datastores[i] for i in indices]

print(f"Seleccionados {len(selected)} datastore(s):")
for ds in selected:
    print(f"  {ds['id']:>4}  {ds['name']}")
print()
print(f"Usuarios a procesar ({len(USUARIOS)}):")
for usuario in USUARIOS:
    print(f"  {usuario}")
print()

ok = 0
fallos = 0

for usuario in USUARIOS:
    print(f"--- {usuario} ---")
    for ds in selected:
        print(f"  Añadiendo datastore {ds['id']} ({ds['name']}) al datacenter {usuario}...")
        try:
            proc = subprocess.run(["onevdc", "adddatastore", usuario, "0", ds["id"]],
                                  capture_output=True, text=True)
            salida = (proc.stdout or "").strip()
            error = (proc.stderr or "").strip()
            if proc.returncode == 0:
                print("    OK" + (f" — {salida}" if salida else ""))
                ok += 1
            else:
                print(f"    ERROR: {error or salida or 'sin salida'}")
                fallos += 1
        except OSError as e:
            print(f"    ERROR: no se pudo ejecutar onevdc: {e}")
            fallos += 1

print()
print("----------------------------------------------------------")
print(f"Resumen: {ok} permisos aplicados, {fallos} error(es).")
print("----------------------------------------------------------")
