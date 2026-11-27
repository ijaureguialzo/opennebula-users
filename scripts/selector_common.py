#!/usr/bin/env python3
"""Selección múltiple interactiva de recursos (compartido).

Implementa la selección de recursos en múltiples pasos (checkboxes con
flechas/ESPACIO/ENTER en consolas interactivas, o entrada por números
separados por comas en consolas no interactivas). Es genérico: el llamador
decide qué recursos lista y con qué nombre los presenta.
"""

import os
import sys

import click


def seleccionar_multiple(items, nombre, preseleccionados=None):
    """Selección múltiple interactiva de un conjunto de recursos.

    Consola interactiva: flechas ↑/↓ para moverse, ESPACIO para marcar/
    desmarcar y ENTER para aceptar (q o Ctrl-C para cancelar). En consolas
    no interactivas: entrada por números separados por comas. En ambos casos
    devuelve la lista de índices de 'items' seleccionados.

    'items' es una lista de diccionarios con 'id' y 'name'. 'nombre' es el
    nombre singular del recurso en español (p. ej. 'datastore', 'host').
    'preseleccionados' es una lista de IDs que empiezan marcados.
    """
    preseleccionados = set(preseleccionados or [])
    hint = "Flechas: moverse  |  ESPACIO: marcar/desmarcar  |  ENTER: aceptar  |  q: salir"

    if not sys.stdin.isatty():
        # Consola no interactiva: selección por números separados por comas
        print(hint)
        for i, item in enumerate(items, start=1):
            print(f"  {i}) {item['id']:>4}  {item['name']}")
        seleccion = click.prompt("Escribe los números seleccionados (separados por comas)", default="")
        if not seleccion.strip():
            print(f"\nERROR: no se ha seleccionado ningún {nombre}.")
            sys.exit(1)
        indices = []
        for token in seleccion.split(","):
            token = token.strip()
            if not token.isdigit() or not (1 <= int(token) <= len(items)):
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
    checked = [item["id"] in preseleccionados for item in items]
    hint_texto = None
    lineas_renderizadas = 0

    def render_block():
        nonlocal lineas_renderizadas
        if lineas_renderizadas:
            sys.stdout.write(f"\x1b[{lineas_renderizadas}A")
        lines = [hint]
        for i, item in enumerate(items):
            mark = "[x]" if checked[i] else "[ ]"
            pointer = ">" if i == cursor else " "
            lines.append(f"  {pointer}  {mark}  {item['id']:>4}  {item['name']}")
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
                cursor = (cursor - 1) % len(items)
            elif key == b"\x1b[B" or key == b"\x1bOB":   # flecha abajo
                cursor = (cursor + 1) % len(items)
            elif key == b"q":
                print("\nSelección cancelada.")
                sys.exit(0)
            elif key == b" ":
                checked[cursor] = not checked[cursor]
            elif key == b"\r" or key == b"\n":
                seleccion = [i for i, c in enumerate(checked) if c]
                if not seleccion:
                    hint_texto = f"Selecciona al menos un {nombre} antes de aceptar."
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
