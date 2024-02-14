#!/usr/bin/env python3

import os

import click

print()
print("----------------------------------------------------------")
print("--- Modificar las cuotas de los usuarios de OpenNebula ---")
print("----------------------------------------------------------")
print()

print("--- Datos del usuario --------------")
nombre = click.prompt("Nombre de usuario", default="test")
separador = click.prompt("Separador", default="-")
inicial = click.prompt("Número de usuario inicial", default=1)
final = click.prompt("Número de usuario final", default=15)

print("--- Cuota de recursos --------------")
cpus = click.prompt("CPUs", type=float, default=4)
ram = click.prompt("RAM (GiB)", type=float, default=12)
disco = click.prompt("Disco (GiB)", type=float, default=64)

print()

for i in range(inicial, final + 1):
    usuario = nombre + separador + "{0:0>2}".format(i)

    print(f"\nModificando las cuotas de usuario {usuario}...\n")

    f = open("temp.txt", "w")
    f.write(f'''
    VM=[
        MEMORY="{ram * 1024}",
        RUNNING_MEMORY="{ram * 1024}",
        CPU="{cpus}",
        RUNNING_CPU="{cpus}",
        SYSTEM_DISK_SIZE="{disco * 1024}"
    ]
    \n''')
    f.write(f'''
    DATASTORE=[
        ID="1",
        SIZE="{disco * 1024}"
    ]
    \n''')
    f.close()
    os.system("oneuser quota " + usuario + " temp.txt")
    os.remove("temp.txt")
