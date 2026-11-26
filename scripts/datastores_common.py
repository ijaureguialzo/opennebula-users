#!/usr/bin/env python3
"""Utilidades comunes para los scripts de datastores.

Incluye el listado de datastores del sistema, la selección interactiva
múltiple (checkboxes con flechas/ESPACIO/ENTER) y el análisis de listas de
IDs de datastores.
"""

import json
import os
import subprocess
import sys

import click

# Datastores por defecto (comportamiento heredado de los scripts existentes)
DATASTORES_DEFAULT = ["0", "1", "2"]


def listar_datastores():
    """Lista los datastores del sistema.

    Devuelve una lista de {'id': ..., 'name': ...}.
    Lanza RuntimeError si no se pueden listar.
    """
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


def parsear_datastores(valor, predeterminado=None):
    """Parsea una lista de IDs de datastores separados por comas.

    Devuelve una lista de strings con los IDs. Lanza ValueError si algún token
    no es un identificador numérico válido. Si 'valor' está vacío, devuelve la
    lista de 'predeterminado' (o [] si no se indica ninguno).
    """
    predeterminado = list(predeterminado if predeterminado is not None else [])
    valor = (valor or "").strip()
    if not valor:
        return predeterminado

    tokens = [tok.strip() for tok in valor.split(",")]
    tokens = [tok for tok in tokens if tok]
    if not tokens:
        return predeterminado
    for tok in tokens:
        if not tok.isdigit():
            raise ValueError(
                f"Datastore '{tok}' inválido (se esperan identificadores numéricos separados por comas)"
            )
    return tokens


def seleccionar_datastores(datastores, preseleccionados=None):
    """Selección múltiple interactiva de datastores.

    Consola interactiva: flechas ↑/↓ para moverse, ESPACIO para marcar/desmarcar
    y ENTER para aceptar (q o Ctrl-C para cancelar). En consolas no interactivas:
    entrada por números separados por comas. En ambos casos devuelve la lista
    de índices de 'datastores' seleccionados.

    'preseleccionados' es una lista de IDs de datastores que empiezan marcados.
    """
    preseleccionados = set(preseleccionados or [])
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
    checked = [ds["id"] in preseleccionados for ds in datastores]
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
        print("\nSelección cancelada.")
        sys.exit(130)
    finally:
        sys.stdout.write("\x1b[?25h")
        termios.tcsetattr(fd, termios.TCSADRAIN, old)
