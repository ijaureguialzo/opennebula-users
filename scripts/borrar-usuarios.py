#!/usr/bin/env python3

import os
import click
import subprocess

print()
print("-------------------------------------")
print("--- Borrar usuarios de OpenNebula ---")
print("-------------------------------------")
print()

print("--- Datos del usuario ---------------")
nombre = click.prompt("Nombre de usuario", default="test")
separador = click.prompt("Separador", default="-")
inicial = click.prompt("Número de usuario inicial", default=1)
final = click.prompt("Número de usuario final", default=15)
grupo = click.prompt("Grupo de usuarios", default=nombre)

for i in range(inicial, final + 1):
    usuario = nombre + separador + "{0:0>2}".format(i)

    print(f"\nBorrando el usuario {usuario} y sus recursos asociados...\n")

    vm_ids = subprocess.run(['onevm', 'list', usuario, '-l', 'id', '--no-header'],
                            capture_output=True, text=True).stdout.split()
    if len(vm_ids) > 0:
        print("Borrando las máquinas virtuales...")
        os.system("onevm recover --delete " + ','.join(vm_ids))

    template_ids = subprocess.run(['onetemplate', 'list', usuario, '-l', 'id', '--no-header'],
                                  capture_output=True, text=True).stdout.split()
    if len(template_ids) > 0:
        print("Borrando las plantillas...")
        os.system("onetemplate delete --recursive " + ','.join(template_ids))

    image_ids = subprocess.run(['oneimage', 'list', usuario, '-l', 'id', '--no-header'],
                               capture_output=True, text=True).stdout.split()
    if len(image_ids) > 0:
        print("Borrando las imágenes...")
        os.system("oneimage delete " + ','.join(image_ids))

    print("Borrando el datacenter...")
    os.system("onevdc delete " + usuario)

    print("Borrando el usuario...")
    os.system("oneuser delete " + usuario)

    print("Borrando el grupo...")
    os.system("onegroup delete " + usuario)

    print("Borrando la red...")
    os.system("onevnet delete " + usuario)

print(f"\nBorrando el grupo {grupo}...")
os.system("onegroup delete " + grupo)
