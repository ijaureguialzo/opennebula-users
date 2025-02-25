#!/usr/bin/env python3

import os
import click
import subprocess

print()
print("--------------------------------------------------")
print("--- Borrar un usuario individual de OpenNebula ---")
print("--------------------------------------------------")
print()

print("--- Datos del usuario ---------------")
usuario = click.prompt("Nombre de usuario", default="test")

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
