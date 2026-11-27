#!/usr/bin/env python3

import subprocess
import sys

import click

from hosts_common import listar_hosts, seleccionar_hosts

print()
print("----------------------------------------------------------")
print("--- Modificar los hosts de los usuarios de OpenNebula ---")
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

try:
    hosts = listar_hosts()
except RuntimeError as e:
    print(f"\nERROR: {e}")
    sys.exit(1)

if not hosts:
    print("\nERROR: no hay hosts disponibles en el sistema.")
    sys.exit(1)

print(f"--- Hosts disponibles ({len(hosts)}) ---")
print()

indices = seleccionar_hosts(hosts)
selected = [hosts[i] for i in indices]

print(f"Seleccionados {len(selected)} host(s):")
for h in selected:
    print(f"  {h['id']:>4}  {h['name']}")
print()
print(f"Usuarios a procesar ({len(USUARIOS)}):")
for usuario in USUARIOS:
    print(f"  {usuario}")
print()

ok = 0
fallos = 0

for usuario in USUARIOS:
    print(f"--- {usuario} ---")
    for h in selected:
        print(f"  Añadiendo host {h['id']} ({h['name']}) al datacenter {usuario}...")
        try:
            proc = subprocess.run(["onevdc", "addhost", usuario, "0", h["id"]],
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
print(f"Resumen: {ok} hosts añadidos, {fallos} error(es).")
print("----------------------------------------------------------")
