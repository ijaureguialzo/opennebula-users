#!/usr/bin/env python3

import os
import click

print()
print("-------------------------------------")
print("--- Borrar usuarios de OpenNebula ---")
print("-------------------------------------")
print()

print("--- Datos del usuario ---------------")
nombre = click.prompt("Nombre de usuario", default="ciber")
separador = click.prompt("Separador", default="-")
inicial = click.prompt("Número de usuario inicial", default=1)
final = click.prompt("Número de usuario final", default=15)

print()

for i in range(inicial, final + 1):
    usuario = nombre + separador + "{0:0>2}".format(i)

    print(f"Borrando el usuario {usuario} y sus recursos asociados...")

    os.system("onevdc delete " + usuario)
    os.system("oneuser delete " + usuario)
    os.system("onegroup delete " + usuario)
    os.system("onevnet delete " + usuario)
