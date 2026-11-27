#!/usr/bin/env python3
"""Utilidades comunes para los scripts de hosts.

Incluye el listado de hosts del sistema y la selección interactiva
múltiple. El comando `onehost` está roto en la imagen oficial de
opennebula-tools (falta el módulo HostSyncManager, así que falla al cargar),
por lo que el listado se hace directamente vía XML-RPC llamando a
'one.hostpool.info' y parseando el XML de la respuesta (misma fuente de
verdad que los comandos one*).
"""

import os
import ssl
import xml.etree.ElementTree as ET
import xmlrpc.client

from selector_common import seleccionar_multiple


def _find_text(element, tag):
    """Devuelve el texto del primer hijo de 'element' con ese nombre de etiqueta."""
    for child in element:
        if child.tag.rsplit("}", 1)[-1] == tag:
            return (child.text or "").strip()
    return ""


def listar_hosts():
    """Lista los hosts del sistema.

    Devuelve una lista de {'id': ..., 'name': ...}.
    Lanza RuntimeError si no se pueden listar.
    """
    endpoint = (os.environ.get("ONE_XMLRPC") or "").strip()
    if not endpoint:
        raise RuntimeError("ONE_XMLRPC no está definida en el entorno.")

    auth_file = (os.environ.get("ONE_AUTH") or "").strip()
    if not auth_file or not os.path.isfile(auth_file):
        raise RuntimeError("ONE_AUTH no apunta a un fichero válido.")

    with open(auth_file, "r", encoding="utf-8") as f:
        token = f.read().strip()
    if not token:
        raise RuntimeError(f"El fichero de credenciales '{auth_file}' está vacío.")

    # Igual que los comandos one* con ONE_DISABLE_SSL_VERIFY: el certificado
    # del endpoint puede no ser de una CA de confianza.
    if os.environ.get("ONE_DISABLE_SSL_VERIFY"):
        ssl._create_default_https_context = ssl._create_unverified_context

    try:
        server = xmlrpc.client.ServerProxy(endpoint)
        resp = server.one.hostpool.info(token)
    except xmlrpc.client.Fault as e:
        raise RuntimeError(f"one.hostpool.info falló: {e.faultString}")
    except OSError as e:
        raise RuntimeError(f"No se pudo conectar al endpoint {endpoint}: {e}")

    xml_body = resp
    if isinstance(resp, (list, tuple)):
        if not resp or not resp[0]:
            detalle = resp[1] if len(resp) > 1 and resp[1] else "sin detalle"
            raise RuntimeError(f"one.hostpool.info falló: {detalle}")
        xml_body = resp[1] if len(resp) > 1 else None

    if not isinstance(xml_body, str) or not xml_body.strip():
        raise RuntimeError("La respuesta de one.hostpool.info no contiene hosts.")

    try:
        root = ET.fromstring(xml_body)
    except ET.ParseError as e:
        raise RuntimeError(f"No se pudo parsear la respuesta de one.hostpool.info: {e}")

    hosts = []
    for element in root.iter():
        if element.tag.rsplit("}", 1)[-1] != "HOST":
            continue
        host_id = _find_text(element, "ID")
        name = _find_text(element, "NAME")
        if host_id and name:
            hosts.append({"id": host_id, "name": name})
    return hosts


def seleccionar_hosts(hosts, preseleccionados=None):
    """Selección múltiple interactiva de hosts.

    Consola interactiva: flechas ↑/↓ para moverse, ESPACIO para marcar/desmarcar
    y ENTER para aceptar (q o Ctrl-C para cancelar). En consolas no interactivas:
    entrada por números separados por comas. En ambos casos devuelve la lista
    de índices de 'hosts' seleccionados.

    'preseleccionados' es una lista de IDs de hosts que empiezan marcados.
    """
    return seleccionar_multiple(hosts, "host", preseleccionados=preseleccionados)
