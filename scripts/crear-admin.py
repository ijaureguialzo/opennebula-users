#!/usr/bin/env python3

import os
import click

print()
print("--------------------------------------------")
print("--- Crear un administrador de OpenNebula ---")
print("--------------------------------------------")
print()

print("--- Datos del usuario --------------")
usuario = click.prompt("Nombre de usuario", default="test")
contrasenya = click.prompt("Contraseña", hide_input=True, confirmation_prompt=True)

print(f"\nCreando el usuario {usuario} y sus recursos asociados...\n")

print(f"Creando el usuario {usuario}...")
os.system("oneuser create " + usuario + " " + contrasenya)
os.system("oneuser chgrp " + usuario + " oneadmin")
