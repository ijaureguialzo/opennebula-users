#!/usr/bin/env python3
"""Utilidades comunes para los scripts de datastores.

Incluye el listado de datastores del sistema, la selección interactiva
múltiple (checkboxes con flechas/ESPACIO/ENTER) y el análisis de listas de
IDs de datastores.
"""

import json
import subprocess

from selector_common import seleccionar_multiple

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
    return seleccionar_multiple(datastores, "datastore", preseleccionados=preseleccionados)
